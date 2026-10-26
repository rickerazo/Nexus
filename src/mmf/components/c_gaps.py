"""Component C: knowledge gaps grounded in claims and resolvable variables."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mmf.components.common import allowed_refs_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource, SchemaMap
from mmf.schemas.gap import GapSet
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord
from mmf.validate.grounding import unresolved_problems


def gap_validator(
    decomps: list[ManuscriptDecomposition], sources: dict[str, DataSource], n_gaps: int
) -> Callable[[GapSet], list[str]]:
    claim_ids = {c.id for d in decomps for c in d.claims}

    def check(g: GapSet) -> list[str]:
        problems = []
        if len(g.gaps) != n_gaps:
            problems.append(f"expected exactly {n_gaps} gaps, got {len(g.gaps)}")
        for gap in g.gaps:
            missing = [cid for cid in gap.supporting_claim_ids if cid not in claim_ids]
            if missing:
                problems.append(f"{gap.id}: unknown claim ids {missing}")
            if not gap.supporting_claim_ids:
                problems.append(f"{gap.id}: must cite at least one claim id")
            if not gap.required_variables:
                problems.append(f"{gap.id}: must list at least one required variable")
            problems += [f"{gap.id}: {p}" for p in unresolved_problems(gap.required_variables, sources)]
            if len(gap.prior_art.split()) < 15:
                problems.append(f"{gap.id}: prior_art must explain what was already tested (too short)")
        return problems

    return check


def find_gaps(
    decomps: list[ManuscriptDecomposition],
    schema_map: SchemaMap,
    sources: dict[str, DataSource],
    client: LLMClient,
    *,
    n_gaps: int,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[GapSet, list[LLMCallRecord]]:
    prompt = load_prompt("c_gaps")
    dec_text = "\n\n".join(d.model_dump_json(indent=1, exclude={"document_sha256"}) for d in decomps)
    map_text = "\n".join(
        f"- {m.concept} -> ({m.source_id}, {m.variable}) [{m.compatibility}]" for m in schema_map.mappings
    )
    user = prompt.render(
        n_gaps=str(n_gaps), decompositions=dec_text, mapping=map_text, allowed_refs=allowed_refs_text(sources)
    )
    obj, rec = generate(
        client,
        prompt,
        user,
        GapSet,
        stage="C_gaps",
        seed=seed,
        temperature=temperature,
        validators=[gap_validator(decomps, sources, n_gaps)],
        max_retries=max_retries,
        log_dir=log_dir,
    )
    return obj, [rec]
