"""Score MMF and Biomni gaps with the same code checks and measures, and write a blinded rater sheet.

Run with the MMF venv:
  .venv/bin/python benchmarks/biomni/score.py configs/suid.yaml BENCH_DIR MMF_RUN_DIR

Reads MMF's shortlist (C_shortlist.json + C_grounding.json in MMF_RUN_DIR) and every BENCH_DIR/biomni_seed*/answer.json.
Writes to BENCH_DIR: scores.csv (one row per gap), report.md (per-run summary), rater_sheet.md and rater_sheet.csv
(blinded: random codes, one template, no arm or run) and blinding_key.csv (keep closed until rating is done).

The checks are those MMF's C3 enforces, applied after the fact to both arms. Neither arm is excluded for failing
them: a failure is a measured outcome.
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np

from mmf.components import roles as roles_mod
from mmf.components.b_crosscheck import VectorCache
from mmf.components.c_narrow import _NO_RATE
from mmf.config import RunConfig, SourceSpec
from mmf.llm.ollama import OllamaEmbedder
from mmf.schemas.dataset import DataSource, VariableType
from mmf.schemas.manuscript import ManuscriptDecomposition

TOP = 10
ROLE_FIELDS = ("case_sources", "reference_sources", "denominator_sources")
ROLE_OF = {"case_sources": "case", "reference_sources": "reference", "denominator_sources": "denominator"}


@dataclass
class Gap:
    arm: str
    run: str
    rank: int
    statement: str
    design: str = ""
    rationale: str = ""
    prior_art: str = ""
    case_sources: list[str] = field(default_factory=list)
    reference_sources: list[str] = field(default_factory=list)
    denominator_sources: list[str] = field(default_factory=list)
    period_start: int | None = None
    period_end: int | None = None
    variables: list[str] = field(default_factory=list)
    cannot_establish: str = ""


def _list(x: object) -> list[str]:
    if isinstance(x, list):
        return [str(v) for v in x]
    return [str(x)] if x else []


def _int(x: object) -> int | None:
    try:
        return int(str(x)[:4])
    except (TypeError, ValueError):
        return None


def load_mmf(run_dir: Path) -> list[Gap]:
    sl = json.loads((run_dir / "C_shortlist.json").read_text())
    gaps = {g["id"]: g for g in json.loads((run_dir / "C_grounding.json").read_text())["gaps"]}
    picked = sorted((s for s in sl["scores"] if s["shortlisted"]), key=lambda s: -s["score"])[:TOP]
    out = []
    for i, s in enumerate(picked, 1):
        g = gaps[s["gap_id"]]
        out.append(
            Gap(
                arm="mmf",
                run=run_dir.name,
                rank=i,
                statement=g["statement"],
                design=g["design"],
                rationale=g["rationale"],
                prior_art=g["prior_art"],
                case_sources=g["case_sources"],
                reference_sources=g["reference_sources"],
                denominator_sources=g["denominator_sources"],
                period_start=g["period_start"],
                period_end=g["period_end"],
                variables=[f"{v['source_id']}:{v['name']}" for v in g["required_variables"]],
                cannot_establish=g["cannot_establish"],
            )
        )
    return out


def load_biomni(seed_dir: Path) -> tuple[list[Gap], str]:
    f = seed_dir / "answer.json"
    if not f.exists():
        return [], "no answer.json"
    try:
        data = json.loads(f.read_text())
    except json.JSONDecodeError as e:
        return [], f"answer.json is not valid JSON: {e}"
    items = data.get("gaps", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        return [], "answer.json has no list of gaps"
    out = []
    for i, d in enumerate(x for x in items if isinstance(x, dict)):
        out.append(
            Gap(
                arm="biomni",
                run=seed_dir.name,
                rank=_int(d.get("rank")) or i + 1,
                statement=str(d.get("statement", "")),
                design=str(d.get("design", "")),
                rationale=str(d.get("rationale", "")),
                prior_art=str(d.get("prior_art", "")),
                case_sources=_list(d.get("case_sources")),
                reference_sources=_list(d.get("reference_sources")),
                denominator_sources=_list(d.get("denominator_sources")),
                period_start=_int(d.get("period_start")),
                period_end=_int(d.get("period_end")),
                variables=_list(d.get("variables")),
                cannot_establish=str(d.get("cannot_establish", "")),
            )
        )
    out.sort(key=lambda g: g.rank)
    return out[:TOP], f"{len(items)} gaps returned"


def checks(g: Gap, sources: dict[str, DataSource], specs: dict[str, SourceSpec], last_year: int) -> dict[str, Any]:
    role_errors = []
    for f in ROLE_FIELDS:
        for sid in getattr(g, f):
            spec = specs.get(sid)
            if spec is None:
                role_errors.append(f"{sid}: unknown source")
            elif ROLE_OF[f] not in spec.roles:
                role_errors.append(f"{sid} listed as {ROLE_OF[f]}")
    listed = {sid for f in ROLE_FIELDS for sid in getattr(g, f)}
    unknown, unlisted, known = [], [], []
    for key in g.variables:
        sid, _, name = key.partition(":")
        v = sources[sid].lookup(name) if sid in sources and name else None
        if v is None:
            unknown.append(key)
            continue
        known.append(v)
        if sid not in listed:
            unlisted.append(key)
    weight_missing = []
    for sid in g.reference_sources:
        w = specs[sid].weight_variable if sid in specs else None
        if w and f"{sid}:{w}".upper() not in {k.upper() for k in g.variables}:
            weight_missing.append(sid)
    ps, pe = g.period_start, g.period_end
    period_ok = ps is not None and pe is not None and ps <= pe <= last_year
    years = []
    if period_ok and ps is not None and pe is not None:  # repeated for mypy narrowing
        for sid in dict.fromkeys(s for f in ROLE_FIELDS for s in getattr(g, f)):
            held = specs[sid].period if sid in specs else None
            if held and (ps < held[0] or pe > held[1]):
                years.append(f"{sid} (held {held[0]}-{held[1]})")
    n = len(g.variables)
    return {
        "n_variables": n,
        "unknown_variables": len(unknown),
        "unknown_list": "; ".join(unknown),
        "variables_from_unlisted_sources": len(unlisted),
        "role_errors": "; ".join(role_errors),
        "weight_missing": "; ".join(weight_missing),
        "rate_without_denominator": bool(_NO_RATE.search(g.statement)) and not g.denominator_sources,
        "period_ok": period_ok,
        "years_to_acquire": "; ".join(years),
        "feasibility": round(sum(bool(v.levels) or v.type != VariableType.UNKNOWN for v in known) / n if n else 0.0, 3),
        "all_checks_pass": not (unknown or unlisted or role_errors or weight_missing)
        and period_ok
        and not (bool(_NO_RATE.search(g.statement)) and not g.denominator_sources)
        and n > 0,
    }


def main(config: str, bench: str, mmf_run: str) -> None:
    cfg = RunConfig.from_yaml(config)
    bench_dir, mmf_dir = Path(bench), Path(mmf_run)
    sources = {
        s.id: DataSource.model_validate_json((mmf_dir / "sources" / f"{s.id}.json").read_text()) for s in cfg.codebooks
    }
    specs = roles_mod.specs_by_id(cfg.codebooks, sources)
    decomps = [ManuscriptDecomposition.model_validate_json(p.read_text()) for p in sorted(mmf_dir.glob("A_*.json"))]
    claims = [c for d in decomps for c in d.claims]
    vectors = VectorCache(OllamaEmbedder(cfg.embed_model), cfg.cache_dir.parent / "embeddings").vectors
    claim_vecs = vectors([c.statement for c in claims])
    last_year = date.today().year - 1

    runs: list[tuple[str, str, list[Gap], str]] = [("mmf", mmf_dir.name, load_mmf(mmf_dir), "shortlist")]
    for d in sorted(bench_dir.glob("biomni_seed*")):
        gaps, note = load_biomni(d)
        summ = json.loads((d / "summary.json").read_text()) if (d / "summary.json").exists() else {}
        runs.append(("biomni", d.name, gaps, f"{note}; {summ.get('status', '')}; {summ.get('minutes', '?')} min"))

    rows: list[dict[str, Any]] = []
    report = [
        "# MMF vs Biomni: code checks",
        "",
        f"Top {TOP} gaps per run. Same checks and measures for both arms.",
        "",
    ]
    report += [
        "| Arm | Run | Gaps | All checks pass | Unknown variables | Role errors | Weight missing | Rate w/o denom."
        " | Novelty (mean) | Feasibility (mean) | Max pairwise cosine | Note |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for arm, run, gaps, note in runs:
        if not gaps:
            report.append(f"| {arm} | {run} | 0 | | | | | | | | | {note} |")
            continue
        gv = vectors([g.statement for g in gaps])
        sims = gv @ claim_vecs.T
        pair = gv @ gv.T
        np.fill_diagonal(pair, -1)
        res = []
        for i, g in enumerate(gaps):
            c = checks(g, sources, specs, last_year)
            c["novelty"] = round(1 - float(sims[i].max()), 3)
            c["nearest_claim"] = claims[int(sims[i].argmax())].id
            res.append(c)
            rows.append(
                {**{k: v for k, v in asdict(g).items() if k != "variables"}, "variables": "; ".join(g.variables), **c}
            )
        n_vars = sum(int(c["n_variables"]) for c in res)
        report.append(
            f"| {arm} | {run} | {len(gaps)} | {sum(bool(c['all_checks_pass']) for c in res)} "
            f"| {sum(int(c['unknown_variables']) for c in res)}/{n_vars} "
            f"| {sum(bool(c['role_errors']) for c in res)} | {sum(bool(c['weight_missing']) for c in res)} "
            f"| {sum(bool(c['rate_without_denominator']) for c in res)} "
            f"| {np.mean([c['novelty'] for c in res]):.2f} | {np.mean([c['feasibility'] for c in res]):.2f} "
            f"| {pair.max() if len(gaps) > 1 else 0:.2f} | {note} |"
        )
    with (bench_dir / "scores.csv").open("w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    (bench_dir / "report.md").write_text("\n".join(report) + "\n")

    # blinded rater sheet: one template, random order and codes, no arm, run, rank or scores
    rng = random.Random(20261118)
    items = [r for r in rows]
    rng.shuffle(items)
    codes = rng.sample(range(100, 1000), len(items))
    sheet = [
        "# Blinded rater sheet",
        "",
        "Rate each question with the rubric in docs/plans/2026-11-18-biomni-benchmark.md.",
        "",
    ]
    key, csv_rows = [], []
    for code, r in zip(codes, items, strict=True):
        roles = "; ".join(
            f"{ROLE_OF[f]}: {r[f] if isinstance(r[f], str) else ', '.join(r[f])}" for f in ROLE_FIELDS if r[f]
        )
        sheet += [
            f"## Q{code}",
            "",
            f"- **Question:** {r['statement']}",
            f"- **Sources:** {roles}; years {r['period_start']}–{r['period_end']}",
            f"- **Variables:** {r['variables']}",
            f"- **Rationale:** {r['rationale']}",
            f"- **Prior art:** {r['prior_art']}",
            f"- **Cannot establish:** {r['cannot_establish']}",
            "",
        ]
        key.append({"blind_code": f"Q{code}", "arm": r["arm"], "run": r["run"], "rank": r["rank"]})
        csv_rows.append({"blind_code": f"Q{code}"})
    (bench_dir / "rater_sheet.md").write_text(re.sub(r"\n{3,}", "\n\n", "\n".join(sheet)) + "\n")
    with (bench_dir / "rater_sheet.csv").open("w", newline="") as f:
        cols = ["blind_code", "rater", "feasibility", "coherence", "novelty", "importance", "interpretability"]
        w = csv.DictWriter(f, fieldnames=[*cols, "pubmed_queries", "comment"])
        w.writeheader()
        w.writerows(csv_rows)
    with (bench_dir / "blinding_key.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["blind_code", "arm", "run", "rank"])
        w.writeheader()
        w.writerows(key)
    print("\n".join(report))


if __name__ == "__main__":
    main(*sys.argv[1:])
