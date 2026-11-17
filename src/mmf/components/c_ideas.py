"""Component C redesign: C0 data inventory and C1 idea generation (see docs/plans, 2026-11-12 section).

C0 gives the gap finder a map of all documented variables, grouped into topic domains, with the ones the
manuscripts already use marked. C1 asks for candidate research questions through six designs built on the source
roles (case series, population reference, denominator), sampled at a non-zero temperature with fixed seeds, so the
output is a pool to narrow down rather than the single most likely answer. Every call is checkpointed as soon as it is accepted, so an interrupted run resumes.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import numpy as np
from pydantic import BaseModel

from mmf.components.roles import ROLE_NAMES
from mmf.llm.base import LLMClient
from mmf.llm.prompts import Prompt, load_primed_prompt, load_prompt
from mmf.llm.structured import GenerationFailedError, Salvage, generate
from mmf.schemas.dataset import DataSource, Variable
from mmf.schemas.ideas import (
    MAX_DOMAINS_PER_BLOCK,
    BlockDomains,
    Candidate,
    DataInventory,
    DomainMatch,
    IdeaBatch,
    IdeaPool,
    InventoryDomain,
)
from mmf.schemas.manuscript import ClaimKind, ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

INVENTORY_PROMPT, IDEAS_PROMPT = "c_inventory", "c_ideas"

# One C1 call per (design, seed). The designs come from the source roles (investigator, 2026-11-16): the leverage
# is in combining case series, population reference and denominator sources. Generic on purpose: an example idea
# would steer every run toward it and contaminate the novelty measure and the B0 baseline (protocol amendments D, E).


class Design(BaseModel):
    instruction: str
    needs: dict[str, int]  # role -> minimum number of sources in that role
    min_sources: int = 1


DESIGNS: dict[str, Design] = {
    "case_population": Design(
        instruction=(
            "Case-population comparison. Compare how common an exposure is among the cases (from a case series) "
            "with its weighted prevalence in the general population (from a population reference source). The "
            "concept must be measured in both; say how its measurement differs between them."
        ),
        needs={"case": 1, "reference": 1},
    ),
    "exposure_rates": Design(
        instruction=(
            "Exposure-specific rates. Estimate outcome rates by exposure group by combining the cases from a case "
            "series (numerator), the exposure prevalence from a population reference source, and the population "
            "at risk from a denominator source."
        ),
        needs={"case": 1, "reference": 1, "denominator": 1},
    ),
    "case_case": Design(
        instruction=(
            "Case-case comparison. Compare the cases of the outcome with cases of other outcomes recorded in the "
            "same case series, to find what is specific to the outcome rather than to every event in the series."
        ),
        needs={"case": 1},
    ),
    "case_only": Design(
        instruction=(
            "Case-only analysis. Study how the circumstances recorded for the cases vary across subgroups or "
            "across age, within the case series and without a population comparison."
        ),
        needs={"case": 1},
    ),
    "trends": Design(
        instruction=(
            "Trends within cases. Compare proportions among the cases across periods. When a case series' "
            "coverage changes over time, changes in case counts are not changes in incidence."
        ),
        needs={"case": 1},
    ),
    "measurement": Design(
        instruction=(
            "Measurement comparison. Compare how the same concept is recorded in two or more sources (wording, "
            "timing, who reports it, how missing answers are coded) and ask how the difference would bias a "
            "comparison between them."
        ),
        needs={},
        min_sources=2,
    ),
}


def inventory_prompt_hash() -> str:
    return load_prompt(INVENTORY_PROMPT).sha256


def ideas_prompt_hash() -> str:
    return load_primed_prompt(IDEAS_PROMPT, "").sha256


def designs_hash(designs: dict[str, Design]) -> str:
    return hashlib.sha256(
        json.dumps({k: v.model_dump() for k, v in designs.items()}, sort_keys=True).encode()
    ).hexdigest()


# ---- C0: data inventory ---------------------------------------------------------------


def blocks(source: DataSource, max_vars: int) -> list[list[Variable]]:
    """Consecutive runs of at most `max_vars` variables, in document order (codebook sections are contiguous)."""
    vs = source.variables
    return [vs[i : i + max_vars] for i in range(0, len(vs), max_vars)]


def variable_line(v: Variable, max_levels: int = 4) -> str:
    line = f"{v.name}: {v.label}"
    if v.levels:
        shown = "; ".join(v.levels[:max_levels]) + (" …" if len(v.levels) > max_levels else "")
        line += f" [{shown}]"
    return line


def block_validator(block: list[Variable]) -> Callable[[BlockDomains], list[str]]:
    index = {v.name: i for i, v in enumerate(block)}

    def check(b: BlockDomains) -> list[str]:
        problems = []
        if not b.domains:
            return ["return at least one domain"]
        if len(b.domains) > MAX_DOMAINS_PER_BLOCK:
            problems.append(f"return at most {MAX_DOMAINS_PER_BLOCK} domains")
        last = -1
        for d in b.domains:
            if d.start not in index:
                problems.append(f"domain {d.name!r}: start {d.start!r} is not a variable name in this block")
                continue
            if index[d.start] <= last:
                problems.append(
                    f"domain {d.name!r}: start {d.start!r} is variable {index[d.start] + 1} of the list, not after the "
                    f"previous domain's start (variable {last + 1}); domains must follow the list order, and names "
                    "that differ only in case or suffix are different variables"
                )
            last = max(last, index[d.start])
            if not d.name.strip() or not d.summary.strip():
                problems.append(f"domain starting at {d.start!r}: name and summary must not be empty")
        if b.domains[0].start != block[0].name:
            problems.append(f"the first domain must start at the block's first variable, {block[0].name!r}")
        return problems

    return check


def drop_misplaced_domains(block: list[Variable]) -> Salvage[BlockDomains]:
    """Final-attempt fallback: drop domains whose start is unknown or out of order. Their variables fall into the
    previous domain, so coverage stays complete; only a topic boundary is lost. Recorded as dropped."""
    index = {v.name: i for i, v in enumerate(block)}

    def salvage(b: BlockDomains, problems: list[str]) -> tuple[BlockDomains, list[str]]:
        kept, dropped, last = [], [], -1
        for d in b.domains:
            if d.start in index and index[d.start] > last:
                kept.append(d)
                last = index[d.start]
            else:
                dropped.append(f"domain {d.name!r} (start {d.start!r})")
        return BlockDomains(domains=kept), dropped

    return salvage


def domains_from_block(sid: str, block: list[Variable], out: BlockDomains, used: set[str]) -> list[InventoryDomain]:
    """Each domain spans from its start to the next domain's start, so every variable lands in exactly one."""
    index = {v.name: i for i, v in enumerate(block)}
    starts = [index[d.start] for d in out.domains] + [len(block)]
    result = []
    for d, a, b in zip(out.domains, starts, starts[1:], strict=False):
        names = [v.name for v in block[a:b]]
        result.append(
            InventoryDomain(
                source_id=sid,
                name=d.name.strip(),
                summary=d.summary.strip(),
                variables=names,
                used=[n for n in names if f"{sid}:{n.upper()}" in used],
            )
        )
    return result


