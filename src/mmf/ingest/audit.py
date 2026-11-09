"""Independent audit of a parsed codebook: does the DataSource account for what the document contains?

This deliberately shares no extraction logic (regexes, helpers, stopwords) with `codebook.pass1_regex`, so a
parser bug cannot hide itself. Two checks:

- Anchor reconciliation (hard): every NVSS Position / Len / File-flag header in the document must correspond to
  exactly one extracted variable with the same position and file flag. A miss means the parser silently dropped
  a variable, and the run must stop before B.
- Identifier census (soft): codebook-style identifiers standing alone on a line, or in the first cell of a table
  row, that are not extracted variable names. Listed for a human to read; never an error.
"""

from __future__ import annotations

import re

from mmf.ingest.pdf import Document
from mmf.schemas.dataset import AnchorMiss, CodebookAudit, DataSource, IdentifierSighting

_ANCHOR_POS = re.compile(r"\d{1,4}(?:-\d{1,4})?")
_ANCHOR_LEN = re.compile(r"\d{1,3}")
_ANCHOR_FILE = re.compile(r"[A-Z](?:,[A-Z])*")
_NOTE_POS = re.compile(r"position=(?P<pos>[^;]+);\s*file=(?P<file>\S+)")
_IDENT = re.compile(r"[A-Z][A-Z0-9_]{2,23}")
_NOT_IDENT = {
    # layout words and common all-caps prose in codebooks; not variable names
    "BLANK", "CDC", "CODE", "CODEBOOK", "CODES", "FIELD", "FILE", "FILLER", "FORMAT", "LABEL", "LEN", "NCHS",
    "NOTE", "NOTES", "PAGE", "PHASE", "POSITION", "PRAMS", "SECTION", "TABLE", "TOTAL", "TYPE", "UNKNOWN",
    "VALUE", "VALUES", "VARIABLE", "YES",
}  # fmt: skip


def find_anchors(doc: Document) -> list[tuple[int, str, str, str]]:
    """(page, position, file flag, text at the name position) for every NVSS field header."""
    out = []
    for page in doc.pages:
        ne = [ln.strip() for ln in page.text.splitlines() if ln.strip()]
        for k in range(len(ne) - 3):
            if _ANCHOR_POS.fullmatch(ne[k]) and _ANCHOR_LEN.fullmatch(ne[k + 1]) and _ANCHOR_FILE.fullmatch(ne[k + 2]):
                out.append((page.number, ne[k], ne[k + 2], ne[k + 3]))
    return out


def audit_codebook(doc: Document, ds: DataSource) -> CodebookAudit:
    by_anchor: dict[tuple[str, str], list[str]] = {}
    for v in ds.variables:
        if m := _NOTE_POS.search(v.notes):
            by_anchor.setdefault((m["pos"].strip(), m["file"].strip()), []).append(v.name)

    anchors = [a for a in find_anchors(doc) if not a[3].upper().startswith("FILLER")]
    misses = []
    for pno, pos, flag, text in anchors:
        names = by_anchor.get((pos, flag), [])
        if len(names) != 1:
            misses.append(AnchorMiss(page=pno, position=pos, file=flag, text=text[:120], extracted=names))

    extracted = {v.name.upper() for v in ds.variables}
    census: dict[str, IdentifierSighting] = {}
    for page in doc.pages:
        for line in page.text.splitlines():
            line = line.strip()
            token = line.split(" | ", 1)[0].strip() if " | " in line else line
            if not _IDENT.fullmatch(token) or token in _NOT_IDENT or token.upper() in extracted:
                continue
            if token in census:
                census[token].count += 1
            else:
                census[token] = IdentifierSighting(token=token, page=page.number, context=line[:160], count=1)
    return CodebookAudit(
        source_id=ds.id,
        n_variables=len(ds.variables),
        anchors_checked=len(anchors),
        unmatched_anchors=misses,
        census=sorted(census.values(), key=lambda s: (s.page, s.token)),
    )
