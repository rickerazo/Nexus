"""Codebook -> DataSource. Two passes, then reconcile.

Pass 1 (deterministic): regex heuristics for 'NAME  Label' lines common to PRAMS/NVSS codebooks.
Pass 2 (LLM): structured extraction per chunk into `Variable[]`.
Reconcile: a variable is kept if pass 1 found it, or if pass 2 proposed it AND its exact name
occurs in the text of the page it cites. Nothing the model invents can enter a DataSource.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from mmf.ingest.chunk import chunk_document
from mmf.ingest.pdf import Document
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource, Variable, VariableType
from mmf.schemas.run import LLMCallRecord

log = logging.getLogger(__name__)

# Bump whenever deterministic extraction changes; it is part of the ingest cache key so fixes re-ingest.
PARSER_VERSION = "4"

# Layout 1 (NVSS-style guides): "MAGER9   Mother's age recode 9" on one line.
_VAR_LINE = re.compile(r"^\s*(?P<name>[A-Z][A-Z0-9_]{1,23})\s*[:\-\u2013]?\s{2,}(?P<label>[A-Za-z][^\n]{3,120})$")
# Layout 2 (PRAMS codebooks): one table cell per line: Q#, VARIABLE, label, format, codes...
# Q# cells: 12, 4d, II3, 56i, plus state/version suffixes seen in PRAMS P7/P8 (4d_L11a, 14k_WA, 18d_SAOa,
# 23j_CNMI, 4k_NYYC, 19mMN, 1_SSO).
_QNUM = re.compile(r"^[IVX]{0,4}\d{1,3}[a-z]?\d?(?:_?[A-Z]{2,4}[a-z0-9]{0,2}|_L\d{1,3}[a-z]?)?$")
_FORMAT = re.compile(r"^[A-Z][A-Z0-9_.]{1,15}$")
# Layout 3 (NVSS public-use file guides): Position, Len, File flags, NAME, Description, then
# value/label pairs on alternating lines.
_POSITION = re.compile(r"^\d{1,4}(-\d{1,4})?$")
_LEN = re.compile(r"^\d{1,3}$")
_FILEFLAG = re.compile(r"^[A-Z](,[A-Z])*$")
_VALUE = re.compile(r"^[0-9A-Z]{1,4}(-[0-9]{1,4})?$")
_BARE_NAME = re.compile(r"^[A-Z][A-Z0-9_]{2,23}$")
_CODE = re.compile(r"^(\.[A-Z]|-?\d+)\s*=")
_STOPWORDS = {
    "PRAMS",
    "CDC",
    "NOTE",
    "PAGE",
    "TABLE",
    "SECTION",
    "CODEBOOK",
    "PHASE",
    "VALUE",
    "LABEL",
    "VARIABLE",
    "FORMAT",
    "CODES",
}


_TABLE_NAME_HEADERS = ("variable name", "variable", "code", "name", "field")
_TABLE_LABEL_HEADERS = ("description", "question", "label", "sas label")
_TABLE_VALUES_HEADERS = ("values", "codes")
_TABLE_TYPE_HEADERS = ("type",)


def pass1_table(doc: Document) -> list[Variable]:
    """Deterministic extraction for spreadsheet codebooks rendered as ' | '-joined rows.

    A sheet is parsed when a header row names a variable column and a label/description column
    (e.g. NFR-CRS 'Variable name | Type | Description | Values', or CDC 'Code | Label').
    """
    found: dict[str, Variable] = {}
    for page in doc.pages:
        cols: dict[str, int] | None = None
        for raw in page.text.splitlines():
            cells = [c.strip() for c in raw.split(" | ")]
            low = [c.lower() for c in cells]
            if any(h in low for h in _TABLE_NAME_HEADERS) and any(h in low for h in _TABLE_LABEL_HEADERS):
                cols = {}
                for key, names in (
                    ("name", _TABLE_NAME_HEADERS),
                    ("label", _TABLE_LABEL_HEADERS),
                    ("values", _TABLE_VALUES_HEADERS),
                    ("type", _TABLE_TYPE_HEADERS),
                ):
                    for h in names:
                        if h in low:
                            cols[key] = low.index(h)
                            break
                continue
            if cols is None or len(cells) <= max(cols["name"], cols["label"]):
                continue
            name = cells[cols["name"]]
            label = cells[cols["label"]]
            if (
                not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.]{0,63}", name)
                or not label
                or name.lower() in ("variable", "code", "name")
            ):
                continue
            values = cells[cols["values"]] if "values" in cols and len(cells) > cols["values"] else ""
            vtype = cells[cols["type"]] if "type" in cols and len(cells) > cols["type"] else ""
            levels = [v.strip() for v in re.split(r"[;\n]|, (?=\d+\s*=)", values) if "=" in v] if values else []
            found.setdefault(
                name,
                Variable(
                    name=name,
                    label=label,
                    levels=levels,
                    page=page.number,
                    notes="; ".join(
                        x
                        for x in (
                            f"type={vtype}" if vtype else "",
                            f"values={values[:200]}" if values and not levels else "",
                        )
                        if x
                    ),
                ),
            )
    return list(found.values())


def pass1_regex(doc: Document) -> list[Variable]:
    """Deterministic extraction for the codebook layouts seen so far. Never invents names."""
    found: dict[str, Variable] = {v.name: v for v in pass1_table(doc)}
    for page in doc.pages:
        lines = [ln.strip() for ln in page.text.splitlines()]
        for i, line in enumerate(lines):
            m = _VAR_LINE.match(line)
            if m and m.group("name") not in _STOPWORDS:
                found.setdefault(
                    m.group("name"), Variable(name=m.group("name"), label=m.group("label").strip(), page=page.number)
                )
                continue
            if (
                _BARE_NAME.match(line)
                and line not in _STOPWORDS
                and i > 0
                and _after_qnum(lines, i)
                and i + 1 < len(lines)
            ):
                label_parts = []
                j = i + 1
                while j < len(lines) and lines[j] and not _CODE.match(lines[j]) and not _QNUM.match(lines[j]):
                    label_parts.append(lines[j])
                    j += 1
                levels = []
                while j < len(lines) and not _QNUM.match(lines[j]):
                    if _CODE.match(lines[j]):
                        levels.append(lines[j])
                    elif levels and lines[j] and not _BARE_NAME.match(lines[j]):
                        levels[-1] += " " + lines[j]  # wrapped code label
                    j += 1
                has_fmt = len(label_parts) > 1 and _FORMAT.match(label_parts[-1]) is not None
                label = " ".join(label_parts[:-1] if has_fmt else label_parts)
                fmt = label_parts[-1] if has_fmt else ""
                found.setdefault(
                    line,
                    Variable(
                        name=line,
                        label=label.strip() or line,
                        levels=levels,
                        page=page.number,
                        notes=f"format={fmt}" if fmt else "",
                    ),
                )
                continue
            nv = _nvss_name(line)
            if nv is None or nv[0] in _STOPWORDS or not _is_nvss_header(lines, i):
                continue
            name, inline_label = nv
            # The label may share the name's line (MBSTATE_REC), follow a blank line (SEX, CIG_0..3, BFED), or
            # equal the name (WIC). Known wart: some labels carry a trailing page number ("MHTR ... Inches 282").
            li = i if inline_label is not None else _nvss_label_index(lines, i)
            if li is None:
                continue
            label = inline_label if inline_label is not None else lines[li]
            levels = []
            j = li + 1
            while j < len(lines) and not _nvss_header_starts(lines, j):
                if _VALUE.match(lines[j]):
                    k = j + 1
                    while k < len(lines) and not lines[k]:
                        k += 1
                    if k < len(lines) and not _VALUE.match(lines[k]) and not _nvss_header_starts(lines, k):
                        levels.append(f"{lines[j]}={lines[k]}")
                        j = k
                j += 1
            prev = _prev_nonempty(lines, i, 3)
            found.setdefault(
                name,
                Variable(
                    name=name,
                    label=label,
                    levels=levels,
                    page=page.number,
                    notes=f"position={prev[0]}; file={prev[2]}",
                ),
            )
    for v in pass1_prams_unnumbered(doc):
        found.setdefault(v.name, v)
    return list(found.values())


def _after_qnum(lines: list[str], i: int) -> bool:
    """Is lines[i] preceded by a Q# cell, possibly wrapped onto two lines by the PDF ('18k_ARS' + 'C')?"""
    if _QNUM.match(lines[i - 1]):
        return True
    prev = _prev_nonempty(lines, i, 2)
    # The first part must carry a suffix ('_'), so an NVSS 'Len' + one-letter file flag ('2', 'G') never qualifies.
    return (
        len(prev) == 2
        and "_" in prev[0]
        and re.fullmatch(r"[A-Za-z]{1,2}", prev[1]) is not None
        and _QNUM.match(prev[0] + prev[1]) is not None
    )