def build_inventory(
    sources: dict[str, DataSource],
    used: set[str],
    client: LLMClient,
    *,
    populations: dict[str, str],
    block_vars: int,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    checkpoint_dir: Path | None = None,
    salt: str = "",
) -> tuple[DataInventory, list[LLMCallRecord]]:
    """One call per block of `block_vars` variables. `used` holds keys 'source_id:NAME' mapped in B."""
    prompt = load_prompt(INVENTORY_PROMPT)
    inv, records = DataInventory(), []
    for sid, src in sources.items():
        for bi, block in enumerate(blocks(src, block_vars)):
            user = prompt.render(
                source_id=sid,
                title=src.title,
                population=populations.get(sid, "not stated"),
                variables="\n".join(variable_line(v) for v in block),
            )
            out, rec = _checkpointed(
                client,
                prompt,
                user,
                BlockDomains,
                stage=f"C_inventory_{sid}_{bi}",
                validator=block_validator(block),
                salvage=drop_misplaced_domains(block),
                checkpoint_dir=checkpoint_dir,
                salt=salt,
                seed=seed,
                temperature=temperature,
                max_retries=max_retries,
                log_dir=log_dir,
            )
            if rec is not None:
                records.append(rec)
            inv.domains += domains_from_block(sid, block, out, used)
    return inv, records


