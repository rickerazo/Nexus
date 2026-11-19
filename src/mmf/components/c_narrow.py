"""Component C redesign, steps C2-C5: narrow the C1 idea pool down to a shortlist (see docs/plans, 2026-11-12).

C2 groups near-duplicate ideas by embedding similarity. C3 grounds each remaining idea in a two-turn call (free-text
reasoning, then JSON) against the variables nearest to it among every documented variable; the design checks are
code, not prompt wording. C4 scores the grounded gaps: novelty and feasibility are computed, importance is a model
rating that can only filter, and the selection rule is fixed in advance. C5 renders the shortlist for review.
"""

from __future__ import annotations

import hashlib
import logging
import re
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any, Literal

import numpy as np
from pydantic import Field, create_model

from mmf.components.b_crosscheck import QUERY_PREFIX, variable_fingerprint
from mmf.components.c_gaps import citation_problems
from mmf.components.c_ideas import DESIGNS, Design, _checkpointed, domain_label, variable_line
from mmf.components.roles import ROLE_NAMES
from mmf.config import SourceSpec
from mmf.llm.base import LLMClient
from mmf.llm.prompts import Prompt, load_primed_prompt
from mmf.llm.structured import GenerationFailedError, Salvage, reason
from mmf.schemas.dataset import DataSource, Variable, VariableRef, VariableType
from mmf.schemas.gap import KnowledgeGap
from mmf.schemas.ideas import (
    Candidate,
    DataInventory,
    DedupedPool,
    DroppedIdea,
    GapScore,
    GroundedGap,
    Grounding,
    GroundingAnswer,
    IdeaGroup,
    IdeaPool,
    ImportanceRating,
    Shortlist,
)
from mmf.schemas.manuscript import ClaimKind, ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord

log = logging.getLogger(__name__)

GROUND_PROMPT, ANSWER_PROMPT, IMPORTANCE_PROMPT = "c_ground", "c_ground_answer", "c_importance"
Vectors = Callable[[list[str]], np.ndarray]


# Part of the C3 stage key. 2: the years held never exclude an idea (no coverage check, no years-based
# not-groundable verdict, years to acquire recorded); claim ids by grammar; bookkeeping fixed on the final attempt.
# 3: more bookkeeping fixed on the final attempt (stray variables, idle sources, cited but unlisted claims).
C3_LOGIC_VERSION = "3"


def prompt_hashes() -> list[str]:
    return [load_primed_prompt(n, "").sha256 for n in (GROUND_PROMPT, ANSWER_PROMPT, IMPORTANCE_PROMPT)]


# ---- C2: dedupe -----------------------------------------------------------------------


def idea_text(c: Candidate) -> str:
    """The question only: with the comparison added, mxbai similarity follows the shared sentence template ("between
    mothers of cases and ...") more than the topic (SUID pool, 2026-11-17)."""
    return c.question


def dedupe(pool: IdeaPool, vectors: Vectors, threshold: float) -> DedupedPool:
    """Greedy, in pool order: an idea joins the first group whose representative it matches at >= threshold."""
    out = DedupedPool(threshold=threshold)
    if not pool.candidates:
        return out
    vecs = vectors([idea_text(c) for c in pool.candidates])
    reps: list[int] = []
    for i, c in enumerate(pool.candidates):
        sims = [float(vecs[i] @ vecs[r]) for r in reps]
        best = int(np.argmax(sims)) if sims else -1
        if best >= 0 and sims[best] >= threshold:
            g = out.groups[best]
            g.members.append(c.id)
            g.max_similarity = max(g.max_similarity, round(sims[best], 3))
        else:
            reps.append(i)
            out.groups.append(IdeaGroup(representative=c.id, members=[c.id], max_similarity=0.0))
    return out


# ---- C3: grounding --------------------------------------------------------------------


def var_key(sid: str, v: Variable) -> str:
    return f"{sid}:{v.name}"


