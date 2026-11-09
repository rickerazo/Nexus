"""Component B: manuscript concepts -> codebook variables, per source."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import NamedTuple

from mmf.components.common import source_groups, sources_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import StageInputError, generate
from mmf.schemas.dataset import DataSource, SchemaMap
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord

PROMPTS = ("b_schema_map",)


def prompt_hashes() -> list[str]:
    """sha256 of every prompt this component uses; part of the stage cache key."""
    return [load_prompt(name).sha256 for name in PROMPTS]


COMPAT = {"direct", "proxy", "derived", "none"}


class Concept(NamedTuple):
    """A concept sent to B: its name exactly as A extracted it, its role, and how it was operationalized."""

    name: str
    role: str
    operationalization: str


def canonical_concept(returned: str, batch: Sequence[Concept]) -> str | None:
    """The sent concept name that `returned` refers to, or None.

    Accepted, in order: an exact match; a case-insensitive match; the name with a trailing
    "as <role>" removed, where <role> is the role that concept was sent with. Anything else is rejected.
    """
    if any(c.name == returned for c in batch):
        return returned
    low = returned.strip().lower()
    for c in batch:
        if c.name.lower() == low:
            return c.name
    for c in batch:
        role = re.escape(c.role.lower()).replace("_", "[_ ]")
        stripped = re.sub(rf"\s+as\s+(?:an?\s+)?{role}$", "", low)
        if stripped != low and stripped == c.name.lower():
            return c.name
    return None


def map_validator(
    sources: dict[str, DataSource], batch: Sequence[Concept] | None = None
) -> Callable[[SchemaMap], list[str]]:
    def check(m: SchemaMap) -> list[str]:
        problems = []
        for x in m.mappings:
            if batch is not None and canonical_concept(x.concept, batch) is None:
                problems.append(f"concept {x.concept!r} was not in the list; copy the concept name exactly as given")
            if x.source_id not in sources:
                problems.append(f"mapping for {x.concept!r}: unknown source_id {x.source_id!r}")
                continue
            if x.compatibility not in COMPAT:
                problems.append(f"mapping for {x.concept!r}: compatibility must be one of {sorted(COMPAT)}")
            if x.variable is not None and sources[x.source_id].lookup(x.variable) is None:
                problems.append(
                    f"mapping for {x.concept!r}: {x.variable!r} is not a documented variable in {x.source_id}"
                )
            if x.variable is None and x.compatibility != "none":
                problems.append(f"mapping for {x.concept!r}: null variable requires compatibility 'none'")
        return problems

    return check


def canonicalize(m: SchemaMap, batch: Sequence[Concept]) -> int:
    """Rewrite accepted concept names to their sent form in place; return how many were rewritten.
    Call only on output that passed `map_validator(..., batch)`."""
    n = 0
    for x in m.mappings:
        name = canonical_concept(x.concept, batch)
        if name is not None and name != x.concept:
            x.concept = name
            n += 1
    return n


def concepts_text(batch: Sequence[Concept]) -> str:
    return "\n".join(f'- "{c.name}" (role: {c.role}) — {c.operationalization}' for c in batch)


def map_schema(
    decompositions: list[ManuscriptDecomposition],
    sources: dict[str, DataSource],
    client: LLMClient,
    *,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    max_vars_per_call: int = 350,
    max_mappings_per_call: int = 50,
) -> tuple[SchemaMap, list[LLMCallRecord], list[str]]:
    """One call per (source group, concept batch); large codebooks are split into groups and long concept
    lists into batches so each call fits the context and the output cap. Mappings are merged. For a concept
    with several candidate variables in one source, every candidate is kept for human review.

    Returns (schema map, call records, warnings). Warnings record concept names rewritten to their sent form
    and (concept, source) pairs the model left without any row."""
    concepts = collect_concepts(decompositions)
    if not concepts:
        raise StageInputError("B", ["no concepts to map: Component A extracted no variables from any manuscript"])
    prompt = load_prompt("b_schema_map")
    merged = SchemaMap()
    records = []
    warnings: list[str] = []
    for gi, group in enumerate(source_groups(sources, max_vars_per_call)):
        batch = max(1, max_mappings_per_call // len(group))
        for bi in range(0, len(concepts), batch):
            sent = concepts[bi : bi + batch]
            stage = f"B_schema_map_{gi}_{bi // batch}"
            user = prompt.render(concepts=concepts_text(sent), sources=sources_text(group))
            obj, rec = generate(
                client,
                prompt,
                user,
                SchemaMap,
                stage=stage,
                seed=seed,
                temperature=temperature,
                validators=[map_validator(group, sent)],
                max_retries=max_retries,
                log_dir=log_dir,
            )
            records.append(rec)
            renamed = canonicalize(obj, sent)
            if renamed:
                warnings.append(f"{stage}: {renamed} concept names canonicalized to the names sent")
            covered = {(m.concept, m.source_id) for m in obj.mappings}
            missing = [f"{c.name} / {sid}" for c in sent for sid in group if (c.name, sid) not in covered]
            if missing:
                warnings.append(f"{stage}: no row for {len(missing)} (concept, source) pair(s): {'; '.join(missing)}")
            for m in obj.mappings:
                if m.variable is None and any(
                    x.concept == m.concept and x.source_id == m.source_id and x.variable for x in merged.mappings
                ):
                    continue  # another part of this source already mapped it
                merged.mappings.append(m)
            for sid, text in obj.source_summaries.items():
                merged.source_summaries[sid] = (merged.source_summaries.get(sid, "") + " " + text).strip()
    # drop 'none' rows for concept/source pairs that got a real mapping from another group
    mapped = {(m.concept, m.source_id) for m in merged.mappings if m.variable}
    merged.mappings = [m for m in merged.mappings if m.variable or (m.concept, m.source_id) not in mapped]
    return merged, records, warnings


def collect_concepts(decompositions: list[ManuscriptDecomposition]) -> list[Concept]:
    """Concepts across manuscripts, first occurrence wins, case-insensitive."""
    seen: dict[str, Concept] = {}
    for d in decompositions:
        for v in d.variables:
            seen.setdefault(v.concept.strip().lower(), Concept(v.concept.strip(), str(v.role), v.operationalization))
    return list(seen.values())