def domain_label(d: InventoryDomain) -> str:
    return f"{d.source_id} / {d.name}"


def new_domain_labels(inv: DataInventory) -> set[str]:
    """Labels whose domains contain no variable the manuscripts use (every same-named domain in that source)."""
    used = {domain_label(d) for d in inv.domains if d.used}
    return {domain_label(d) for d in inv.domains} - used


def inventory_text(inv: DataInventory, sources: dict[str, DataSource], roles: dict[str, list[str]]) -> str:
    """Domains per source, headed by the source's roles (described in full in the primer). Each line starts with
    the exact label ideas must cite; NEW marks domains no manuscript uses."""
    new = new_domain_labels(inv)
    parts = []
    for sid, src in sources.items():
        role = " and ".join(ROLE_NAMES[r] for r in roles.get(sid, [])) or "lookup list, no role"
        lines = [f"## {sid}: {src.title} ({role})"]
        for d in (d for d in inv.domains if d.source_id == sid):
            label = domain_label(d)
            tag = "NEW, " if label in new else ""
            used = f"{len(d.used)} used by the manuscripts" if d.used else "none used by the manuscripts"
            lines.append(f"- {label} [{tag}{len(d.variables)} variables, {used}]: {d.summary}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def match_domains(
    inv: DataInventory, roles: dict[str, list[str]], vectors: Callable[[list[str]], np.ndarray], threshold: float
) -> list[DomainMatch]:
    """For each case-series domain, the most similar population-reference domain at or above `threshold`."""
    case = [d for d in inv.domains if "case" in roles.get(d.source_id, [])]
    ref = [d for d in inv.domains if "reference" in roles.get(d.source_id, [])]
    if not case or not ref:
        return []
    vecs = vectors([f"{d.name}: {d.summary}" for d in (*case, *ref)])
    sims = vecs[: len(case)] @ vecs[len(case) :].T
    new = new_domain_labels(inv)
    out: dict[tuple[str, str], DomainMatch] = {}
    for i, d in enumerate(case):
        j = int(np.argmax(sims[i]))
        if sims[i, j] < threshold:
            continue
        pair = (domain_label(d), domain_label(ref[j]))
        score = round(float(sims[i, j]), 3)
        if pair not in out or out[pair].score < score:
            out[pair] = DomainMatch(
                case=pair[0], reference=pair[1], score=score, case_new=pair[0] in new, reference_new=pair[1] in new
            )
    # both sides unused by the manuscripts first: the comparisons nobody has made
    return sorted(out.values(), key=lambda m: (-(m.case_new + m.reference_new), -m.score))


def domain_matches_text(matches: list[DomainMatch]) -> str:
    lines = []
    for m in matches:
        tags = [t for t, on in (("case domain NEW", m.case_new), ("reference domain NEW", m.reference_new)) if on]
        suffix = "; " + ", ".join(tags) if tags else ""
        lines.append(f"- {m.case} <-> {m.reference} (similarity {m.score:.2f}{suffix})")
    return "\n".join(lines) or "(no matching domains)"


# ---- C1: idea generation --------------------------------------------------------------


