"""Human-readable outputs. Structured JSON stays the source of truth; these are views."""

from __future__ import annotations

from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel

from mmf.schemas import (
    DataSource,
    FeasibilitySet,
    GapSet,
    ManuscriptDecomposition,
    RunManifest,
    SchemaCheck,
    SchemaMap,
    StrategySet,
)

_env = Environment(
    loader=PackageLoader("mmf.report", "templates"),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_review(stage: str, title: str, obj: BaseModel, check: SchemaCheck | None = None) -> str:
    flagged = []
    if check is not None:
        order = {"llm_outside_topk": 0, "possible_miss": 1}
        flagged = sorted(
            (r for r in check.records if r.verdict in order),
            key=lambda r: (order[r.verdict], r.source_id, r.concept),
        )
    return _env.get_template("review.md.j2").render(
        stage=stage, title=title, json=obj.model_dump_json(indent=2), check=check, flagged=flagged
    )


def render_report(
    manifest: RunManifest,
    decs: list[ManuscriptDecomposition],
    sources: dict[str, DataSource],
    smap: SchemaMap,
    gaps: GapSet,
    strategies: StrategySet,
    feas: FeasibilitySet,
) -> str:
    feas_by_id = {r.strategy_id: r for r in feas.reports}
    return _env.get_template("report.md.j2").render(
        m=manifest,
        decs=decs,
        sources=sources,
        smap=smap,
        gaps=gaps.gaps,
        strategies=strategies.strategies,
        feas=feas_by_id,
    )
