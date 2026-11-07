"""Component B: manuscript concepts -> codebook variables, per source."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mmf.components.common import source_groups, sources_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import StageInputError, generate
from mmf.schemas.dataset import DataSource, SchemaMap
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord

COMPAT = {"direct", "proxy", "derived", "none"}


def map_validator(sources: dict[str, DataSource]) -> Callable[[SchemaMap], list[str]]:
    def check(m: SchemaMap) -> list[str]:
        problems = []
        for x in m.mappings:
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
) -> tuple[SchemaMap, list[LLMCallRecord]]:
    """One call per (source group, concept batch); large codebooks are split into groups and long concept
    lists into batches so each call fits the context and the output cap. Mappings are merged. For a concept
    with several candidate variables in one source, every candidate is kept for human review."""
    concepts = collect_concepts(decompositions)
    if not concepts:
        raise StageInputError("B", ["no concepts to map: Component A extracted no variables from any manuscript"])
    prompt = load_prompt("b_schema_map")
    merged = SchemaMap()
    records = []
    for gi, group in enumerate(source_groups(sources, max_vars_per_call)):
        batch = max(1, max_mappings_per_call // len(group))
        for bi in range(0, len(concepts), batch):
            concept_text = "\n".join(f"- {k}: {v}" for k, v in concepts[bi : bi + batch])
            user = prompt.render(concepts=concept_text, sources=sources_text(group))
            obj, rec = generate(
                client,
                prompt,
                user,
                SchemaMap,
                stage=f"B_schema_map_{gi}_{bi // batch}",
                seed=seed,
                temperature=temperature,
                validators=[map_validator(group)],
                max_retries=max_retries,
                log_dir=log_dir,
            )
            records.append(rec)
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
    return merged, records


def collect_concepts(decompositions: list[ManuscriptDecomposition]) -> list[tuple[str, str]]:
    """(concept, 'role; operationalization') across manuscripts, first occurrence wins, case-insensitive."""
    seen: dict[str, tuple[str, str]] = {}
    for d in decompositions:
        for v in d.variables:
            seen.setdefault(v.concept.strip().lower(), (v.concept.strip(), f"{v.role}; {v.operationalization}"))
    return list(seen.values())
