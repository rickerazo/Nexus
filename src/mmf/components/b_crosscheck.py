"""Independent check on Component B: rank each source's variables for each concept by embedding similarity and
compare with the LLM's mappings. Disagreements are flagged for the human reviewer; neither pathway overrides
the other, and nothing here changes the SchemaMap.

Verdict per (concept, source):
- agree             every variable the LLM chose is in the embedding top-k
- llm_outside_topk  the LLM chose a variable the embeddings rank below top-k (possible stretch or wrong map)
- possible_miss     the LLM chose nothing, but the best embedding candidate scores >= the miss threshold
- both_none         the LLM chose nothing and no candidate reaches the threshold
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from mmf.components.b_schema_map import Concept, collect_concepts
from mmf.llm.base import Embedder
from mmf.schemas.dataset import CheckCandidate, CheckRecord, DataSource, SchemaCheck, SchemaMap, Variable
from mmf.schemas.manuscript import ManuscriptDecomposition

# mxbai-embed-large's retrieval instruction for queries; documents are embedded without a prefix.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
FINGERPRINT_VERSION = "1"  # bump when the fingerprint text changes; part of the B check cache key
_MACHINE_NOTES = ("position=", "file=", "format=")


def variable_fingerprint(v: Variable) -> str:
    """Name, label and up to 8 coded values: opaque codenames (CIG_0, BFED) carry no meaning on their own."""
    notes = "; ".join(p.strip() for p in v.notes.split(";") if p.strip() and not p.strip().startswith(_MACHINE_NOTES))
    parts = [f"{v.name}: {v.label}."]
    if v.levels:
        parts.append("Values: " + "; ".join(v.levels[:8]) + ".")
    if notes:
        parts.append(notes)
    return " ".join(parts)


def concept_fingerprint(c: Concept) -> str:
    return f"{QUERY_PREFIX}{c.name} ({c.role}): {c.operationalization}"


class VectorCache:
    """Embeddings on disk under <dir>/<model>/<digest>/<sha256(text)>.json, so reruns embed nothing twice."""

    def __init__(self, embedder: Embedder, cache_dir: Path | None) -> None:
        self.embedder = embedder
        digest = embedder.model_digest() or "nodigest"
        self.dir = cache_dir / embedder.model.replace(":", "_").replace("/", "_") / digest[:16] if cache_dir else None

    def vectors(self, texts: list[str]) -> np.ndarray:
        keys = [hashlib.sha256(t.encode()).hexdigest() for t in texts]
        found: dict[str, list[float]] = {}
        if self.dir is not None:
            self.dir.mkdir(parents=True, exist_ok=True)
            for k in set(keys):
                p = self.dir / f"{k}.json"
                if p.exists():
                    found[k] = json.loads(p.read_text())
        todo = list(dict.fromkeys((k, t) for k, t in zip(keys, texts, strict=True) if k not in found))
        if todo:
            for (k, _), vec in zip(todo, self.embedder.embed([t for _, t in todo]), strict=True):
                found[k] = vec
                if self.dir is not None:
                    (self.dir / f"{k}.json").write_text(json.dumps(vec))
        m = np.asarray([found[k] for k in keys], dtype=np.float32)
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.where(norms == 0, 1, norms)


def check_schema(
    smap: SchemaMap,
    decompositions: list[ManuscriptDecomposition],
    sources: dict[str, DataSource],
    embedder: Embedder,
    *,
    top_k: int,
    miss_threshold: float,
    cache_dir: Path | None,
) -> SchemaCheck:
    concepts = collect_concepts(decompositions)
    cache = VectorCache(embedder, cache_dir)
    cvecs = cache.vectors([concept_fingerprint(c) for c in concepts])
    llm: dict[tuple[str, str], list[str]] = {}
    for m in smap.mappings:
        names = llm.setdefault((m.concept.lower(), m.source_id), [])
        if m.variable and m.variable not in names:
            names.append(m.variable)

    records: list[CheckRecord] = []
    for sid, src in sources.items():
        if not src.variables:
            continue
        vvecs = cache.vectors([variable_fingerprint(v) for v in src.variables])
        scores = cvecs @ vvecs.T  # (concepts, variables) cosine similarities
        k = min(top_k, len(src.variables))
        for ci, c in enumerate(concepts):
            order = np.argsort(-scores[ci])[:k]
            top = [
                CheckCandidate(
                    name=src.variables[j].name, label=src.variables[j].label, score=round(float(scores[ci, j]), 4)
                )
                for j in order
            ]
            chosen = llm.get((c.name.lower(), sid), [])
            top_names = {t.name.upper() for t in top}
            outside = [n for n in chosen if n.upper() not in top_names]
            if chosen:
                verdict = "llm_outside_topk" if outside else "agree"
            else:
                verdict = "possible_miss" if top and top[0].score >= miss_threshold else "both_none"
            records.append(
                CheckRecord(
                    concept=c.name,
                    role=c.role,
                    source_id=sid,
                    llm_variables=chosen,
                    verdict=verdict,
                    outside=outside,
                    top=top,
                )
            )
    return SchemaCheck(
        embed_model=embedder.model,
        embed_digest=embedder.model_digest(),
        top_k=top_k,
        miss_threshold=miss_threshold,
        records=records,
    )
