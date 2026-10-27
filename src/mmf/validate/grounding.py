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


def quote_found(quote: str, doc: Document, page: int | None = None, fuzzy: float = 0.95) -> tuple[bool, int | None]:
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
    # fuzzy fallback (PDF extraction noise), same-page first then all pages
    for p in candidates + [p for p in doc.pages if p not in candidates]:
        ratio, _, _ = _best_window(q, normalize(p.text))
        if ratio >= fuzzy:
            return True, p.number
    return False, None


def _best_window(q: str, t: str) -> tuple[float, int, str]:
    """Best (ratio, start, window) of q against t: coarse scan, then step-1 refinement around the best."""
    if not t:
        return 0.0, 0, ""
    n = len(q)
    coarse = max(1, n // 4)
    best = (0.0, 0)
    for i in range(0, max(1, len(t) - n + 1), coarse):
        r = SequenceMatcher(None, q, t[i : i + n]).ratio()
        if r > best[0]:
            best = (r, i)
    lo, hi = max(0, best[1] - coarse), min(len(t) - 1, best[1] + coarse)
    for i in range(lo, hi + 1):
        r = SequenceMatcher(None, q, t[i : i + n]).ratio()
        if r > best[0]:
            best = (r, i)
    return best[0], best[1], t[best[1] : best[1] + n]


_SENT = re.compile(r"(?<=[.;:?!])\s+(?=[A-Za-z(\[])")


def closest_span(quote: str, doc: Document, page: int | None = None) -> tuple[float, str, int | None]:
    """Best-matching window of document text for a quote: (ratio, text, page)."""
    q = normalize(quote)
    best: tuple[float, str, int | None] = (0.0, "", None)
    candidates = [p for p in doc.pages if page is None or p.number == page] or doc.pages
    for p in candidates:
        r, _, window = _best_window(q, normalize(p.text))
        if r > best[0]:
            best = (r, window, p.number)
    return best


def quote_problems(quote: str, doc: Document, page: int | None = None, fuzzy: float = 0.95) -> list[str]:
    """Verify a quote sentence by sentence. Each sentence (>= 15 chars) must occur verbatim (after
    normalization, fuzzy >= `fuzzy` for PDF noise). Returns one problem per failing sentence, with
    the closest document text so a retry can copy it exactly. Empty list = grounded.

    Sentence-level checking tolerates a model stitching two true sentences together while still
    rejecting paraphrase: every sentence must itself be in the document.
    """
    if quote_found(quote, doc, page, fuzzy)[0]:
        return []
    sentences = [x.strip() for x in _SENT.split(quote.strip()) if len(x.strip()) >= 15]
    if not sentences:
        return [f"quote too short to verify (need >= 15 characters): {quote!r}"]
    problems = []
    for sent in sentences:
        ok, _ = quote_found(sent, doc, page, fuzzy)
        if not ok:
            ratio, near, pg = closest_span(sent, doc, page)
            hint = f' Closest text (p.{pg}): "{near[:220]}"' if ratio >= 0.6 else ""
            problems.append(f'not verbatim in the document: "{sent[:120]}".{hint}')
    return problems


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