def manuscripts_text(decomps: list[ManuscriptDecomposition]) -> str:
    """What has been studied: questions, findings, limitations, future work and the variables used (no quotes)."""
    kinds = (ClaimKind.FINDING, ClaimKind.HYPOTHESIS, ClaimKind.LIMITATION, ClaimKind.FUTURE_WORK)
    parts = []
    for d in decomps:
        lines = [f"## {d.title}"]
        lines += [f"Question: {q}" for q in d.research_questions]
        lines += [f"- {c.kind.value}: {c.statement}" for c in d.claims if c.kind in kinds]
        if d.variables:
            lines.append("Variables used: " + "; ".join(sorted({f"{v.concept} ({v.role.value})" for v in d.variables})))
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def ideas_validator(
    n_ideas: int,
    design: Design,
    roles: dict[str, list[str]],
    labels: set[str] | None = None,
    new: set[str] | None = None,
    min_new: int = 0,
) -> Callable[[IdeaBatch], list[str]]:
    """Each source must be listed under a role it has, each idea must have the roles its design needs, its domains
    must be inventory labels from its sources, and at least `min_new` ideas must use a domain no manuscript uses.
    `labels=None` skips the domain checks."""
    new_labels = new or set()

    def check(b: IdeaBatch) -> list[str]:
        problems = []
        n_new = 0
        if len(b.ideas) != n_ideas:
            problems.append(f"return exactly {n_ideas} ideas, got {len(b.ideas)}")
        seen: set[str] = set()
        for i, idea in enumerate(b.ideas, start=1):
            q = " ".join(idea.question.lower().split())
            if not q or not idea.why_open.strip() or not idea.data.strip() or not idea.comparison.strip():
                problems.append(f"idea {i}: question, comparison, why_open and data must not be empty")
            if q in seen:
                problems.append(f"idea {i}: repeats an earlier idea")
            seen.add(q)
            listed = idea.by_role()
            for role, ids in listed.items():
                for sid in ids:
                    if sid not in roles:
                        problems.append(f"idea {i}: unknown source id {sid!r}; use only {sorted(roles)}")
                    elif role not in roles[sid]:
                        has = " and ".join(ROLE_NAMES[r] for r in roles[sid]) or "no role"
                        problems.append(
                            f"idea {i}: {sid} is listed as a {ROLE_NAMES[role]} source but its role is {has}"
                        )
            for role, n in design.needs.items():
                if len([sid for sid in listed[role] if role in roles.get(sid, [])]) < n:
                    problems.append(f"idea {i}: this design needs at least {n} {ROLE_NAMES[role]} source(s)")
            if len({sid for ids in listed.values() for sid in ids}) < design.min_sources:
                problems.append(f"idea {i}: this design needs at least {design.min_sources} different sources")
            if labels is None:
                continue
            if not idea.domains:
                problems.append(f"idea {i}: list the inventory domains it uses in `domains`")
            named = {sid for ids in listed.values() for sid in ids}
            for label in idea.domains:
                if label not in labels:
                    problems.append(
                        f"idea {i}: domain {label!r} is not in the inventory; copy labels exactly as 'source_id / "
                        "domain name'"
                    )
                elif label.split(" / ", 1)[0] not in named:
                    problems.append(f"idea {i}: domain {label!r} belongs to a source not listed under any role")
            if any(label in new_labels for label in idea.domains):
                n_new += 1
        if labels is not None and n_new < min_new:
            problems.append(
                f"only {n_new} idea(s) use a domain marked NEW; at least {min_new} must be built mainly on domains "
                "no manuscript uses"
            )
        return problems

    return check