def candidate_variables(
    idea: Candidate,
    inv: DataInventory,
    sources: dict[str, DataSource],
    specs: dict[str, SourceSpec],
    vectors: Vectors,
    *,
    per_source: int,
    per_domain: int,
) -> list[tuple[str, Variable]]:
    """The variables C3 may use for one idea: the nearest `per_source` of every role-bearing source, the nearest
    `per_domain` of each inventory domain the idea cites, and every reference source's survey weight. Grouped by
    source, nearest first."""
    query = vectors([QUERY_PREFIX + f"{idea.question} {idea.comparison} {idea.data}"])[0]
    chosen: dict[str, float] = {}

    def take(sid: str, vs: list[Variable], k: int) -> None:
        if not vs or k <= 0:
            return
        sims = vectors([variable_fingerprint(v) for v in vs]) @ query
        for j in np.argsort(-sims)[:k]:
            key = var_key(sid, vs[int(j)])
            chosen[key] = max(chosen.get(key, -1.0), float(sims[int(j)]))

    for sid, spec in specs.items():
        if spec.roles and sid in sources:
            take(sid, sources[sid].variables, per_source)
    cited = set(idea.domains)
    for d in inv.domains:
        if domain_label(d) in cited and d.source_id in sources:
            src = sources[d.source_id]
            take(d.source_id, [v for n in d.variables if (v := src.lookup(n)) is not None], per_domain)
    for sid, spec in specs.items():
        if "reference" in spec.roles and spec.weight_variable and sid in sources:
            w = sources[sid].lookup(spec.weight_variable)
            if w is not None:
                chosen.setdefault(var_key(sid, w), 1.0)
    out: list[tuple[str, Variable]] = []
    for sid in sources:
        keys = sorted((k for k in chosen if k.split(":", 1)[0] == sid), key=lambda k: -chosen[k])
        for k in keys:
            v = sources[sid].lookup(k.split(":", 1)[1])
            if v is not None:
                out.append((sid, v))
    return out


def variables_text(cands: list[tuple[str, Variable]]) -> str:
    return "\n".join(f"- {sid}:{variable_line(v)}" for sid, v in cands)


def claims_text(decomps: list[ManuscriptDecomposition]) -> str:
    """Every claim except methods, with its id, for prior art."""
    return "\n".join(
        f"- {c.id} [{c.kind.value}]: {c.statement}" for d in decomps for c in d.claims if c.kind != ClaimKind.METHOD
    )


def needs_text(design: Design) -> str:
    parts = [f"at least {n} {ROLE_NAMES[r]} source(s)" for r, n in design.needs.items()]
    if design.min_sources > 1:
        parts.append(f"at least {design.min_sources} different sources")
    return ", ".join(parts) or "any sources"


def answer_model(
    roles: dict[str, list[str]], var_keys: list[str], claim_ids: list[str] | None = None
) -> type[GroundingAnswer]:
    """GroundingAnswer whose source fields accept only sources with that role, whose `variables` accept only
    the candidate variables of this idea, and whose `supporting_claim_ids` accept only real claim ids (on
    2026-11-17 two ideas failed on bare ids such as `C10`)."""

    def choice(values: list[str]) -> Any:
        if not values:
            return list[str]
        return list[Literal[tuple(values)]]  # type: ignore[misc]

    fields: dict[str, Any] = {}
    for role in ROLE_NAMES:
        name = f"{role}_sources"
        allowed = sorted(sid for sid, rs in roles.items() if role in rs)
        fields[name] = (choice(allowed), Field(max_length=0) if not allowed else Field())
    fields["variables"] = (choice(var_keys), Field(description=GroundingAnswer.model_fields["variables"].description))
    if claim_ids:
        fields["supporting_claim_ids"] = (
            choice(sorted(claim_ids)),
            Field(description=GroundingAnswer.model_fields["supporting_claim_ids"].description),
        )
    return create_model("GroundingChoice", __base__=GroundingAnswer, **fields)


_NO_RATE = re.compile(r"\b(incidence|risks?)\b", re.IGNORECASE)
# A not-groundable verdict that rests on the years held. Years are a data holding, not a limitation (investigator,
# 2026-11-18): more years of every source can be acquired.
_YEARS_REASON = re.compile(
    r"\b(periods?|years?|coverage|covers?|covered|overlap\w*|time ?frames?|(19|20)\d\d)\b", re.IGNORECASE
)
YEARS_FEEDBACK = (
    "why_not refers to years or periods. The years a source holds now are not a limitation: more years of every "
    "source can be acquired. If the years are the only obstacle, set groundable to true and give the years the "
    "question needs. Otherwise state the epistemological, logical or logistical reason without referring to years"
)


