"""Component D: one Strategy per gap, every variable resolvable, vocab-constrained."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mmf.components.common import allowed_refs_text
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource, SchemaMap
from mmf.schemas.gap import KnowledgeGap
from mmf.schemas.manuscript import ManuscriptDecomposition, VariableRole
from mmf.schemas.run import LLMCallRecord
from mmf.schemas.strategy import Strategy, StrategySet
from mmf.validate.grounding import unresolved_problems
from mmf.validate.vocab import ModelClass, vocab_text

RATE_MODELS = {ModelClass.POISSON_REGRESSION, ModelClass.NEGATIVE_BINOMIAL}
TIME_MODELS = {ModelClass.COX_PROPORTIONAL_HAZARDS, ModelClass.TIME_STRATIFIED}


def strategy_validator(
    gap: KnowledgeGap, sources: dict[str, DataSource], outcome_refs: set[str] | None = None
) -> Callable[[Strategy], list[str]]:
    """`outcome_refs`: keys of variables mapped from outcome-role concepts (Component B). If given and
    non-empty, the strategy's outcome must be one of them."""

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
        if s.model_class in TIME_MODELS and s.time_scale is None:
            problems.append(f"{s.model_class} requires a time_scale variable (the time axis, e.g. age at death)")
        out_key = s.outcome.variable.key()
        non_outcome = {
            r.key()
            for r in [*s.exposures, *s.covariates, *s.stratification, *(t for term in s.interactions for t in term)]
        }
        if out_key in non_outcome:
            problems.append(
                f"outcome {s.outcome.variable.name} also appears as exposure/covariate/interaction; the outcome must be a distinct event variable"
            )
        if outcome_refs and out_key not in outcome_refs:
            problems.append(f"outcome must be a variable mapped from an outcome concept: one of {sorted(outcome_refs)}")
        if len(s.rationale.split()) < 20:
            problems.append("rationale too short; justify design and model class and state what is not established")
        return problems

    return check


def outcome_variable_keys(decomps: list[ManuscriptDecomposition], schema_map: SchemaMap) -> set[str]:
    concepts = {v.concept.lower() for d in decomps for v in d.variables if v.role == VariableRole.OUTCOME}
    return {
        f"{m.source_id}:{m.variable.upper()}"
        for m in schema_map.mappings
        if m.variable and m.concept.lower() in concepts
    }


def generate_strategies(
    gaps: list[KnowledgeGap],
    decomps: list[ManuscriptDecomposition],
    sources: dict[str, DataSource],
    client: LLMClient,
    schema_map: SchemaMap | None = None,
    *,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[StrategySet, list[LLMCallRecord]]:
    prompt = load_prompt("d_strategy").bind(vocab=vocab_text())
    claims = {c.id: c for d in decomps for c in d.claims}
    outcome_refs = outcome_variable_keys(decomps, schema_map) if schema_map else set()
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
            validators=[strategy_validator(gap, sources, outcome_refs)],
            max_retries=max_retries,
            log_dir=log_dir,
        )
        out.strategies.append(obj.model_copy(update={"id": f"S{i}"}))
        records.append(rec)
    return out, records
