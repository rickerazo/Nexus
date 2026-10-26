"""Component D: one Strategy per gap, every variable resolvable, vocab-constrained."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mmf.components.common import allowed_refs_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource
from mmf.schemas.gap import KnowledgeGap
from mmf.schemas.manuscript import ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord
from mmf.schemas.strategy import Strategy, StrategySet
from mmf.validate.grounding import unresolved_problems
from mmf.validate.vocab import ModelClass, vocab_text

RATE_MODELS = {ModelClass.POISSON_REGRESSION, ModelClass.NEGATIVE_BINOMIAL}


def strategy_validator(gap: KnowledgeGap, sources: dict[str, DataSource]) -> Callable[[Strategy], list[str]]:
    def check(s: Strategy) -> list[str]:
        problems = unresolved_problems(s.all_refs(), sources)
        if s.gap_id != gap.id:
            problems.append(f"gap_id must be {gap.id}")
        if not s.exposures:
            problems.append("at least one exposure is required")
        for term in s.interactions:
            if len(term) < 2:
                problems.append("each interaction term needs 2+ variables")
        if s.model_class in RATE_MODELS and s.offset is None:
            problems.append(f"{s.model_class} requires an offset (denominator) variable")
        if len(s.rationale.split()) < 20:
            problems.append("rationale too short; justify design and model class and state what is not established")
        return problems

    return check


def generate_strategies(
    gaps: list[KnowledgeGap],
    decomps: list[ManuscriptDecomposition],
    sources: dict[str, DataSource],
    client: LLMClient,
    *,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[StrategySet, list[LLMCallRecord]]:
    prompt = load_prompt("d_strategy").bind(vocab=vocab_text())
    claims = {c.id: c for d in decomps for c in d.claims}
    out = StrategySet()
    records = []
    for i, gap in enumerate(gaps, start=1):
        cited = "\n".join(f"- {cid}: {claims[cid].statement}" for cid in gap.supporting_claim_ids if cid in claims)
        user = prompt.render(
            gap=gap.model_dump_json(indent=1),
            claims=cited,
            allowed_refs=allowed_refs_text(sources, with_labels=True),
            vocab=vocab_text(),
        )
        obj, rec = generate(
            client,
            prompt,
            user,
            Strategy,
            stage=f"D_strategy_{gap.id}",
            seed=seed,
            temperature=temperature,
            validators=[strategy_validator(gap, sources)],
            max_retries=max_retries,
            log_dir=log_dir,
        )
        out.strategies.append(obj.model_copy(update={"id": f"S{i}"}))
        records.append(rec)
    return out, records