def grounding_validator(
    design: Design,
    roles: dict[str, list[str]],
    specs: dict[str, SourceSpec],
    claim_ids: set[str],
    max_year: int | None = None,
) -> Callable[[GroundingAnswer], list[str]]:
    """The design checks, in code: roles the design needs, variables from the listed sources only and from each
    case and reference source, the survey weight of each reference source, a coherent period that is not in the
    future, no incidence or risk wording without a denominator, and prior art. The years a source holds are not
    checked: they never exclude an idea (see `years_to_acquire`). A not-groundable verdict must give a reason
    other than years."""
    last_year = max_year if max_year is not None else date.today().year - 1

    def check(a: GroundingAnswer) -> list[str]:
        if not a.groundable:
            if len(a.why_not.split()) < 8:
                return ["why_not must say which data or design element is missing"]
            return [YEARS_FEEDBACK] if _YEARS_REASON.search(a.why_not) else []
        problems: list[str] = []
        if not a.statement.strip():
            problems.append("statement must not be empty")
        listed = a.by_role()
        for role, ids in listed.items():
            for sid in ids:
                if role not in roles.get(sid, []):
                    problems.append(f"{sid} is listed as a {ROLE_NAMES[role]} source but does not have that role")
        for role, n in design.needs.items():
            if len(set(listed[role])) < n:
                problems.append(f"this design needs at least {n} {ROLE_NAMES[role]} source(s)")
        used = {sid for ids in listed.values() for sid in ids}
        if len(used) < design.min_sources:
            problems.append(f"this design needs at least {design.min_sources} different sources")
        by_source: dict[str, list[str]] = {}
        for key in a.variables:
            sid, name = key.split(":", 1)
            by_source.setdefault(sid, []).append(name)
            if sid not in used:
                problems.append(f"variable {key} is from {sid}, which is not listed under any role; list it or drop it")
        if not a.variables:
            problems.append("list the variables the study uses")
        for sid in sorted(set(listed["case"]) | set(listed["reference"])):
            if sid not in by_source:
                problems.append(f"{sid} is listed but none of its variables is used")
        if design.min_sources > 1 and len(by_source) < design.min_sources:
            problems.append(f"this design compares sources: use variables from at least {design.min_sources} sources")
        for sid in sorted(set(listed["reference"])):
            w = specs[sid].weight_variable if sid in specs else None
            if w and w.upper() not in {n.upper() for n in by_source.get(sid, [])}:
                problems.append(f"a prevalence from {sid} needs its survey weight: add {sid}:{w} to variables")
        if a.period_start > a.period_end:
            problems.append("period_start is after period_end")
        if a.period_end > last_year:
            problems.append(f"period_end {a.period_end} is in the future: no data exist after {last_year}")
        if "denominator" not in design.needs and _NO_RATE.search(a.statement):
            problems.append(
                "this design has no denominator source, so it cannot estimate incidence or risk: compare proportions "
                "or odds among cases"
            )
        gap = KnowledgeGap(
            id="G",
            statement=a.statement,
            rationale=a.rationale,
            prior_art=a.prior_art,
            supporting_claim_ids=a.supporting_claim_ids,
            required_concepts=a.required_concepts,
            required_variables=[],
        )
        unknown = [c for c in a.supporting_claim_ids if c not in claim_ids]
        if unknown:
            problems.append(f"unknown claim ids {unknown}")
        if len(a.prior_art.split()) < 15:
            problems.append("prior_art must name the closest tested work or say why none is close (too short)")
        problems += citation_problems(gap, claim_ids)
        return problems

    return check


def _spans(years: list[int]) -> str:
    """[2016, 2017, 2018, 2021] -> '2016-2018, 2021'."""
    spans: list[list[int]] = []
    for y in years:
        if spans and y == spans[-1][1] + 1:
            spans[-1][1] = y
        else:
            spans.append([y, y])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in spans)


