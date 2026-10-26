"""Component A: manuscript -> ManuscriptDecomposition, quote-anchored."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mmf.ingest.chunk import chunk_document
from mmf.ingest.pdf import Document
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord
from mmf.validate.grounding import quote_found
from mmf.validate.vocab import vocab_text


def quote_validator(doc: Document) -> Callable[[ManuscriptDecomposition], list[str]]:
    def check(d: ManuscriptDecomposition) -> list[str]:
        problems = []
        for c in d.claims:
            ok, _ = quote_found(c.quote, doc)
            if not ok:
                problems.append(f"claim {c.id}: quote not found verbatim in manuscript: {c.quote[:80]!r}")
        for v in d.variables:
            ok, _ = quote_found(v.quote, doc)
            if not ok:
                problems.append(f"variable {v.concept!r}: quote not found verbatim: {v.quote[:80]!r}")
        ids = [c.id for c in d.claims]
        if len(ids) != len(set(ids)):
            problems.append("claim ids must be unique")
        return problems

    return check


def decompose(
    doc: Document,
    manuscript_id: str,
    client: LLMClient,
    *,
    seed: int,
    temperature: float,
    chunk_tokens: int,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[ManuscriptDecomposition, list[LLMCallRecord]]:
    prompt = load_prompt("a_decompose").bind(vocab=vocab_text())
    parts: list[ManuscriptDecomposition] = []
    records: list[LLMCallRecord] = []
    for chunk in chunk_document(doc, chunk_tokens):
        user = prompt.render(
            title=doc.title,
            first_page=str(chunk.first_page),
            last_page=str(chunk.last_page),
            text=chunk.text,
            vocab=vocab_text(),
        )
        obj, rec = generate(
            client,
            prompt,
            user,
            ManuscriptDecomposition,
            stage=f"A_{manuscript_id}_{chunk.index}",
            seed=seed,
            temperature=temperature,
            validators=[quote_validator(doc)],
            max_retries=max_retries,
            log_dir=log_dir,
        )
        parts.append(obj)
        records.append(rec)
    return _merge(parts, manuscript_id, doc), records


def _merge(parts: list[ManuscriptDecomposition], manuscript_id: str, doc: Document) -> ManuscriptDecomposition:
    merged = ManuscriptDecomposition(manuscript_id=manuscript_id, title=doc.title, document_sha256=doc.sha256)
    n = 0
    seen_q: set[str] = set()
    for p in parts:
        for q in p.research_questions:
            if q.strip().lower() not in seen_q:
                seen_q.add(q.strip().lower())
                merged.research_questions.append(q)
        merged.designs = list(dict.fromkeys([*merged.designs, *p.designs]))
        merged.model_classes = list(dict.fromkeys([*merged.model_classes, *p.model_classes]))
        merged.data_sources_used = list(dict.fromkeys([*merged.data_sources_used, *p.data_sources_used]))
        merged.variables.extend(p.variables)
        for c in p.claims:
            n += 1
            merged.claims.append(c.model_copy(update={"id": f"{manuscript_id}.C{n}"}))
    return merged
