"""Hard grounding checks. These, not prompt wording, are what make generation 'constrained'."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from mmf.ingest.pdf import Document
from mmf.schemas.dataset import DataSource, VariableRef
from mmf.schemas.feasibility import VariableResolution

_WS = re.compile(r"\s+")
_LIGATURES = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "­": ""})


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(_LIGATURES)
    text = text.replace("-\n", "")  # hyphenated line breaks from PDF extraction
    return _WS.sub(" ", text).strip().lower()


def quote_found(quote: str, doc: Document, page: int | None = None, fuzzy: float = 0.92) -> tuple[bool, int | None]:
    """Is `quote` present verbatim (after normalization) in the document? Returns (found, page).

    Falls back to a fuzzy ratio over a sliding window to tolerate PDF extraction noise; the
    threshold is deliberately high so paraphrases are rejected.
    """
    q = normalize(quote)
    if len(q) < 15:
        return False, None
    candidates = [p for p in doc.pages if page is None or p.number == page] or doc.pages
    for p in candidates:
        if q in normalize(p.text):
            return True, p.number
    # fuzzy fallback, same-page first then all pages
    for p in candidates + [p for p in doc.pages if p not in candidates]:
        t = normalize(p.text)
        step = max(1, len(q) // 2)
        for i in range(0, max(1, len(t) - len(q) + 1), step):
            if SequenceMatcher(None, q, t[i : i + len(q) + step]).ratio() >= fuzzy:
                return True, p.number
    return False, None


def resolve_refs(refs: list[VariableRef], sources: dict[str, DataSource]) -> list[VariableResolution]:
    out: list[VariableResolution] = []
    for ref in refs:
        src = sources.get(ref.source_id)
        if src is None:
            out.append(
                VariableResolution(
                    ref=ref,
                    resolved=False,
                    note=f"unknown source_id {ref.source_id!r}; known: {sorted(sources)}",
                )
            )
            continue
        var = src.lookup(ref.name)
        if var is None:
            out.append(
                VariableResolution(
                    ref=ref,
                    resolved=False,
                    note=f"{ref.name!r} is not a documented variable in {ref.source_id}",
                )
            )
        else:
            out.append(VariableResolution(ref=ref, resolved=True, variable=var))
    return out


def unresolved_problems(refs: list[VariableRef], sources: dict[str, DataSource]) -> list[str]:
    return [r.note for r in resolve_refs(refs, sources) if not r.resolved]
