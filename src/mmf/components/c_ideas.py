"""Component C redesign: C0 data inventory and C1 idea generation (see docs/plans, 2026-11-12 section).

C0 gives the gap finder a map of all documented variables, grouped into topic domains, with the ones the
manuscripts already use marked. C1 asks for candidate research questions through several lenses, sampled at a
non-zero temperature with fixed seeds, so the output is a pool to narrow down rather than the single most likely
answer. Every call is checkpointed as soon as it is accepted, so an interrupted run resumes.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from mmf.llm.base import LLMClient
from mmf.llm.prompts import Prompt, load_prompt
from mmf.llm.structured import GenerationFailedError, Salvage, generate
from mmf.schemas.dataset import DataSource, Variable
from mmf.schemas.ideas import (
    MAX_DOMAINS_PER_BLOCK,
    BlockDomains,
    Candidate,
    DataInventory,
    IdeaBatch,
    IdeaPool,
    InventoryDomain,
)
from mmf.schemas.manuscript import ClaimKind, ManuscriptDecomposition
from mmf.schemas.run import LLMCallRecord

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

INVENTORY_PROMPT, IDEAS_PROMPT = "c_inventory", "c_ideas"

# Generic on purpose: an example idea in a lens would steer every run toward it and contaminate the novelty
# measure and the B0 baseline comparison (evaluation protocol, amendments D and E).
LENSES: dict[str, str] = {
    "unused_data": (
        "Unused data. Build each question mainly on domains with no variables used by the manuscripts: "
        "measurements none of them touch."
    ),
    "tensions": (
        "Tensions. Find findings in the manuscripts that conflict with each other, are surprising, or are left "
        "unexplained, and ask what would resolve them."
    ),
    "inversion": (
        "Inversion. Ask about groups, settings or periods in which the outcome is rarer than the known risk "
        "factors predict, and what protects them."
    ),
    "mechanism": (
        "Mechanism to measurement. Take a biological or behavioural mechanism proposed in the manuscripts and ask "
        "which documented measurement could test a prediction of it that has not been tested."
    ),
    "cross_source": (
        "Cross-source. Combine what one source records with the population another source covers, and ask a "
        "question that neither source can answer alone."
    ),
    "design": (
        "Design. Ask questions that need a study design the manuscripts did not use, for example comparisons "
        "across time periods, places or changes in how events are recorded, natural experiments, or case-only "
        "designs."
    ),
}


def prompt_hashes() -> list[str]:
    return [load_prompt(name).sha256 for name in (INVENTORY_PROMPT, IDEAS_PROMPT)]


def lenses_hash(lenses: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(lenses, sort_keys=True).encode()).hexdigest()


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


def inventory_text(inv: DataInventory, sources: dict[str, DataSource], populations: dict[str, str]) -> str:
    parts = []
    for sid, src in sources.items():
        doms = [d for d in inv.domains if d.source_id == sid]
        lines = [f"## {sid}: {src.title}", f"Population: {populations.get(sid, 'not stated')}"]
        for d in doms:
            used = f"{len(d.used)} used by the manuscripts" if d.used else "none used by the manuscripts"
            lines.append(f"- {d.name} ({len(d.variables)} variables, {used}): {d.summary}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


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


def ideas_validator(n_ideas: int, source_ids: set[str]) -> Callable[[IdeaBatch], list[str]]:
    def check(b: IdeaBatch) -> list[str]:
        problems = []
        if len(b.ideas) != n_ideas:
            problems.append(f"return exactly {n_ideas} ideas, got {len(b.ideas)}")
        seen: set[str] = set()
        for i, idea in enumerate(b.ideas, start=1):
            q = " ".join(idea.question.lower().split())
            if not q or not idea.why_open.strip() or not idea.data.strip():
                problems.append(f"idea {i}: question, why_open and data must not be empty")
            if q in seen:
                problems.append(f"idea {i}: repeats an earlier idea")
            seen.add(q)
            unknown = sorted(set(idea.sources) - source_ids)
            if unknown:
                problems.append(f"idea {i}: unknown source ids {unknown}; use only {sorted(source_ids)}")
            if not idea.sources:
                problems.append(f"idea {i}: name at least one source id")
        return problems

    return check


def generate_ideas(
    decomps: list[ManuscriptDecomposition],
    inventory: str,
    sources: dict[str, DataSource],
    client: LLMClient,
    *,
    lenses: dict[str, str],
    seeds: list[int],
    n_ideas: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
    checkpoint_dir: Path | None = None,
    salt: str = "",
) -> tuple[IdeaPool, list[LLMCallRecord]]:
    """One call per (lens, seed). A call that fails after retries is recorded and skipped: one lens failing must
    not discard the rest of the pool."""
    prompt = load_prompt(IDEAS_PROMPT).bind(n_ideas=str(n_ideas))
    validator = ideas_validator(n_ideas, set(sources))
    pool, records = IdeaPool(), []
    for lens, instruction in lenses.items():
        user = prompt.render(lens=instruction, manuscripts=manuscripts_text(decomps), inventory=inventory)
        for seed in seeds:
            stage = f"C_ideas_{lens}_s{seed}"
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
                        id=f"I{len(pool.candidates) + 1}", lens=lens, seed=seed, model=client.model, **idea.model_dump()
                    )
                )
    return pool, records


def pool_markdown(pool: IdeaPool) -> str:
    lines = [f"# Candidate ideas (C1): {len(pool.candidates)} ideas", ""]
    if pool.failed_calls:
        lines += [f"Failed calls (no ideas): {', '.join(pool.failed_calls)}", ""]
    for lens in dict.fromkeys(c.lens for c in pool.candidates):
        lines += [f"## {lens}", ""]
        for c in (c for c in pool.candidates if c.lens == lens):
            lines += [
                f"**{c.id}** (seed {c.seed}, {c.model}) {c.question}",
                f"- Why open: {c.why_open}",
                f"- Data: {', '.join(c.sources)}: {c.data}",
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
