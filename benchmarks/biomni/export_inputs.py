"""Export the benchmark inputs for Biomni, using MMF's deterministic (non-LLM) ingestion only.

Biomni gets what MMF gets before any LLM step: the manuscript texts, every documented variable of every source
(the parsed data dictionaries, as CSV), the original documents, and the investigator-supplied source roles from
the config. It gets none of MMF's LLM outputs (claims, schema map, inventory, ideas) and none of MMF's prompts.

Run with the MMF venv:  .venv/bin/python benchmarks/biomni/export_inputs.py configs/suid.yaml RUN_DIR
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

from mmf.components import roles
from mmf.config import RunConfig
from mmf.ingest.pdf import load_document
from mmf.schemas.dataset import DataSource


def main(config: str, run_dir: str, sources_dir: str = "runs/suid_poc_20261103_ideas/sources") -> None:
    cfg = RunConfig.from_yaml(config)
    out = Path(run_dir) / "inputs"
    (out / "manuscripts").mkdir(parents=True, exist_ok=True)
    (out / "dictionaries").mkdir(exist_ok=True)
    (out / "original_documents").mkdir(exist_ok=True)
    manifest: dict[str, dict[str, str]] = {}

    for p in cfg.manuscripts:
        doc = load_document(p, cfg.cache_dir)
        dest = out / "manuscripts" / f"{Path(p).stem}.txt"
        dest.write_text(doc.text)
        manifest[str(dest.relative_to(out))] = {"from": str(p), "sha256": doc.sha256}

    sources: dict[str, DataSource] = {}
    for spec in cfg.codebooks:
        ds = DataSource.model_validate_json((Path(sources_dir) / f"{spec.id}.json").read_text())
        sources[spec.id] = ds
        dest = out / "dictionaries" / f"{spec.id}.csv"
        with dest.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "label", "type", "levels", "years", "notes"])
            for v in ds.variables:
                w.writerow([v.name, v.label, v.type, " | ".join(v.levels), " ".join(map(str, v.years)), v.notes or ""])
        orig = out / "original_documents" / Path(spec.path).name
        shutil.copy2(spec.path, orig)
        manifest[str(dest.relative_to(out))] = {"from": str(spec.path), "sha256": ds.document_sha256}

    (out / "source_roles.md").write_text(roles.source_roles_text(cfg.codebooks, sources) + "\n")
    manifest["source_roles.md"] = {
        "from": config,
        "sha256": hashlib.sha256((out / "source_roles.md").read_bytes()).hexdigest(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"exported {len(manifest)} files to {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
