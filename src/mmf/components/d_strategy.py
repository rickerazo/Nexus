"""Component D: one Strategy per gap, every variable resolvable, vocab-constrained."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from mmf.components.common import allowed_refs_text, mapped_keys
from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource, SchemaMap
from mmf.schemas.gap import KnowledgeGap
from mmf.schemas.manuscript import ManuscriptDecomposition, VariableRole
from mmf.schemas.run import LLMCallRecord
from mmf.schemas.strategy import DERIVED, Strategy, StrategySet
from mmf.validate.grounding import unresolved_problems
from mmf.validate.vocab import ModelClass, vocab_text

PROMPTS = ("d_strategy",)


def prompt_hashes() -> list[str]:
    """sha256 of every prompt this component uses; part of the stage cache key."""
    return [load_prompt(name).sha256 for name in PROMPTS]


RATE_MODELS = {ModelClass.POISSON_REGRESSION, ModelClass.NEGATIVE_BINOMIAL}
TIME_MODELS = {ModelClass.COX_PROPORTIONAL_HAZARDS, ModelClass.TIME_STRATIFIED}


def strategy_validator(
    gap: KnowledgeGap,
    sources: dict[str, DataSource],
    outcome_refs: set[str] | None = None,
    denominator_sources: set[str] | None = None,
) -> Callable[[Strategy], list[str]]:
    """`outcome_refs`: keys of variables mapped from outcome-role concepts (Component B). If given and
    non-empty, the strategy's outcome must be one of them. `denominator_sources`: sources the run config marks
    as the population at risk; a rate model may use one of them instead of an offset variable."""
    denoms = denominator_sources or set()

    def check(s: Strategy) -> list[str]:
        problems = unresolved_problems([r for r in s.all_refs() if r.source_id != DERIVED], sources)
        problems += derived_problems(s)
        if s.gap_id != gap.id:
            problems.append(f"gap_id must be {gap.id}")
        if not s.exposures:
            problems.append("at least one exposure is required")
        for term in s.interactions:
            if len(term) < 2:
                problems.append("each interaction term needs 2+ variables")
        if s.denominator_source is not None and s.denominator_source not in denoms:
            problems.append(
                f"denominator_source {s.denominator_source!r} is not a denominator source; "
                f"use one of {sorted(denoms)} or null"
            )
        if s.model_class in RATE_MODELS and s.offset is None and s.denominator_source not in denoms:
            options = f" or a denominator_source (one of {sorted(denoms)})" if denoms else ""
            problems.append(f"{s.model_class} requires an offset (denominator) variable{options}")
        if s.model_class in TIME_MODELS and s.time_scale is None:
            problems.append(f"{s.model_class} requires a time_scale variable (the time axis, e.g. age at death)")
        out_key = s.outcome.variable.key()
        name = s.outcome.variable.name
        predictors = {r.key() for r in [*s.exposures, *s.covariates]}
        by_subtype = {r.key() for r in [*s.stratification, *(t for term in s.interactions for t in term)]}
        if out_key in predictors:
            problems.append(
                f"outcome {name} also appears as an exposure or covariate; the outcome must be a distinct event variable"
            )
        if out_key in by_subtype and len(s.outcome.subtypes) < 2:
            problems.append(
                f"outcome {name} appears in stratification or an interaction; that is allowed only to analyse outcome "
                "subtypes, listed in outcome.subtypes (2+ codes or levels)"
            )
        if outcome_refs and out_key not in outcome_refs:
            problems.append(f"outcome must be a variable mapped from an outcome concept: one of {sorted(outcome_refs)}")
        if not s.expected_direction.strip():
            problems.append("expected_direction is empty; state what result would support or refute the gap")
        if len(s.rationale.split()) < 20:
            problems.append("rationale too short; justify design and model class and state what is not established")
        return problems

    return check


def clear_unused_subtypes(s: Strategy) -> tuple[Strategy, list[str]]:
    """Subtypes listed while the outcome variable is in no stratification or interaction have no effect, but the
    report would claim subtype-specific analyses. The model lists the codes that define the outcome there (smoke runs,
    2026-11-11, 3 of 4 attempts), so they are cleared and recorded instead of failing the strategy."""
    used = {r.key() for r in [*s.stratification, *(t for term in s.interactions for t in term)]}
    if not s.outcome.subtypes or s.outcome.variable.key() in used:
        return s, []
    note = f"{s.gap_id}: outcome.subtypes {s.outcome.subtypes} cleared (outcome not stratified or in an interaction)"
    return s.model_copy(update={"outcome": s.outcome.model_copy(update={"subtypes": []})}), [note]


_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_FUNCTIONS = {"floor", "ceil", "round", "min", "max", "abs", "log", "exp", "and", "or", "not", "if", "else"}


def derived_problems(s: Strategy) -> list[str]:
    """Derived variables must be computable from one source and must be what the strategy actually uses.
    Added 2026-11-11: without them D could not name postconceptional age and used age at death in its place."""
    problems = []
    names = [d.name.upper() for d in s.derived]
    for dup in sorted({n for n in names if names.count(n) > 1}):
        problems.append(f"derived variable {dup} is declared more than once")
    outcome = s.outcome.variable.key()
    for d in s.derived:
        label = f"derived variable {d.name}"
        if not d.inputs:
            problems.append(f"{label} lists no inputs")
            continue
        if any(i.source_id == DERIVED for i in d.inputs):
            problems.append(f"{label}: inputs must be documented variables, not other derived variables")
        srcs = sorted({i.source_id for i in d.inputs})
        if len(srcs) > 1:
            problems.append(
                f"{label} combines sources {srcs}; inputs must come from one source (records are not linked across "
                "sources)"
            )
        inputs = {i.name.upper() for i in d.inputs}
        tokens = {t.upper() for t in _TOKEN.findall(d.formula) if t.lower() not in _FUNCTIONS}
        for t in sorted(tokens - inputs):
            problems.append(f"{label}: formula uses {t}, which is not in its inputs")
        for t in sorted(inputs - tokens):
            problems.append(f"{label}: input {t} does not appear in the formula")
        if outcome in {i.key() for i in d.inputs}:
            used_as_predictor = any(
                r.source_id == DERIVED and r.name.upper() == d.name.upper() for r in [*s.exposures, *s.covariates]
            )
            if used_as_predictor:
                problems.append(f"{label} is computed from the outcome and cannot be an exposure or covariate")
    used = {r.name.upper() for r in s.used_refs() if r.source_id == DERIVED}
    if s.outcome.variable.source_id == DERIVED:
        problems.append("the outcome must be a documented event variable, not a derived variable")
    for u in sorted(used - set(names)):
        problems.append(f"derived:{u} is used but not declared in `derived`")
    for n in sorted(set(names) - used):
        problems.append(
            f"derived variable {n} is declared but not used; to use it, put "
            f'{{"source_id": "{DERIVED}", "name": "{n}"}} in exposures, covariates, stratification, an interaction or '
            "time_scale (in place of the variables it is computed from), or remove it from `derived`"
        )
    return problems


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
    denominator_sources: set[str] | None = None,
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
            allowed_refs=allowed_refs_text(
                sources, with_labels=True, only=(mapped_keys(schema_map) if schema_map else None) or None
            ),
            vocab=vocab_text(),
            denominator_sources=", ".join(sorted(denominator_sources or ())) or "none",
        )
        obj, rec = generate(
            client,
            prompt,
            user,
            Strategy,
            stage=f"D_strategy_{gap.id}",
            seed=seed,
            temperature=temperature,
            validators=[strategy_validator(gap, sources, outcome_refs, denominator_sources)],
            max_retries=max_retries,
            log_dir=log_dir,
        )
        obj, notes = clear_unused_subtypes(obj)
        out.strategies.append(obj.model_copy(update={"id": f"S{i}"}))
        records.append(rec.model_copy(update={"normalized": notes}) if notes else rec)
    return out, records