def generate_ideas(
    decomps: list[ManuscriptDecomposition],
    inv: DataInventory,
    sources: dict[str, DataSource],
    cross_role: str,
    matches: str,
    source_roles: str,
    roles: dict[str, list[str]],
    client: LLMClient,
    *,
    designs: dict[str, Design],
    seeds: list[int],
    n_ideas: int,
    min_new: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    checkpoint_dir: Path | None = None,
    salt: str = "",
) -> tuple[IdeaPool, list[LLMCallRecord]]:
    """One call per (design, seed), with the scientific primer and source roles as the system message. A call that
    fails after retries is recorded and skipped: one design failing must not discard the rest of the pool."""
    prompt = load_primed_prompt(IDEAS_PROMPT, source_roles).bind(n_ideas=str(n_ideas), min_new=str(min_new))
    labels = {domain_label(d) for d in inv.domains}
    new = new_domain_labels(inv)
    inventory = inventory_text(inv, sources, roles)
    pool, records = IdeaPool(), []
    for name, design in designs.items():
        validator = ideas_validator(n_ideas, design, roles, labels, new, min_new)
        user = prompt.render(
            design=design.instruction,
            manuscripts=manuscripts_text(decomps),
            cross_role=cross_role,
            matches=matches,
            inventory=inventory,
        )
        for seed in seeds:
            stage = f"C_ideas_{name}_s{seed}"
            try:
                out, rec = _checkpointed(
                    client,
                    prompt,
                    user,
                    IdeaBatch,
                    stage=stage,
                    validator=validator,
                    checkpoint_dir=checkpoint_dir,
                    salt=salt,
                    seed=seed,
                    temperature=temperature,
                    max_retries=max_retries,
                    log_dir=log_dir,
                )
            except GenerationFailedError as e:
                log.warning("%s: no valid ideas after %d attempts; skipped", stage, e.attempts)
                pool.failed_calls.append(stage)
                if e.record is not None:
                    records.append(e.record)
                continue
            if rec is not None:
                records.append(rec)
            for idea in out.ideas:
                pool.candidates.append(
                    Candidate(
                        id=f"I{len(pool.candidates) + 1}",
                        design=name,
                        seed=seed,
                        model=client.model,
                        **idea.model_dump(),
                    )
                )
    return pool, records


def pool_markdown(pool: IdeaPool) -> str:
    lines = [f"# Candidate ideas (C1): {len(pool.candidates)} ideas", ""]
    if pool.failed_calls:
        lines += [f"Failed calls (no ideas): {', '.join(pool.failed_calls)}", ""]
    for design in dict.fromkeys(c.design for c in pool.candidates):
        lines += [f"## {design}", ""]
        for c in (c for c in pool.candidates if c.design == design):
            roles = "; ".join(f"{ROLE_NAMES[r]}: {', '.join(v)}" for r, v in c.by_role().items() if v)
            lines += [
                f"**{c.id}** (seed {c.seed}, {c.model}) {c.question}",
                f"- Comparison: {c.comparison}",
                f"- Why open: {c.why_open}",
                f"- Sources: {roles}",
                f"- Domains: {'; '.join(c.domains)}",
                f"- Data: {c.data}",
                "",
            ]
    return "\n".join(lines)


# ---- shared ---------------------------------------------------------------------------


def _checkpointed(
    client: LLMClient,
    prompt: Prompt,
    user: str,
    model: type[T],
    *,
    stage: str,
    validator: Callable[[T], list[str]],
    salvage: Salvage[T] | None = None,
    checkpoint_dir: Path | None,
    salt: str,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[T, LLMCallRecord | None]:
    """generate() with a per-call checkpoint keyed by salt, prompt, rendered input, schema and seed. Returns
    (output, record); the record is None for a call resumed from its checkpoint."""
    ckpt = None
    if checkpoint_dir is not None:
        schema = json.dumps(model.model_json_schema(), sort_keys=True)
        key = hashlib.sha256(
            "\x00".join((salt, prompt.sha256, user, schema, str(seed), str(temperature))).encode()
        ).hexdigest()
        ckpt = checkpoint_dir / f"{stage}_{key[:16]}.json"
        if ckpt.exists():
            obj = model.model_validate_json(ckpt.read_text())
            if not validator(obj):
                return obj, None
    obj, rec = generate(
        client,
        prompt,
        user,
        model,
        stage=stage,
        seed=seed,
        temperature=temperature,
        validators=[validator],
        max_retries=max_retries,
        log_dir=log_dir,
        salvage=salvage,
    )
    if ckpt is not None:
        ckpt.parent.mkdir(parents=True, exist_ok=True)
        ckpt.write_text(obj.model_dump_json(indent=1))
    return obj, rec