def years_to_acquire(a: GroundingAnswer, specs: dict[str, SourceSpec]) -> list[str]:
    """Per listed source, the years of the period it does not hold yet. A record for the investigator, never a
    reason to exclude a gap."""
    out = []
    for sid in dict.fromkeys(sid for ids in a.by_role().values() for sid in ids):
        held = specs[sid].period if sid in specs else None
        if not held:
            continue
        missing = [y for y in range(a.period_start, a.period_end + 1) if not held[0] <= y <= held[1]]
        if missing:
            out.append(f"{sid}: {_spans(missing)} (held {held[0]}-{held[1]})")
    return out


def fix_bookkeeping(specs: dict[str, SourceSpec], claim_ids: set[str] | None = None) -> Salvage[GroundingAnswer]:
    """Final-attempt salvage for bookkeeping errors that say nothing about the idea, in this order:
    1. drop variables from sources not listed under any role;
    2. drop case or population-reference sources that contribute no variable;
    3. add the survey weight of each remaining population reference;
    4. remove supporting claims the text does not discuss (supporting claims are optional);
    5. add claims that prior_art cites but supporting_claim_ids omits (a bare `C8` only if exactly one claim
       id ends in `.C8`).
    On 2026-11-17 and 2026-11-18, 12 ideas failed on these alone. The result must still pass every check (so a
    design that loses a role it needs still fails, as it should); every fix is recorded."""
    known = claim_ids or set()

    def salvage(a: GroundingAnswer, problems: list[str]) -> tuple[GroundingAnswer, list[str]]:
        if not a.groundable:
            return a, []
        out, fixed = a.model_copy(deep=True), []
        listed = {sid for ids in out.by_role().values() for sid in ids}
        stray = [v for v in out.variables if v.split(":", 1)[0] not in listed]
        if stray:
            out.variables = [v for v in out.variables if v not in stray]
            fixed += [f"dropped variable {v} (source not listed)" for v in stray]
        used = {v.split(":", 1)[0] for v in out.variables}
        for role in ("case", "reference"):
            ids = getattr(out, f"{role}_sources")
            idle = [sid for sid in dict.fromkeys(ids) if sid not in used]
            if idle:
                setattr(out, f"{role}_sources", [sid for sid in ids if sid not in idle])
                fixed += [f"dropped {sid} as {ROLE_NAMES[role]} (no variable used)" for sid in idle]
        have = {v.upper() for v in out.variables}
        for sid in dict.fromkeys(out.reference_sources):
            w = specs[sid].weight_variable if sid in specs else None
            if w and f"{sid}:{w}".upper() not in have:
                out.variables.append(f"{sid}:{w}")
                fixed.append(f"added survey weight {sid}:{w}")
        undiscussed = {
            m.group(1) for p in problems if (m := re.match(r"supporting claim (\S+) is not discussed", p)) is not None
        }
        if undiscussed:
            out.supporting_claim_ids = [c for c in out.supporting_claim_ids if c not in undiscussed]
            fixed += [f"removed undiscussed supporting claim {c}" for c in sorted(undiscussed)]
        for p in problems:
            m = re.match(r"prior_art cites (\S+), which is not in supporting_claim_ids", p)
            if m is None:
                continue
            cited = m.group(1)
            full = [cited] if cited in known else [c for c in sorted(known) if c.endswith(f".{cited}")]
            if len(full) == 1 and full[0] not in out.supporting_claim_ids:
                out.supporting_claim_ids.append(full[0])
                fixed.append(f"added cited claim {full[0]}")
        return out, fixed

    return salvage