def _label_like(line: str) -> bool:
    """Label text: has lowercase or a space, or closes a wrapped parenthetical ('SKIP)'); never a code line."""
    return (re.search(r"[a-z]", line) is not None or " " in line or line.endswith(")")) and not _CODE.match(line)


def _unnumbered_name_at(ne: list[str], i: int) -> bool:
    """A Variable cell of a PRAMS section without a Q# column: a bare name followed by a label line."""
    return (
        _BARE_NAME.match(ne[i]) is not None and ne[i] not in _STOPWORDS and i + 1 < len(ne) and _label_like(ne[i + 1])
    )


def pass1_prams_unnumbered(doc: Document) -> list[Variable]:
    """PRAMS ARF sections whose table has no Q# column (birth certificate, operations/weighting, analytic
    variables): Variable, SAS Label (may wrap), Format, Codes. Only pages with a 'SAS Label' header and no
    'Q#' header are read."""
    found: dict[str, Variable] = {}
    for page in doc.pages:
        ne = [ln.strip() for ln in page.text.splitlines() if ln.strip()]
        if "Q#" in ne or "SAS Label" not in ne:
            continue
        i = ne.index("SAS Label") + 1
        while i < len(ne):
            if not _unnumbered_name_at(ne, i):
                i += 1
                continue
            name, j = ne[i], i + 1
            label_parts = []
            while j < len(ne) and _label_like(ne[j]):
                label_parts.append(ne[j])
                j += 1
            fmt = ""
            if j < len(ne) and _FORMAT.match(ne[j]) and not _unnumbered_name_at(ne, j):
                fmt, j = ne[j], j + 1
            levels: list[str] = []
            while j < len(ne) and not _unnumbered_name_at(ne, j):
                if _CODE.match(ne[j]):
                    levels.append(ne[j])
                elif levels:
                    levels[-1] += " " + ne[j]  # wrapped code label
                j += 1
            found.setdefault(
                name,
                Variable(
                    name=name,
                    label=" ".join(label_parts),
                    levels=levels,
                    page=page.number,
                    notes=f"format={fmt}" if fmt else "",
                ),
            )
            i = j
    return list(found.values())


