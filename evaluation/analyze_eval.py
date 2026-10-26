"""Compute pre-specified evaluation metrics from run directories (see docs/evaluation_protocol.md).

Usage:
    uv run python evaluation/analyze_eval.py runs/evalL_* --label L
    uv run python evaluation/analyze_eval.py runs/evalL_* runs/evalO_* --label L --label O --rater-sheets evaluation/ratings/*.csv

Metrics 1 (grounding) and 2 (reproducibility) need only manifests and stage JSON.
Metric 4 (rubric) needs rater sheets in the `rater_sheet_template.csv` format.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def grounding(run_dirs: list[Path]) -> dict[str, float]:
    calls = [c for rd in run_dirs for c in json.loads((rd / "manifest.json").read_text())["calls"]]
    if not calls:
        return {}
    first_try = sum(c["attempts"] == 1 and c["ok"] for c in calls)
    return {
        "n_calls": len(calls),
        "accepted_first_attempt": first_try / len(calls),
        "accepted_within_retries": sum(c["ok"] for c in calls) / len(calls),
        "mean_attempts": statistics.mean(c["attempts"] for c in calls),
    }


def _strategy_signatures(rd: Path) -> list[tuple[str, frozenset[str]]]:
    p = rd / "D_strategies.json"
    if not p.exists():
        return []
    out = []
    for s in json.loads(p.read_text())["strategies"]:
        refs = {
            f"{r['source_id']}:{r['name']}"
            for r in [s["outcome"]["variable"], *s["exposures"], *s["covariates"], *s["stratification"]]
        }
        for term in s["interactions"]:
            refs |= {f"{r['source_id']}:{r['name']}" for r in term}
        out.append((f"{s['design']}|{s['model_class']}", frozenset(refs)))
    return out


def _gap_tokens(rd: Path) -> list[frozenset[str]]:
    p = rd / "C_gaps.json"
    if not p.exists():
        return []
    return [frozenset(re.findall(r"[a-z]{4,}", g["statement"].lower())) for g in json.loads(p.read_text())["gaps"]]


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def reproducibility(run_dirs: list[Path]) -> dict[str, float]:
    """Pairwise agreement across repeats, strategies matched by position (gap order)."""
    design_matches, ref_j, gap_j = [], [], []
    for a, b in combinations(run_dirs, 2):
        sa, sb = _strategy_signatures(a), _strategy_signatures(b)
        for (da, ra), (db, rb) in zip(sa, sb, strict=False):
            design_matches.append(da == db)
            ref_j.append(jaccard(ra, rb))
        for ga, gb in zip(_gap_tokens(a), _gap_tokens(b), strict=False):
            gap_j.append(jaccard(ga, gb))
    if not design_matches:
        return {}
    return {
        "n_pairs": len(list(combinations(run_dirs, 2))),
        "design_model_exact_match": statistics.mean(design_matches),
        "variable_set_jaccard_mean": statistics.mean(ref_j),
        "variable_set_jaccard_min": min(ref_j),
        "gap_statement_jaccard_mean": statistics.mean(gap_j) if gap_j else float("nan"),
    }


def rubric(sheets: list[Path]) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    by_rater: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
    dims = ["feasibility", "alignment", "novelty", "interpretability"]
    for sheet in sheets:
        with sheet.open() as f:
            for row in csv.DictReader(f):
                for d in dims:
                    if row.get(d):
                        scores[row["blind_code"]][d].append(int(row[d]))
                        by_rater[row["rater"]][row["blind_code"]] = {k: int(row[k]) for k in dims if row.get(k)}
    out: dict[str, dict[str, float]] = {
        "means": {
            d: statistics.mean(v for s in scores.values() for v in s[d])
            for d in dims
            if any(s[d] for s in scores.values())
        }
    }
    raters = list(by_rater)
    if len(raters) == 2:
        out["weighted_kappa"] = {
            d: _qw_kappa(
                [by_rater[raters[0]][c][d] for c in scores if c in by_rater[raters[0]] and c in by_rater[raters[1]]],
                [by_rater[raters[1]][c][d] for c in scores if c in by_rater[raters[0]] and c in by_rater[raters[1]]],
            )
            for d in dims
        }
    return out


def _qw_kappa(a: list[int], b: list[int], k: int = 5) -> float:
    """Quadratic-weighted Cohen's kappa for 1..k ordinal ratings."""
    n = len(a)
    if n == 0:
        return float("nan")
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b, strict=True):
        obs[x - 1][y - 1] += 1
    ha = [sum(obs[i][j] for j in range(k)) for i in range(k)]
    hb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * obs[i][j] / n
            den += w * ha[i] * hb[j] / n**2
    return 1 - num / den if den else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument(
        "--label", action="append", default=[], help="Condition label per group (groups split by label count)."
    )
    ap.add_argument("--rater-sheets", nargs="*", type=Path, default=[])
    args = ap.parse_args()
    groups = {args.label[0] if args.label else "all": args.run_dirs}
    result = {
        lbl: {"grounding": grounding(rds), "reproducibility": reproducibility(rds)} for lbl, rds in groups.items()
    }
    if args.rater_sheets:
        result["rubric"] = rubric(args.rater_sheets)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
