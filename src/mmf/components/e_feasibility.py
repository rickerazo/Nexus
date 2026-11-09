"""Component E: deterministic feasibility checks, plus LLM-written caveats from documentation."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from mmf.llm.base import LLMClient
from mmf.llm.prompts import load_prompt
from mmf.llm.structured import generate
from mmf.schemas.dataset import DataSource
from mmf.schemas.feasibility import FeasibilityReport, FeasibilitySet
from mmf.schemas.run import LLMCallRecord
from mmf.schemas.strategy import Strategy
from mmf.validate.grounding import resolve_refs

PROMPTS = ("e_caveats",)


def prompt_hashes() -> list[str]:
    """sha256 of every prompt this component uses; part of the stage cache key."""
    return [load_prompt(name).sha256 for name in PROMPTS]


class _Caveats(BaseModel):
    caveats: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


def deterministic_report(s: Strategy, sources: dict[str, DataSource]) -> FeasibilityReport:
    res = resolve_refs(s.all_refs(), sources)
    blockers = [r.note for r in res if not r.resolved]
    notes: list[str] = []
    used_sources = {r.ref.source_id for r in res}
    if len(used_sources) > 1:
        notes.append(
            f"Strategy spans sources {sorted(used_sources)}; requires record linkage or a harmonized pooled design."
        )
    years = [set(r.variable.years) for r in res if r.resolved and r.variable and r.variable.years]
    if len(years) > 1 and not set.intersection(*years):
        blockers.append("No common year/phase across the documented availability of the required variables.")
    return FeasibilityReport(strategy_id=s.id, resolutions=res, blockers=blockers, cross_source_notes=notes)


def assess(
    strategies: list[Strategy],
    sources: dict[str, DataSource],
    client: LLMClient | None,
    *,
    seed: int,
    temperature: float,
    max_retries: int,
    log_dir: Path | None,
) -> tuple[FeasibilitySet, list[LLMCallRecord]]:
    out = FeasibilitySet()
    records: list[LLMCallRecord] = []
    prompt = load_prompt("e_caveats") if client else None
    for s in strategies:
        rep = deterministic_report(s, sources)
        if client and prompt and rep.feasible:
            defs = "\n".join(
                f"- ({r.ref.source_id}, {r.ref.name}): {r.variable.model_dump_json()}"
                for r in rep.resolutions
                if r.variable
            )
            user = prompt.render(strategy=s.model_dump_json(indent=1), definitions=defs)
            cav, rec = generate(
                client,
                prompt,
                user,
                _Caveats,
                stage=f"E_caveats_{s.id}",
                seed=seed,
                temperature=temperature,
                max_retries=max_retries,
                log_dir=log_dir,
            )
            rep.caveats.extend(cav.caveats)
            rep.blockers.extend(cav.blockers)
            records.append(rec)
        out.reports.append(rep)
    return out, records
