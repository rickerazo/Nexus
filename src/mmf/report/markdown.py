"""Human-readable outputs. Structured JSON stays the source of truth; these are views."""

from __future__ import annotations

from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel

from mmf.schemas import DataSource, FeasibilitySet, GapSet, ManuscriptDecomposition, RunManifest, SchemaMap, StrategySet

_env = Environment(
    loader=PackageLoader("mmf.report", "templates"),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_review(stage: str, title: str, obj: BaseModel) -> str:
    return _env.get_template("review.md.j2").render(stage=stage, title=title, json=obj.model_dump_json(indent=2))


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
