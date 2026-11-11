"""Component C: knowledge gaps grounded in claims and resolvable variables."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from mmf.components.common import allowed_refs_text, mapped_keys
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource, SchemaMap
from mmf.schemas.gap import GapSet, KnowledgeGap
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord
from mmf.validate.grounding import unresolved_problems

PROMPTS = ("c_gaps",)


def prompt_hashes() -> list[str]:
    """sha256 of every prompt this component uses; part of the stage cache key."""
    return [load_prompt(name).sha256 for name in PROMPTS]


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
            problems += [f"{gap.id}: {p}" for p in citation_problems(gap, claim_ids)]
        return problems

    return check


_BARE = re.compile(r"(?<![\w.])C\d+\b")


def citation_problems(gap: KnowledgeGap, claim_ids: set[str]) -> list[str]:
    """Supporting claims must be the ones the gap's text builds on. On 2026-11-11 the model listed unrelated
    method claims as support while prior_art cited claims it had not listed. A bare `C12` in the text refers to
    a supporting claim ending in `.C12`."""

    def mentions(cid: str, text: str) -> bool:
        return re.search(rf"{re.escape(cid)}\b", text) is not None

    problems = []
    text = f"{gap.prior_art} {gap.rationale}"
    for cid in sorted(claim_ids - set(gap.supporting_claim_ids)):
        if mentions(cid, gap.prior_art):
            problems.append(f"prior_art cites {cid}, which is not in supporting_claim_ids")
    for bare in sorted(set(_BARE.findall(gap.prior_art))):
        if not any(cid.endswith(f".{bare}") for cid in gap.supporting_claim_ids):
            problems.append(f"prior_art cites {bare}, which is not in supporting_claim_ids")
    for cid in gap.supporting_claim_ids:
        short = cid.rsplit(".", 1)[-1]
        if not mentions(cid, text) and not re.search(rf"(?<![\w.]){re.escape(short)}\b", text):
            problems.append(
                f"supporting claim {cid} is not discussed in prior_art or rationale; cite only claims the gap builds on "
                "and say how each one bears on it"
            )
    return problems


def populations_text(sources: dict[str, DataSource], populations: dict[str, str]) -> str:
    return "\n".join(f"- {sid}: {populations.get(sid, 'not stated')}" for sid in sources)


def find_gaps(
    decomps: list[ManuscriptDecomposition],
    schema_map: SchemaMap,
    sources: dict[str, DataSource],
    client: LLMClient,
    *,
    n_gaps: int,
    populations: dict[str, str] | None = None,
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
        n_gaps=str(n_gaps),
        decompositions=dec_text,
        mapping=map_text,
        allowed_refs=allowed_refs_text(sources, only=mapped_keys(schema_map) or None),
        populations=populations_text(sources, populations or {}),
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
