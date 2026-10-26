"""Component B: manuscript concepts -> codebook variables, per source."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mmf.components.common import sources_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
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
) -> tuple[SchemaMap, list[LLMCallRecord]]:
    prompt = load_prompt("b_schema_map")
    concepts: dict[str, str] = {}
    for d in decompositions:
        for v in d.variables:
            concepts.setdefault(v.concept, f"{v.role}; {v.operationalization}")
    concept_text = "\n".join(f"- {k}: {v}" for k, v in concepts.items())
    user = prompt.render(concepts=concept_text, sources=sources_text(sources))
    obj, rec = generate(
        client,
        prompt,
        user,
        SchemaMap,
        stage="B_schema_map",
        seed=seed,
        temperature=temperature,
        validators=[map_validator(sources)],
        max_retries=max_retries,
        log_dir=log_dir,
    )
    return obj, [rec]
