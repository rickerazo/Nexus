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
from mmf.components import (
    a_decompose,
    b_crosscheck,
    b_schema_map,
    c_gaps,
    c_ideas,
    c_narrow,
    d_strategy,
    e_feasibility,
    roles,
)
from mmf.components.common import mapped_keys
from mmf.config import RunConfig, Settings, SourceSpec
from mmf.ingest.audit import audit_codebook
from mmf.ingest.codebook import PARSER_VERSION, build_datasource
from mmf.ingest.pdf import Document, load_document, sha256_file
from mmf.llm.base import Embedder, LLMClient
from mmf.llm.structured import GenerationFailedError, StageInputError, make_client
from mmf.report.markdown import render_report, render_review
from mmf.schemas import (
    DataSource,
    FeasibilitySet,
    GapSet,
    InputRecord,
    LLMCallRecord,
    ManuscriptDecomposition,
    RunManifest,
    SchemaCheck,
    SchemaMap,
    Strategy,
    StrategySet,
)
from mmf.schemas.ideas import DataInventory, Grounding, GroundingAnswer, IdeaBatch, IdeaPool, Shortlist

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
    def __init__(
        self,
        cfg: RunConfig,
        run_dir: Path | None = None,
        client: LLMClient | None = None,
        embedder: Embedder | None = None,
    ) -> None:
        self.cfg = cfg
        self._embedder = embedder
        self.settings = Settings()
        self.run_dir = run_dir or cfg.out_dir / f"{datetime.now(UTC):%Y%m%dT%H%M%S}_{cfg.sha256()[:8]}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = self.run_dir / "llm_log"
        self.client = client or make_client(
            cfg.backend,
            cfg.model,
            ollama_host=self.settings.ollama_host,
            num_ctx=cfg.num_ctx,
            max_output_tokens=cfg.max_output_tokens,
            allow_cloud=cfg.allow_cloud,
            api_key=self.settings.api_key,
            api_base_url=self.settings.api_base_url,
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
            allow_cloud=self.cfg.allow_cloud,
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

    def _reset_review(self, stage: str) -> None:
        """A regenerated stage needs a new review: an approval given for earlier output must not carry over."""
        p = self.run_dir / f"review_{stage}.md"
        if p.exists():
            p.unlink()
            self._warn(f"{stage} was regenerated; its earlier review approval was cleared")

    def _review_gate(self, stage: str, obj: BaseModel, title: str, check: SchemaCheck | None = None) -> None:
        p = self.run_dir / f"review_{stage}.md"
        if p.exists():
            head = p.read_text().split("---", 2)
            if len(head) >= 3 and yaml.safe_load(head[1]).get("approved") is True:
                return
        p.write_text(render_review(stage, title, obj, check))
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
            key = _h(doc.sha256, "codebook_extract", PARSER_VERSION, self.cfg.model, str(self.cfg.chunk_tokens))
            ds = self._cached(f"ingest_{spec.id}", key, DataSource, f"sources/{spec.id}.json")
            if ds is None:
                ds = self._ingest(spec, doc, key)
            self._audit(spec.id, doc, ds)  # on cache hits too, so an incomplete parse can never reach B
            out[spec.id] = ds
        return out

    def _ingest(self, spec: SourceSpec, doc: Document, key: str) -> DataSource:
        ds, rejected, recs = build_datasource(
            doc,
            spec.id,
            self.client if spec.llm_extract else None,
            title=spec.title,
            chunk_tokens=self.cfg.chunk_tokens,
            **self._llm_kwargs(),
        )
        (self.run_dir / "sources" / f"{spec.id}.rejected.json").write_text(
            json.dumps([r.model_dump() for r in rejected], indent=2)
        )
        self._record(recs)
        self._store(f"ingest_{spec.id}", key, ds, f"sources/{spec.id}.json")
        return ds

    def _audit(self, sid: str, doc: Document, ds: DataSource) -> None:
        """Independent ingestion audit (`mmf.ingest.audit`). Writes sources/<id>.audit.json; stops the run if a
        documented field header has no extracted variable; records unexplained identifiers as a warning."""
        audit = audit_codebook(doc, ds)
        path = self.run_dir / "sources" / f"{sid}.audit.json"
        path.write_text(audit.model_dump_json(indent=2))
        if audit.census:
            self._warn(
                f"ingest_{sid}: {len(audit.census)} identifier(s) in the codebook are not extracted variables; see {path}"
            )
        if audit.unmatched_anchors:
            shown = "; ".join(f"p{a.page} {a.position} {a.text!r}" for a in audit.unmatched_anchors[:10])
            raise StageInputError(
                f"ingest_{sid}",
                [
                    f"{len(audit.unmatched_anchors)} field header(s) without exactly one extracted variable: {shown}",
                    f"see {path}",
                ],
            )

    def _warn(self, w: str) -> None:
        log.warning("%s", w)
        if w not in self.manifest.warnings:
            self.manifest.warnings.append(w)
        self._save_manifest()

    def stage_a(self) -> list[ManuscriptDecomposition]:
        out = []
        for path in self.cfg.manuscripts:
            doc = load_document(path, self.cfg.cache_dir)
            self._add_input(path, doc.sha256, "manuscript")
            mid = path.stem.replace(" ", "_")[:40]
            key = _h(
                doc.sha256,
                *a_decompose.prompt_hashes(),
                self.cfg.model,
                str(self.cfg.chunk_tokens),
                str(self.cfg.max_output_tokens),
            )
            dec = self._cached(f"A_{mid}", key, ManuscriptDecomposition, f"A_{mid}.json")
            if dec is None:
                dec, recs = a_decompose.decompose(
                    doc, mid, self.client, chunk_tokens=self.cfg.chunk_tokens, **self._llm_kwargs()
                )
                self._record(recs)
                self._store(f"A_{mid}", key, dec, f"A_{mid}.json")
            # checked on cache hits too, so an unusable decomposition can never reach B
            errors, warnings = a_decompose.decomposition_problems(dec)
            for w in warnings:
                log.warning("A_%s: %s", mid, w)
                if w not in self.manifest.warnings:
                    self.manifest.warnings.append(w)
            self._save_manifest()
            if errors:
                raise StageInputError(f"A_{mid}", [*errors, f"inspect {self.run_dir / f'A_{mid}.json'}"])
            out.append(dec)
        return out

    def stage_b(self, decs: list[ManuscriptDecomposition], sources: dict[str, DataSource]) -> SchemaMap:
        key = _h(
            *(d.model_dump_json() for d in decs),
            *(s.model_dump_json() for s in sources.values()),
            *b_schema_map.prompt_hashes(),
            self.cfg.model,
            str(self.cfg.b_max_vars_per_call),
            str(self.cfg.b_max_mappings_per_call),
        )
        cached = self._cached("B", key, SchemaMap, "B_schema.json")
        if cached is None:
            cached, recs, warnings = b_schema_map.map_schema(
                decs,
                sources,
                self.client,
                max_vars_per_call=self.cfg.b_max_vars_per_call,
                max_mappings_per_call=self.cfg.b_max_mappings_per_call,
                checkpoint_dir=self.run_dir / "checkpoints" / "B",
                salt=_h(self.cfg.model, str(self.cfg.seed), str(self.cfg.temperature), str(self.cfg.num_ctx)),
                **self._llm_kwargs(),
            )
            for w in warnings:
                log.warning("B: %s", w)
                if w not in self.manifest.warnings:
                    self.manifest.warnings.append(w)
            self._record(recs)
            self._store("B", key, cached, "B_schema.json")
            self._reset_review("B")
        smap = SchemaMap.model_validate_json((self.run_dir / "B_schema.json").read_text())  # user may have edited
        check = self.stage_b_check(smap, decs, sources) if self.cfg.b_crosscheck else None
        self._review_gate("B", smap, "Schema map", check)
        return smap

    def embedder(self) -> Embedder:
        if self._embedder is None:
            from mmf.llm.ollama import OllamaEmbedder  # local only; there is no cloud embedder

            self._embedder = OllamaEmbedder(self.cfg.embed_model, host=self.settings.ollama_host)
        return self._embedder

    def stage_b_check(
        self, smap: SchemaMap, decs: list[ManuscriptDecomposition], sources: dict[str, DataSource]
    ) -> SchemaCheck:
        """Embedding cross-check of B (flags only). Its own cache entry, so it never touches B's."""
        emb = self.embedder()
        key = _h(
            smap.model_dump_json(),
            *(d.model_dump_json() for d in decs),
            *(s.model_dump_json() for s in sources.values()),
            emb.model,
            emb.model_digest() or "",
            b_crosscheck.FINGERPRINT_VERSION,
            str(self.cfg.b_check_top_k),
            str(self.cfg.b_check_miss_threshold),
        )
        check = self._cached("B_check", key, SchemaCheck, "B_check.json")
        if check is None:
            check = b_crosscheck.check_schema(
                smap,
                decs,
                sources,
                emb,
                top_k=self.cfg.b_check_top_k,
                miss_threshold=self.cfg.b_check_miss_threshold,
                cache_dir=self.cfg.cache_dir.parent / "embeddings",
            )
            self._store("B_check", key, check, "B_check.json")
        counts = check.counts()
        flagged = counts.get("llm_outside_topk", 0) + counts.get("possible_miss", 0)
        if flagged:
            self._warn(f"B_check: {flagged} (concept, source) pair(s) where embeddings and the LLM disagree; {counts}")
        return check

    def stage_c(self, decs: list[ManuscriptDecomposition], smap: SchemaMap, sources: dict[str, DataSource]) -> GapSet:
        populations = {c.id: c.population for c in self.cfg.codebooks if c.id in sources and c.population}
        key = _h(
            *(d.model_dump_json() for d in decs),
            smap.model_dump_json(),
            *c_gaps.prompt_hashes(),
            self.cfg.model,
            str(self.cfg.n_gaps),
            json.dumps(populations, sort_keys=True),
        )
        cached = self._cached("C", key, GapSet, "C_gaps.json")
        if cached is None:
            cached, recs = c_gaps.find_gaps(
                decs,
                smap,
                sources,
                self.client,
                n_gaps=self.cfg.n_gaps,
                populations=populations,
                **self._llm_kwargs(),
            )
            self._record(recs)
            self._store("C", key, cached, "C_gaps.json")
            self._reset_review("C")
        self._review_gate("C", cached, "Knowledge gaps")
        return GapSet.model_validate_json((self.run_dir / "C_gaps.json").read_text())

    def populations(self, sources: dict[str, DataSource]) -> dict[str, str]:
        return {c.id: c.population for c in self.cfg.codebooks if c.id in sources and c.population}

    def stage_c_inventory(self, sources: dict[str, DataSource], smap: SchemaMap) -> DataInventory:
        """C0: every documented variable grouped into topic domains, marking those B mapped to manuscript concepts."""
        pops = self.populations(sources)
        used = mapped_keys(smap)
        key = _h(
            *(s.model_dump_json() for s in sources.values()),
            json.dumps(sorted(used)),
            json.dumps(pops, sort_keys=True),
            c_ideas.inventory_prompt_hash(),
            self.cfg.model,
            str(self.cfg.c_inventory_block_vars),
        )
        inv = self._cached("C_inventory", key, DataInventory, "C_inventory.json")
        if inv is None:
            inv, recs = c_ideas.build_inventory(
                sources,
                used,
                self.client,
                populations=pops,
                block_vars=self.cfg.c_inventory_block_vars,
                checkpoint_dir=self.run_dir / "checkpoints" / "C_inventory",
                salt=_h(self.cfg.model, str(self.cfg.num_ctx)),
                **self._llm_kwargs(),
            )
            self._record(recs)
            self._store("C_inventory", key, inv, "C_inventory.json")
        return inv

    def source_roles(self, sources: dict[str, DataSource]) -> str:
        problems = roles.role_problems(self.cfg.codebooks, sources)
        if problems:
            raise StageInputError("roles", problems)
        return roles.source_roles_text(self.cfg.codebooks, sources)

    def stage_c_ideas(
        self,
        decs: list[ManuscriptDecomposition],
        sources: dict[str, DataSource],
        smap: SchemaMap,
        inv: DataInventory,
    ) -> IdeaPool:
        """C1: candidate questions from each role-based design and seed, sampled at `c_ideation_temperature`."""
        model = self.cfg.c_ideation_model or self.cfg.model
        client = self.client if model == self.cfg.model else self._client_for(model)
        role_map = {s.id: [str(r) for r in s.roles] for s in self.cfg.codebooks if s.id in sources}
        source_roles = self.source_roles(sources)
        cross = roles.cross_role_text(roles.cross_role_concepts(smap, self.cfg.codebooks))
        cache = b_crosscheck.VectorCache(self.embedder(), self.cfg.cache_dir.parent / "embeddings")
        matches = c_ideas.match_domains(inv, role_map, cache.vectors, self.cfg.c_domain_match_threshold)
        (self.run_dir / "C_domain_matches.json").write_text(json.dumps([m.model_dump() for m in matches], indent=1))
        matches_text = c_ideas.domain_matches_text(matches, c_ideas.domain_ids(inv))
        key = _h(
            *(d.model_dump_json() for d in decs),
            inv.model_dump_json(),
            cross,
            matches_text,
            source_roles,
            c_ideas.ideas_prompt_hash(),
            c_ideas.designs_hash(c_ideas.DESIGNS),
            json.dumps(IdeaBatch.model_json_schema(), sort_keys=True),
            model,
            str(self.cfg.c_ideation_temperature),
            json.dumps(self.cfg.c_ideation_seeds),
            str(self.cfg.c_ideas_per_call),
            str(self.cfg.c_min_new_ideas),
            c_ideas.C1_LOGIC_VERSION,
        )
        pool = self._cached("C_ideas", key, IdeaPool, "C_ideas.json")
        if pool is None:
            kw = self._llm_kwargs()
            pool, recs = c_ideas.generate_ideas(
                decs,
                inv,
                sources,
                cross,
                matches_text,
                source_roles,
                role_map,
                client,
                designs=c_ideas.DESIGNS,
                seeds=self.cfg.c_ideation_seeds,
                n_ideas=self.cfg.c_ideas_per_call,
                min_new=self.cfg.c_min_new_ideas,
                temperature=self.cfg.c_ideation_temperature,
                max_retries=kw["max_retries"],
                log_dir=kw["log_dir"],
                checkpoint_dir=self.run_dir / "checkpoints" / "C_ideas",
                salt=_h(model, str(self.cfg.num_ctx)),
            )
            self._record(recs)
            for stage in pool.failed_calls:
                self._warn(f"{stage}: no valid ideas after retries; skipped")
            self._store("C_ideas", key, pool, "C_ideas.json")
            (self.run_dir / "C_ideas.md").write_text(c_ideas.pool_markdown(pool))
        return pool

    def _client_for(self, model: str) -> LLMClient:
        if self.cfg.backend != "ollama":
            raise ValueError("a separate C1 ideation model is supported only with the local ollama backend")
        return make_client(
            "ollama",
            model,
            ollama_host=self.settings.ollama_host,
            num_ctx=self.cfg.num_ctx,
            max_output_tokens=self.cfg.max_output_tokens,
        )

    def stage_c_narrow(
        self, decs: list[ManuscriptDecomposition], sources: dict[str, DataSource], inv: DataInventory, pool: IdeaPool
    ) -> Path:
        """C2 dedupe, C3 grounding (two-turn), C4 scoring and selection, C5 review file. Never writes C_gaps.json:
        the investigator's pick of 5 from the shortlist becomes D's input in a later step."""
        cfg = self.cfg
        cache = b_crosscheck.VectorCache(self.embedder(), cfg.cache_dir.parent / "embeddings")
        deduped = c_narrow.dedupe(pool, cache.vectors, cfg.c_dedupe_threshold)
        (self.run_dir / "C_dedupe.json").write_text(deduped.model_dump_json(indent=1))
        role_map = {s.id: [str(r) for r in s.roles] for s in cfg.codebooks if s.id in sources}
        specs = roles.specs_by_id(cfg.codebooks, sources)
        source_roles = self.source_roles(sources)
        kw = self._llm_kwargs()
        key = _h(
            pool.model_dump_json(),
            deduped.model_dump_json(),
            inv.model_dump_json(),
            *(d.model_dump_json() for d in decs),
            *(sources[s].model_dump_json() for s in sorted(sources)),
            json.dumps({k: v.model_dump(mode="json") for k, v in sorted(specs.items())}, sort_keys=True),
            source_roles,
            *c_narrow.prompt_hashes(),
            c_narrow.C3_LOGIC_VERSION,
            c_ideas.designs_hash(c_ideas.DESIGNS),
            json.dumps(GroundingAnswer.model_json_schema(), sort_keys=True),
            cfg.model,
            str(cfg.seed),
            str(cfg.temperature),
            str(cfg.c_reason_temperature),
            str(cfg.c_ground_vars_per_source),
            str(cfg.c_ground_vars_per_domain),
        )
        grounding = self._cached("C_ground", key, Grounding, "C_grounding.json")
        if grounding is None:
            grounding, recs = c_narrow.ground_ideas(
                pool,
                deduped,
                decs,
                inv,
                sources,
                specs,
                role_map,
                source_roles,
                self.client,
                cache.vectors,
                per_source=cfg.c_ground_vars_per_source,
                per_domain=cfg.c_ground_vars_per_domain,
                seed=cfg.seed,
                reason_temperature=cfg.c_reason_temperature,
                temperature=cfg.temperature,
                max_retries=kw["max_retries"],
                log_dir=kw["log_dir"],
                checkpoint_dir=self.run_dir / "checkpoints" / "C_ground",
                salt=_h(cfg.model, str(cfg.num_ctx)),
            )
            self._record(recs)
            for stage in grounding.failed_calls:
                self._warn(f"{stage}: no valid grounding after retries; skipped")
            self._store("C_ground", key, grounding, "C_grounding.json")
        skey = _h(
            key,
            grounding.model_dump_json(),
            json.dumps(cfg.c_reference_ideas),
            str(cfg.c_shortlist),
            str(cfg.c_min_importance),
            str(cfg.c_shortlist_max_similarity),
        )
        sl = self._cached("C_shortlist", skey, Shortlist, "C_shortlist.json")
        if sl is None:
            ratings, recs = c_narrow.rate_importance(
                grounding.gaps,
                cfg.c_reference_ideas,
                source_roles,
                self.client,
                seed=cfg.seed,
                temperature=cfg.temperature,
                max_retries=kw["max_retries"],
                log_dir=kw["log_dir"],
                checkpoint_dir=self.run_dir / "checkpoints" / "C_importance",
                salt=_h(cfg.model, str(cfg.num_ctx)),
            )
            self._record(recs)
            sl = c_narrow.shortlist(
                grounding.gaps,
                sources,
                decs,
                ratings,
                cache.vectors,
                size=cfg.c_shortlist,
                min_importance=cfg.c_min_importance,
                max_similarity=cfg.c_shortlist_max_similarity,
            )
            self._store("C_shortlist", skey, sl, "C_shortlist.json")
        out = self.run_dir / "review_C_shortlist.md"
        out.write_text(c_narrow.review_markdown(pool, deduped, grounding, sl))
        return out

    def ideate(self) -> Path:
        """C0-C5 on an existing run whose B is approved: inventory, ideas, dedupe, grounding, scoring, and the
        shortlist for review (review_C_shortlist.md). Not part of `run()`: D still reads C_gaps.json."""
        sources = self.ingest_sources()
        decs = self.stage_a()
        smap = self.stage_b(decs, sources)
        inv = self.stage_c_inventory(sources, smap)
        pool = self.stage_c_ideas(decs, sources, smap, inv)
        return self.stage_c_narrow(decs, sources, inv, pool)

    def stage_d(
        self, gaps: GapSet, decs: list[ManuscriptDecomposition], sources: dict[str, DataSource], smap: SchemaMap
    ) -> StrategySet:
        denoms = {c.id for c in self.cfg.codebooks if c.denominator and c.id in sources}
        key = _h(
            gaps.model_dump_json(),
            *d_strategy.prompt_hashes(),
            self.cfg.model,
            json.dumps(sorted(denoms)),
            json.dumps(Strategy.model_json_schema(), sort_keys=True),
        )
        cached = self._cached("D", key, StrategySet, "D_strategies.json")
        if cached is None:
            cached, recs = d_strategy.generate_strategies(
                gaps.gaps, decs, sources, self.client, smap, denoms, **self._llm_kwargs()
            )
            self._record(recs)
            self._store("D", key, cached, "D_strategies.json")
        return cached

    def stage_e(self, strategies: StrategySet, sources: dict[str, DataSource]) -> FeasibilitySet:
        key = _h(
            strategies.model_dump_json(),
            *(s.model_dump_json() for s in sources.values()),
            *e_feasibility.prompt_hashes(),
            self.cfg.model,
        )
        cached = self._cached("E", key, FeasibilitySet, "E_feasibility.json")
        if cached is None:
            cached, recs = e_feasibility.assess(strategies.strategies, sources, self.client, **self._llm_kwargs())
            self._record(recs)
            self._store("E", key, cached, "E_feasibility.json")
        return cached

    def run(self) -> Path:
        try:
            return self._run()
        except GenerationFailedError as e:
            if e.record is not None:
                self._record([e.record])  # failed calls count toward grounding-rate metrics
            raise

    def _run(self) -> Path:
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
