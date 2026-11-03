"""Component A: manuscript -> ManuscriptDecomposition, quote-anchored."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from pydantic import Field

from mmf.ingest.chunk import chunk_document
from mmf.ingest.pdf import Document
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.manuscript import Claim, ManuscriptDecomposition, VariableMention
from mmf.schemas.run import LLMCallRecord
from mmf.validate.grounding import quote_problems
from mmf.validate.vocab import vocab_text

MAX_CLAIMS_PER_CHUNK = 60
MAX_VARIABLES_PER_CHUNK = 60


class ChunkDecomposition(ManuscriptDecomposition):
    """LLM-facing output for one chunk: list sizes are capped in the JSON schema (grammar-enforced by Ollama),
    so a model that starts enumerating cannot run away; the merged decomposition is uncapped."""

    claims: list[Claim] = Field(default_factory=list, max_length=MAX_CLAIMS_PER_CHUNK)
    variables: list[VariableMention] = Field(default_factory=list, max_length=MAX_VARIABLES_PER_CHUNK)


def quote_validator(doc: Document) -> Callable[[ManuscriptDecomposition], list[str]]:
    def check(d: ManuscriptDecomposition) -> list[str]:
        problems = []
        for c in d.claims:
            problems += [f"claim {c.id}: {p}" for p in quote_problems(c.quote, doc)]
        for v in d.variables:
            problems += [f"variable {v.concept!r}: {p}" for p in quote_problems(v.quote, doc)]
        ids = [c.id for c in d.claims]
        if len(ids) != len(set(ids)):
            problems.append("claim ids must be unique")
        return problems

    return check


_CLAIM_PROBLEM = re.compile(r"^claim (\S+): ")
_VAR_PROBLEM = re.compile(r"^variable (['\"])(.*)\1: ")


def drop_ungrounded(d: ChunkDecomposition, problems: list[str]) -> tuple[ChunkDecomposition, list[str]]:
    """Salvage for Component A: remove the claims/variables named in quote-grounding problems.

    The local model fixes one quote and breaks another across retries; rather than fail the run
    on the last attempt, the still-ungrounded items are dropped and listed in the call record.
    Problems that name no item (e.g. duplicate ids) are not salvageable and leave the output failing.
    """
    bad_claims = {m.group(1) for p in problems if (m := _CLAIM_PROBLEM.match(p))}
    bad_vars = {m.group(2) for p in problems if (m := _VAR_PROBLEM.match(p))}
    dropped = [f"claim {c.id}: {c.statement}" for c in d.claims if c.id in bad_claims]
    dropped += [f"variable {v.concept!r}: {v.operationalization}" for v in d.variables if v.concept in bad_vars]
    pruned = d.model_copy(
        update={
            "claims": [c for c in d.claims if c.id not in bad_claims],
            "variables": [v for v in d.variables if v.concept not in bad_vars],
        }
    )
    return pruned, dropped


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
            ChunkDecomposition,
            stage=f"A_{manuscript_id}_{chunk.index}",
            seed=seed,
            temperature=temperature,
            validators=[quote_validator(doc)],
            max_retries=max_retries,
            log_dir=log_dir,
            salvage=drop_ungrounded,
        )
        parts.append(ManuscriptDecomposition.model_validate(obj.model_dump()))
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