def _prev_nonempty(lines: list[str], i: int, n: int) -> list[str]:
    """The n non-empty lines before index i, in order."""
    out: list[str] = []
    j = i - 1
    while j >= 0 and len(out) < n:
        if lines[j]:
            out.insert(0, lines[j])
        j -= 1
    return out


_NVSS_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,23}$")
_NVSS_SPLIT_NAME = re.compile(r"^(?P<a>[A-Za-z][A-Za-z0-9_]*_)\s+(?P<b>[A-Z0-9_]{1,12})$")
_NVSS_INLINE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]*|[A-Z][A-Z0-9]{2,23})\s+(?P<label>\S.{2,})$")


def _nvss_name(line: str) -> tuple[str, str | None] | None:
    """(name, inline label or None) for the NAME line of an NVSS header, or None.

    Only consulted at the name position of a Position/Len/File header, so mixed-case names (OEGest_Comb,
    uRF_Diab) are safe to accept there. Also handles a name split by the PDF ("F_MM_ PLAC") and a name sharing
    its line with the label ("MBSTATE_REC Mother's Nativity")."""
    if _NVSS_NAME.match(line):
        return line, None
    if m := _NVSS_SPLIT_NAME.match(line):
        return m["a"] + m["b"], None
    if m := _NVSS_INLINE.match(line):
        return m["name"], m["label"].strip()
    return None


def _nvss_label_index(lines: list[str], i: int, window: int = 3) -> int | None:
    """Index of the label line for the NVSS NAME at lines[i]: the next non-empty line within `window` lines,
    unless it looks like the next header's position or length field."""
    for j in range(i + 1, min(i + 1 + window, len(lines))):
        if lines[j]:
            return None if _POSITION.match(lines[j]) or _LEN.match(lines[j]) else j
    return None


def _is_nvss_header(lines: list[str], i: int) -> bool:
    """Is lines[i] the NAME line of an NVSS 'Position / Len / File / Field' header?"""
    prev = _prev_nonempty(lines, i, 3)
    return (
        len(prev) == 3
        and _POSITION.match(prev[0]) is not None
        and _LEN.match(prev[1]) is not None
        and _FILEFLAG.match(prev[2]) is not None
        and i + 1 < len(lines)
    )


def _nvss_header_starts(lines: list[str], j: int) -> bool:
    """Does a new NVSS header begin at lines[j] (position line followed by len, file flag, name)?"""
    if not _POSITION.match(lines[j]):
        return False
    nxt = [ln for ln in lines[j + 1 : j + 8] if ln][:3]
    return (
        len(nxt) == 3
        and _LEN.match(nxt[0]) is not None
        and _FILEFLAG.match(nxt[1]) is not None
        and _nvss_name(nxt[2]) is not None
    )


