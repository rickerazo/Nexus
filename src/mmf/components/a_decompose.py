"""Component A: manuscript -> ManuscriptDecomposition, quote-anchored.

Each chunk gets two focused calls: a study profile (research questions, data sources, designs,
model classes, variables) and the claims. Every field of the LLM-facing models is required, so a
grammar-constrained decoder cannot skip a list by omitting its key; an empty list is still allowed
per chunk (e.g. a references-only chunk), and the document-level check in `decomposition_problems`
decides whether an empty result is acceptable.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, Field

from mmf.ingest.chunk import chunk_document
from mmf.ingest.pdf import Document
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.manuscript import Claim, ManuscriptDecomposition, VariableMention
from mmf.schemas.run import LLMCallRecord
from mmf.validate.grounding import quote_problems
from mmf.validate.vocab import ModelClass, StudyDesign, vocab_text

MAX_CLAIMS_PER_CHUNK = 60
MAX_VARIABLES_PER_CHUNK = 60
PROMPTS = ("a_profile", "a_claims")


class ChunkProfile(BaseModel):
    """LLM-facing study profile for one chunk. All fields required; list sizes capped in the JSON schema
    (grammar-enforced by Ollama) so a model that starts enumerating cannot run away."""

    research_questions: list[str] = Field(description="Research questions or aims the text states.")
    data_sources_used: list[str] = Field(description="Datasets the study analysed, as written.")
    designs: list[StudyDesign]
    model_classes: list[ModelClass]
    variables: list[VariableMention] = Field(max_length=MAX_VARIABLES_PER_CHUNK)


class ChunkClaims(BaseModel):
    """LLM-facing claims for one chunk."""

    claims: list[Claim] = Field(max_length=MAX_CLAIMS_PER_CHUNK)


Chunk = TypeVar("Chunk", ChunkProfile, ChunkClaims)


def prompt_hashes() -> list[str]:
    """sha256 of every Component A prompt; part of the stage cache key."""
    return [load_prompt(name).sha256 for name in PROMPTS]


def quote_validator(doc: Document) -> Callable[[ChunkProfile | ChunkClaims], list[str]]:
    def check(d: ChunkProfile | ChunkClaims) -> list[str]:
        problems = []
        if isinstance(d, ChunkClaims):
            for c in d.claims:
                problems += [f"claim {c.id}: {p}" for p in quote_problems(c.quote, doc)]
            ids = [c.id for c in d.claims]
            if len(ids) != len(set(ids)):
                problems.append("claim ids must be unique")
        else:
            for v in d.variables:
                problems += [f"variable {v.concept!r}: {p}" for p in quote_problems(v.quote, doc)]
        return problems

    return check


_CLAIM_PROBLEM = re.compile(r"^claim (\S+): ")
_VAR_PROBLEM = re.compile(r"^variable (['\"])(.*)\1: ")


def drop_ungrounded(d: Chunk, problems: list[str]) -> tuple[Chunk, list[str]]:
    """Salvage for Component A: remove the claims/variables named in quote-grounding problems.

    The local model fixes one quote and breaks another across retries; rather than fail the run
    on the last attempt, the still-ungrounded items are dropped and listed in the call record.
    Problems that name no item (e.g. duplicate ids) are not salvageable and leave the output failing.
    """
    if isinstance(d, ChunkClaims):
        bad_claims = {m.group(1) for p in problems if (m := _CLAIM_PROBLEM.match(p))}
        dropped = [f"claim {c.id}: {c.statement}" for c in d.claims if c.id in bad_claims]
        return d.model_copy(update={"claims": [c for c in d.claims if c.id not in bad_claims]}), dropped
    bad_vars = {m.group(2) for p in problems if (m := _VAR_PROBLEM.match(p))}
    dropped = [f"variable {v.concept!r}: {v.operationalization}" for v in d.variables if v.concept in bad_vars]
    return d.model_copy(update={"variables": [v for v in d.variables if v.concept not in bad_vars]}), dropped


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
    profile_prompt = load_prompt("a_profile").bind(vocab=vocab_text())
    claims_prompt = load_prompt("a_claims")
    validator = quote_validator(doc)
    parts: list[tuple[ChunkProfile, ChunkClaims]] = []
    records: list[LLMCallRecord] = []
    for chunk in chunk_document(doc, chunk_tokens):
        fields = {
            "title": doc.title,
            "first_page": str(chunk.first_page),
            "last_page": str(chunk.last_page),
            "text": chunk.text,
        }
        profile, rec_p = generate(
            client,
            profile_prompt,
            profile_prompt.render(**fields),
            ChunkProfile,
            stage=f"A_{manuscript_id}_{chunk.index}_profile",
            validators=[validator],
            salvage=drop_ungrounded,
            seed=seed,
            temperature=temperature,
            max_retries=max_retries,
            log_dir=log_dir,
        )
        claims, rec_c = generate(
            client,
            claims_prompt,
            claims_prompt.render(**fields),
            ChunkClaims,
            stage=f"A_{manuscript_id}_{chunk.index}_claims",
            validators=[validator],
            salvage=drop_ungrounded,
            seed=seed,
            temperature=temperature,
            max_retries=max_retries,
            log_dir=log_dir,
        )
        parts.append((profile, claims))
        records += [rec_p, rec_c]
    return _merge(parts, manuscript_id, doc), records


def _merge(parts: list[tuple[ChunkProfile, ChunkClaims]], manuscript_id: str, doc: Document) -> ManuscriptDecomposition:
    merged = ManuscriptDecomposition(manuscript_id=manuscript_id, title=doc.title, document_sha256=doc.sha256)
    n = 0
    seen_q: set[str] = set()
    seen_v: set[tuple[str, str]] = set()
    for profile, claims in parts:
        for q in profile.research_questions:
            if q.strip().lower() not in seen_q:
                seen_q.add(q.strip().lower())
                merged.research_questions.append(q)
        merged.designs = list(dict.fromkeys([*merged.designs, *profile.designs]))
        merged.model_classes = list(dict.fromkeys([*merged.model_classes, *profile.model_classes]))
        merged.data_sources_used = list(dict.fromkeys([*merged.data_sources_used, *profile.data_sources_used]))
        for v in profile.variables:
            key = (v.concept.strip().lower(), v.role.value)
            if key not in seen_v:
                seen_v.add(key)
                merged.variables.append(v)
        for c in claims.claims:
            n += 1
            merged.claims.append(c.model_copy(update={"id": f"{manuscript_id}.C{n}"}))
    return merged


def decomposition_problems(dec: ManuscriptDecomposition) -> tuple[list[str], list[str]]:
    """Document-level check after merging chunks: (errors, warnings).

    Errors stop the run: a manuscript with no grounded variables gives Component B nothing to map, and
    one with no claims gives Component C nothing to cite. Missing designs/model classes are only warnings,
    because a collection of abstracts often states none.
    """
    errors, warnings = [], []
    if not dec.variables:
        errors.append(f"{dec.manuscript_id}: no grounded variables extracted")
    if not dec.claims:
        errors.append(f"{dec.manuscript_id}: no grounded claims extracted")
    if not dec.designs:
        warnings.append(f"{dec.manuscript_id}: no study design extracted")
    if not dec.model_classes:
        warnings.append(f"{dec.manuscript_id}: no model class extracted")
    return errors, warnings
