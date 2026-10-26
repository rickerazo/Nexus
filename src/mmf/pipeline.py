"""Orchestrates A -> B -> [review] -> C -> [review] -> D -> E -> report, with provenance and caching.

Run directory contract:
  manifest.json, config.yaml, sources/<id>.json, A_<manuscript>.json, B_schema.json, review_B.md,
  C_gaps.json, review_C.md, D_strategies.json, E_feasibility.json, report.md, llm_log/
A stage is recomputed only if its inputs' hash changed (or its output file is missing).
Review checkpoints: after B and C the pipeline writes review_<stage>.md and stops until the
front-matter line `approved: true` is set (edit the stage JSON first if needed).
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict, TypeVar

import yaml
from pydantic import BaseModel

from mmf import __version__
from mmf.components import a_decompose, b_schema_map, c_gaps, d_strategy, e_feasibility
from mmf.config import RunConfig, Settings
from mmf.ingest.codebook import build_datasource
from mmf.ingest.pdf import load_document, sha256_file
from mmf.llm.base import LLMClient
from mmf.llm.structured import make_client
from mmf.report.markdown import render_report, render_review
from mmf.schemas import (
    DataSource,
    FeasibilitySet,
    GapSet,
    InputRecord,
    LLMCallRecord,
    ManuscriptDecomposition,
    RunManifest,
    SchemaMap,
    StrategySet,
)

log = logging.getLogger(__name__)
M = TypeVar("M", bound=BaseModel)


class LLMKwargs(TypedDict):
    seed: int
    temperature: float
    max_retries: int
    log_dir: Path | None


class ReviewPending(Exception):  # noqa: N818 - signal, not an error
    def __init__(self, stage: str, path: Path) -> None:
        super().__init__(f"Stage {stage} awaits review: edit {path} and set 'approved: true', then re-run.")
        self.stage, self.path = stage, path


def _h(*parts: str) -> str:
    return hashlib.sha256("␟".join(parts).encode()).hexdigest()


class Run:
    def __init__(self, cfg: RunConfig, run_dir: Path | None = None, client: LLMClient | None = None) -> None:
        self.cfg = cfg
        self.settings = Settings()
        self.run_dir = run_dir or cfg.out_dir / f"{datetime.now(UTC):%Y%m%dT%H%M%S}_{cfg.sha256()[:8]}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = self.run_dir / "llm_log"
        self.client = client or make_client(
            cfg.backend,
            cfg.model,
            ollama_host=self.settings.ollama_host,
            openai_api_key=self.settings.openai_api_key,
            num_ctx=cfg.num_ctx,
        )
        self.manifest = self._load_manifest()
        (self.run_dir / "config.yaml").write_text(yaml.safe_dump(json.loads(cfg.model_dump_json()), sort_keys=False))

    # ---- provenance -----------------------------------------------------------------
    def _load_manifest(self) -> RunManifest:
        p = self.run_dir / "manifest.json"
        if p.exists():
            return RunManifest.model_validate_json(p.read_text())
        return RunManifest(
            run_id=self.run_dir.name,
            mmf_version=__version__,
            config_sha256=self.cfg.sha256(),
            backend=self.cfg.backend,
            model=self.cfg.model,
            seed=self.cfg.seed,
            temperature=self.cfg.temperature,
        )

    def _save_manifest(self) -> None:
        (self.run_dir / "manifest.json").write_text(self.manifest.model_dump_json(indent=2))

    def _record(self, records: list[LLMCallRecord]) -> None:
        self.manifest.calls.extend(records)
        self._save_manifest()

    def _cached(self, stage: str, key: str, model: type[M], filename: str) -> M | None:
        p = self.run_dir / filename
        if p.exists() and self.manifest.stage_hashes.get(stage) == key:
            log.info("%s: cache hit", stage)
            return model.model_validate_json(p.read_text())
        return None

    def _store(self, stage: str, key: str, obj: BaseModel, filename: str) -> None:
        (self.run_dir / filename).write_text(obj.model_dump_json(indent=2))
        self.manifest.stage_hashes[stage] = key
        self._save_manifest()

    def _review_gate(self, stage: str, obj: BaseModel, title: str) -> None:
        p = self.run_dir / f"review_{stage}.md"
        if p.exists():
            head = p.read_text().split("---", 2)
            if len(head) >= 3 and yaml.safe_load(head[1]).get("approved") is True:
                return
        p.write_text(render_review(stage, title, obj))
        raise ReviewPending(stage, p)

    def _llm_kwargs(self) -> LLMKwargs:
        return {
            "seed": self.cfg.seed,
            "temperature": self.cfg.temperature,
            "max_retries": self.cfg.max_retries,
            "log_dir": self.log_dir,
        }

    # ---- stages ---------------------------------------------------------------------
    def ingest_sources(self) -> dict[str, DataSource]:
        out: dict[str, DataSource] = {}
        (self.run_dir / "sources").mkdir(exist_ok=True)
        for spec in self.cfg.codebooks:
            doc = load_document(spec.path, self.cfg.cache_dir)
            self._add_input(spec.path, doc.sha256, "codebook")
            key = _h(doc.sha256, "codebook_extract", self.cfg.model, str(self.cfg.chunk_tokens))
            cached = self._cached(f"ingest_{spec.id}", key, DataSource, f"sources/{spec.id}.json")
            if cached is not None:
                out[spec.id] = cached
                continue
            ds, rejected, recs = build_datasource(
                doc, spec.id, self.client, title=spec.title, chunk_tokens=self.cfg.chunk_tokens, **self._llm_kwargs()
            )
            (self.run_dir / "sources" / f"{spec.id}.rejected.json").write_text(
                json.dumps([r.model_dump() for r in rejected], indent=2)
            )
            self._record(recs)
            self._store(f"ingest_{spec.id}", key, ds, f"sources/{spec.id}.json")
            out[spec.id] = ds
        return out

    def stage_a(self) -> list[ManuscriptDecomposition]:
        out = []
        for path in self.cfg.manuscripts:
            doc = load_document(path, self.cfg.cache_dir)
            self._add_input(path, doc.sha256, "manuscript")
            mid = path.stem.replace(" ", "_")[:40]
            key = _h(doc.sha256, "a_decompose", self.cfg.model, str(self.cfg.chunk_tokens))
            cached = self._cached(f"A_{mid}", key, ManuscriptDecomposition, f"A_{mid}.json")
            if cached is not None:
                out.append(cached)
                continue
            dec, recs = a_decompose.decompose(
                doc, mid, self.client, chunk_tokens=self.cfg.chunk_tokens, **self._llm_kwargs()
            )
            self._record(recs)
            self._store(f"A_{mid}", key, dec, f"A_{mid}.json")
            out.append(dec)
        return out

    def stage_b(self, decs: list[ManuscriptDecomposition], sources: dict[str, DataSource]) -> SchemaMap:
        key = _h(*(d.model_dump_json() for d in decs), *(s.model_dump_json() for s in sources.values()), self.cfg.model)
        cached = self._cached("B", key, SchemaMap, "B_schema.json")
        if cached is None:
            cached, recs = b_schema_map.map_schema(decs, sources, self.client, **self._llm_kwargs())
            self._record(recs)
            self._store("B", key, cached, "B_schema.json")
        self._review_gate("B", cached, "Schema map")
        return SchemaMap.model_validate_json(
            (self.run_dir / "B_schema.json").read_text()
        )  # re-read: user may have edited

    def stage_c(self, decs: list[ManuscriptDecomposition], smap: SchemaMap, sources: dict[str, DataSource]) -> GapSet:
        key = _h(*(d.model_dump_json() for d in decs), smap.model_dump_json(), self.cfg.model, str(self.cfg.n_gaps))
        cached = self._cached("C", key, GapSet, "C_gaps.json")
        if cached is None:
            cached, recs = c_gaps.find_gaps(
                decs, smap, sources, self.client, n_gaps=self.cfg.n_gaps, **self._llm_kwargs()
            )
            self._record(recs)
            self._store("C", key, cached, "C_gaps.json")
        self._review_gate("C", cached, "Knowledge gaps")
        return GapSet.model_validate_json((self.run_dir / "C_gaps.json").read_text())

    def stage_d(
        self, gaps: GapSet, decs: list[ManuscriptDecomposition], sources: dict[str, DataSource], smap: SchemaMap
    ) -> StrategySet:
        key = _h(gaps.model_dump_json(), self.cfg.model)
        cached = self._cached("D", key, StrategySet, "D_strategies.json")
        if cached is None:
            cached, recs = d_strategy.generate_strategies(
                gaps.gaps, decs, sources, self.client, smap, **self._llm_kwargs()
            )
            self._record(recs)
            self._store("D", key, cached, "D_strategies.json")
        return cached

    def stage_e(self, strategies: StrategySet, sources: dict[str, DataSource]) -> FeasibilitySet:
        key = _h(strategies.model_dump_json(), *(s.model_dump_json() for s in sources.values()), self.cfg.model)
        cached = self._cached("E", key, FeasibilitySet, "E_feasibility.json")
        if cached is None:
            cached, recs = e_feasibility.assess(strategies.strategies, sources, self.client, **self._llm_kwargs())
            self._record(recs)
            self._store("E", key, cached, "E_feasibility.json")
        return cached

    def run(self) -> Path:
        sources = self.ingest_sources()
        decs = self.stage_a()
        smap = self.stage_b(decs, sources)
        gaps = self.stage_c(decs, smap, sources)
        strategies = self.stage_d(gaps, decs, sources, smap)
        feas = self.stage_e(strategies, sources)
        report = render_report(self.manifest, decs, sources, smap, gaps, strategies, feas)
        (self.run_dir / "report.md").write_text(report)
        return self.run_dir / "report.md"

    def _add_input(self, path: Path, digest: str, role: str) -> None:
        if not any(i.sha256 == digest for i in self.manifest.inputs):
            self.manifest.inputs.append(InputRecord(path=str(path), sha256=digest, role=role))
            self._save_manifest()


def approve(run_dir: Path, stage: str) -> None:
    p = run_dir / f"review_{stage}.md"
    text = p.read_text()
    p.write_text(text.replace("approved: false", "approved: true", 1))


def manifest_for_paths(paths: list[Path]) -> dict[str, str]:
    return {str(p): sha256_file(p) for p in paths}