def ground_ideas(
    pool: IdeaPool,
    deduped: DedupedPool,
    decomps: list[ManuscriptDecomposition],
    inv: DataInventory,
    sources: dict[str, DataSource],
    specs: dict[str, SourceSpec],
    roles: dict[str, list[str]],
    source_roles: str,
    client: LLMClient,
    vectors: Vectors,
    *,
    per_source: int,
    per_domain: int,
    seed: int,
    reason_temperature: float,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    checkpoint_dir: Path | None = None,
    salt: str = "",
) -> tuple[Grounding, list[LLMCallRecord]]:
    """C3: one two-turn call per group representative. A failed call is recorded and skipped."""
    think = load_primed_prompt(GROUND_PROMPT, source_roles)
    answer = load_primed_prompt(ANSWER_PROMPT, source_roles)
    by_id = {c.id: c for c in pool.candidates}
    claims = claims_text(decomps)
    claim_ids = {c.id for d in decomps for c in d.claims}
    out, records = Grounding(), []
    for group in deduped.groups:
        idea = by_id[group.representative]
        design = DESIGNS[idea.design]
        cands = candidate_variables(idea, inv, sources, specs, vectors, per_source=per_source, per_domain=per_domain)
        user = think.render(
            idea_id=idea.id,
            design_name=idea.design,
            question=idea.question,
            comparison=idea.comparison,
            why_open=idea.why_open,
            sources="; ".join(f"{ROLE_NAMES[r]}: {', '.join(v)}" for r, v in idea.by_role().items() if v) or "none",
            data=idea.data,
            design=design.instruction,
            claims=claims,
            variables=variables_text(cands),
        )
        stage = f"C_ground_{idea.id}"
        try:
            thought, rec = _reason_checkpointed(
                client,
                think,
                user,
                stage=f"{stage}_reason",
                seed=seed,
                temperature=reason_temperature,
                log_dir=log_dir,
                checkpoint_dir=checkpoint_dir,
                salt=salt,
            )
            if rec is not None:
                records.append(rec)
            model = answer_model(roles, [var_key(s, v) for s, v in cands], sorted(claim_ids))
            ans, rec = _checkpointed(
                client,
                answer,
                answer.render(needs=needs_text(design)),
                model,
                stage=stage,
                validator=grounding_validator(design, roles, specs, claim_ids),
                salvage=fix_bookkeeping(specs, claim_ids),
                checkpoint_dir=checkpoint_dir,
                salt=salt,
                seed=seed,
                temperature=temperature,
                max_retries=max_retries,
                log_dir=log_dir,
                history=[{"role": "user", "content": user}, {"role": "assistant", "content": thought}],
            )
        except GenerationFailedError as e:
            log.warning("%s: no valid grounding after %d attempts; skipped", stage, e.attempts)
            out.failed_calls.append(stage)
            if e.record is not None:
                records.append(e.record)
            continue
        if rec is not None:
            records.append(rec)
        if not ans.groundable:
            out.dropped.append(DroppedIdea(idea_id=idea.id, reason=ans.why_not))
            continue
        out.gaps.append(
            GroundedGap(
                id=f"G{len(out.gaps) + 1}",
                statement=ans.statement,
                rationale=ans.rationale,
                prior_art=ans.prior_art,
                supporting_claim_ids=ans.supporting_claim_ids,
                required_concepts=ans.required_concepts,
                required_variables=[
                    VariableRef(source_id=k.split(":", 1)[0], name=k.split(":", 1)[1])
                    for k in dict.fromkeys(ans.variables)
                ],
                idea_id=idea.id,
                design=idea.design,
                case_sources=list(dict.fromkeys(ans.case_sources)),
                reference_sources=list(dict.fromkeys(ans.reference_sources)),
                denominator_sources=list(dict.fromkeys(ans.denominator_sources)),
                period_start=ans.period_start,
                period_end=ans.period_end,
                cannot_establish=ans.cannot_establish,
                reasoning=thought,
                years_to_acquire=years_to_acquire(ans, specs),
                salvaged=rec.dropped if rec is not None else [],
            )
        )
    return out, records


def _reason_checkpointed(
    client: LLMClient,
    prompt: Prompt,
    user: str,
    *,
    stage: str,
    seed: int,
    temperature: float,
    log_dir: Path | None,
    checkpoint_dir: Path | None,
    salt: str,
) -> tuple[str, LLMCallRecord | None]:
    ckpt = None
    if checkpoint_dir is not None:
        key = hashlib.sha256("\x00".join((salt, prompt.sha256, user, str(seed), str(temperature))).encode()).hexdigest()
        ckpt = checkpoint_dir / f"{stage}_{key[:16]}.txt"
        if ckpt.exists():
            return ckpt.read_text(), None
    text, rec = reason(client, prompt, user, stage=stage, seed=seed, temperature=temperature, log_dir=log_dir)
    if ckpt is not None:
        ckpt.parent.mkdir(parents=True, exist_ok=True)
        ckpt.write_text(text)
    return text, rec


# ---- C4: scoring and selection ---------------------------------------------------------