class _VariableOut(BaseModel):
    """LLM-facing variant of Variable: `page` is a required integer so the model cannot omit it."""

    name: str
    label: str
    type: VariableType = VariableType.UNKNOWN
    levels: list[str] = Field(default_factory=list)
    years: list[int] = Field(default_factory=list)
    page: int = Field(description="The integer N from the nearest preceding [page N] marker. Required.")
    notes: str = ""

    def to_variable(self) -> Variable:
        return Variable(**self.model_dump())


class _VariableList(BaseModel):
    variables: list[_VariableOut] = Field(default_factory=list)


def pass2_llm(
    doc: Document,
    client: LLMClient,
    *,
    seed: int,
    temperature: float,
    chunk_tokens: int,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[list[Variable], list[LLMCallRecord]]:
    prompt = load_prompt("codebook_extract")
    variables: list[Variable] = []
    records: list[LLMCallRecord] = []
    for chunk in chunk_document(doc, chunk_tokens):
        user = prompt.render(first_page=str(chunk.first_page), last_page=str(chunk.last_page), text=chunk.text)
        obj, rec = generate(
            client,
            prompt,
            user,
            _VariableList,
            stage=f"codebook_extract_{chunk.index}",
            seed=seed,
            temperature=temperature,
            validators=[_page_validator(chunk.first_page, chunk.last_page)],
            max_retries=max_retries,
            log_dir=log_dir,
        )
        variables.extend(v.to_variable() for v in obj.variables)
        records.append(rec)
    return variables, records


def _page_validator(first: int, last: int) -> Callable[[_VariableList], list[str]]:
    return lambda v: _check_pages(v, first, last)


def _check_pages(v: _VariableList, first: int, last: int) -> list[str]:
    return [
        f"variable {x.name!r}: page={x.page} but this excerpt only contains pages {first}-{last}; "
        f"set page to the integer N of the [page N] marker above the definition"
        for x in v.variables
        if not first <= x.page <= last
    ]


def reconcile(doc: Document, pass1: list[Variable], pass2: list[Variable]) -> tuple[list[Variable], list[Variable]]:
    """Return (accepted, rejected). pass2 entries enrich pass1 entries with the same name."""
    accepted: dict[str, Variable] = {v.name.upper(): v for v in pass1}
    rejected: list[Variable] = []
    for v in pass2:
        key = v.name.upper()
        page_text = doc.page_text(v.page) if v.page else None
        name_on_page = (
            page_text is not None
            and re.search(rf"(?<![A-Z0-9_]){re.escape(v.name)}(?![A-Z0-9_])", page_text) is not None
        )
        if key in accepted:
            base = accepted[key]
            accepted[key] = base.model_copy(
                update={
                    "label": base.label or v.label,
                    "type": v.type if base.type == "unknown" else base.type,
                    "levels": base.levels or v.levels,
                    "years": base.years or v.years,
                    "notes": base.notes or v.notes,
                }
            )
        elif name_on_page:
            accepted[key] = v
        else:
            rejected.append(v)
    return sorted(accepted.values(), key=lambda x: (x.page or 0, x.name)), rejected


def build_datasource(
    doc: Document,
    source_id: str,
    client: LLMClient | None,
    *,
    title: str | None = None,
    seed: int = 0,
    temperature: float = 0.0,
    chunk_tokens: int = 12000,
    max_retries: int = 3,
    log_dir: Path | None = None,
) -> tuple[DataSource, list[Variable], list[LLMCallRecord]]:
    """Returns (datasource, rejected_llm_variables, llm_call_records)."""
    p1 = pass1_regex(doc)
    p2: list[Variable] = []
    records: list[LLMCallRecord] = []
    if client is not None:
        p2, records = pass2_llm(
            doc,
            client,
            seed=seed,
            temperature=temperature,
            chunk_tokens=chunk_tokens,
            max_retries=max_retries,
            log_dir=log_dir,
        )
    accepted, rejected = reconcile(doc, p1, p2)
    log.info("%s: pass1=%d pass2=%d accepted=%d rejected=%d", source_id, len(p1), len(p2), len(accepted), len(rejected))
    ds = DataSource(
        id=source_id, title=title or doc.title, document_path=doc.path, document_sha256=doc.sha256, variables=accepted
    )
    return ds, rejected, records