def novelty(
    gaps: list[GroundedGap], decomps: list[ManuscriptDecomposition], vectors: Vectors
) -> list[tuple[float, str]]:
    """1 - the highest cosine between the gap statement and any extracted claim, with that claim's id."""
    claims = [c for d in decomps for c in d.claims]
    if not gaps:
        return []
    if not claims:
        return [(1.0, "") for _ in gaps]
    g = vectors([x.statement for x in gaps])
    c = vectors([x.statement for x in claims])
    sims = g @ c.T
    return [(round(1.0 - float(sims[i].max()), 3), claims[int(sims[i].argmax())].id) for i in range(len(gaps))]


def feasibility(gap: GroundedGap, sources: dict[str, DataSource]) -> float:
    """Share of the required variables with documented levels or a known type: a variable with neither cannot be
    coded without going back to the codebook."""
    refs = gap.required_variables
    if not refs:
        return 0.0
    ok = 0
    for r in refs:
        v = sources[r.source_id].lookup(r.name) if r.source_id in sources else None
        ok += v is not None and (bool(v.levels) or v.type != VariableType.UNKNOWN)
    return round(ok / len(refs), 3)


def rate_importance(
    gaps: list[GroundedGap],
    references: list[str],
    source_roles: str,
    client: LLMClient,
    *,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    checkpoint_dir: Path | None = None,
    salt: str = "",
) -> tuple[dict[str, ImportanceRating], list[LLMCallRecord]]:
    prompt = load_primed_prompt(IMPORTANCE_PROMPT, source_roles)
    refs = "\n".join(f"- {r}" for r in references) or "(none given)"
    out: dict[str, ImportanceRating] = {}
    records = []
    for g in gaps:
        user = prompt.render(
            references=refs,
            gap_id=g.id,
            design_name=g.design,
            statement=g.statement,
            rationale=g.rationale,
            prior_art=g.prior_art,
            cannot_establish=g.cannot_establish,
        )
        try:
            r, rec = _checkpointed(
                client,
                prompt,
                user,
                ImportanceRating,
                stage=f"C_importance_{g.id}",
                validator=lambda r: [] if r.reason.strip() else ["give the reason"],
                checkpoint_dir=checkpoint_dir,
                salt=salt,
                seed=seed,
                temperature=temperature,
                max_retries=max_retries,
                log_dir=log_dir,
            )
        except GenerationFailedError as e:
            log.warning("C_importance_%s: no valid rating; treated as unrated", g.id)
            if e.record is not None:
                records.append(e.record)
            continue
        if rec is not None:
            records.append(rec)
        out[g.id] = r
    return out, records


SELECTION_RULE = (
    "Gaps rated below the minimum importance (or unrated) are filtered out. The rest are ranked by novelty x "
    "feasibility, highest first; a gap whose statement is at least the maximum similarity to one already shortlisted "
    "is skipped; selection stops at the shortlist size."
)


def shortlist(
    gaps: list[GroundedGap],
    sources: dict[str, DataSource],
    decomps: list[ManuscriptDecomposition],
    ratings: dict[str, ImportanceRating],
    vectors: Vectors,
    *,
    size: int,
    min_importance: int,
    max_similarity: float,
) -> Shortlist:
    nov = novelty(gaps, decomps, vectors)
    scores = []
    for g, (n, nearest) in zip(gaps, nov, strict=True):
        f = feasibility(g, sources)
        r = ratings.get(g.id)
        scores.append(
            GapScore(
                gap_id=g.id,
                idea_id=g.idea_id,
                design=g.design,
                novelty=n,
                nearest_claim=nearest,
                feasibility=f,
                importance=r.importance if r else 0,
                importance_reason=r.reason if r else "not rated (call failed)",
                score=round(n * f, 4),
            )
        )
    vecs = vectors([g.statement for g in gaps]) if gaps else np.zeros((0, 1))
    index = {g.id: i for i, g in enumerate(gaps)}
    picked: list[int] = []
    for s in sorted(scores, key=lambda s: (-s.score, int(s.gap_id[1:]))):
        if s.importance < min_importance:
            s.skipped_reason = f"importance {s.importance} < {min_importance}"
            continue
        if len(picked) >= size:
            s.skipped_reason = "shortlist full"
            continue
        i = index[s.gap_id]
        close = [gaps[j].id for j in picked if float(vecs[i] @ vecs[j]) >= max_similarity]
        if close:
            s.skipped_reason = f"too similar to {close[0]}"
            continue
        s.shortlisted = True
        picked.append(i)
    rule = f"{SELECTION_RULE} (size {size}, minimum importance {min_importance}, maximum similarity {max_similarity})"
    return Shortlist(scores=scores, rule=rule)


# ---- C5: review -----------------------------------------------------------------------


def review_markdown(pool: IdeaPool, deduped: DedupedPool, grounding: Grounding, sl: Shortlist) -> str:
    gaps = {g.id: g for g in grounding.gaps}
    ideas = {c.id: c for c in pool.candidates}
    short = sorted((s for s in sl.scores if s.shortlisted), key=lambda s: -s.score)
    lines = [
        "# C shortlist for review",
        "",
        f"{len(pool.candidates)} ideas → {len(deduped.groups)} after deduplication (cosine ≥ {deduped.threshold}) → "
        f"{len(grounding.gaps)} grounded, {len(grounding.dropped)} judged not groundable, "
        f"{len(grounding.failed_calls)} failed → {len(short)} shortlisted.",
        "",
        f"Selection rule: {sl.rule}",
        "",
        "Pick 5 by ticking the boxes below.",
        "",
    ]
    for s in short:
        g = gaps[s.gap_id]
        roles = "; ".join(
            f"{ROLE_NAMES[r]}: {', '.join(v)}"
            for r, v in (
                ("case", g.case_sources),
                ("reference", g.reference_sources),
                ("denominator", g.denominator_sources),
            )
            if v
        )
        lines += [
            f"## [ ] {g.id} ({g.design}, from {g.idea_id}) {g.statement}",
            "",
            f"- Scores: novelty {s.novelty:.2f} (nearest claim {s.nearest_claim}), feasibility {s.feasibility:.2f}, "
            f"importance {s.importance}: {s.importance_reason}",
            f"- Sources: {roles}; period {g.period_start}-{g.period_end}",
            f"- Variables: {', '.join(f'{v.source_id}:{v.name}' for v in g.required_variables)}",
            f"- Rationale: {g.rationale}",
            f"- Prior art: {g.prior_art}",
            f"- Cannot establish: {g.cannot_establish}",
            f"- Original idea: {ideas[g.idea_id].question if g.idea_id in ideas else ''}",
            *([f"- Years to acquire (not held yet): {'; '.join(g.years_to_acquire)}"] if g.years_to_acquire else []),
            *([f"- Fixed in code on the final attempt: {'; '.join(g.salvaged)}"] if g.salvaged else []),
            "",
            "<details><summary>Reasoning turn</summary>",
            "",
            g.reasoning,
            "",
            "</details>",
            "",
        ]
    lines += ["## Not shortlisted", ""]
    for s in sorted((s for s in sl.scores if not s.shortlisted), key=lambda s: -s.score):
        lines.append(
            f"- {s.gap_id} ({s.design}) {gaps[s.gap_id].statement} — novelty {s.novelty:.2f}, feasibility "
            f"{s.feasibility:.2f}, importance {s.importance}; {s.skipped_reason}"
            + (
                f"; years to acquire: {'; '.join(gaps[s.gap_id].years_to_acquire)}"
                if gaps[s.gap_id].years_to_acquire
                else ""
            )
        )
    if grounding.dropped:
        lines += ["", "## Judged not groundable by C3", ""]
        lines += [
            f"- {d.idea_id}: {ideas[d.idea_id].question if d.idea_id in ideas else ''} — {d.reason}"
            for d in grounding.dropped
        ]
    if grounding.failed_calls:
        lines += ["", f"Failed grounding calls: {', '.join(grounding.failed_calls)}"]
    merged = [g for g in deduped.groups if len(g.members) > 1]
    if merged:
        lines += ["", "## Merged near-duplicates (C2)", ""]
        lines += [
            f"- {g.representative} ← {', '.join(g.members[1:])} (max cosine {g.max_similarity:.2f})" for g in merged
        ]
    return "\n".join(lines) + "\n"
