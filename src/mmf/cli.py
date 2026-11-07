"""`mmf` command line."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated

import typer

from mmf.config import RunConfig, Settings

app = typer.Typer(help="Manuscript-to-Model Framework (Nexus).", no_args_is_help=True)


@app.callback()
def _setup(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@app.command()
def ingest(
    path: Path,
    source_id: Annotated[str, typer.Option("--id", help="Slug used as source_id.")],
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("data/sources"),
    no_llm: Annotated[bool, typer.Option(help="Deterministic pass only.")] = False,
    model: str = "qwen2.5:14b",
    backend: str = "ollama",
) -> None:
    """Parse one codebook into a DataSource JSON."""
    from mmf.ingest.codebook import build_datasource
    from mmf.ingest.pdf import load_document
    from mmf.llm.structured import make_client

    s = Settings()
    client = None if no_llm else make_client(backend, model, ollama_host=s.ollama_host, num_ctx=32768)
    doc = load_document(path)
    ds, rejected, _ = build_datasource(doc, source_id, client, log_dir=out / "llm_log")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{source_id}.json").write_text(ds.model_dump_json(indent=2))
    typer.echo(
        f"{source_id}: {len(ds.variables)} variables accepted, {len(rejected)} LLM proposals rejected -> {out / (source_id + '.json')}"
    )


@app.command()
def run(
    config: Path,
    run_dir: Annotated[Path | None, typer.Option(help="Resume/continue an existing run directory.")] = None,
) -> None:
    """Execute the pipeline A→E (stops at review checkpoints)."""
    from mmf.llm.structured import StageInputError
    from mmf.pipeline import ReviewPending, Run

    cfg = RunConfig.from_yaml(config)
    r = Run(cfg, run_dir=run_dir)
    try:
        report = r.run()
    except ReviewPending as e:
        typer.echo(str(e))
        typer.echo(f"Resume with: mmf run {config} --run-dir {r.run_dir}")
        raise typer.Exit(code=2) from None
    except StageInputError as e:
        typer.echo(f"Stopped: {e}", err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"Report: {report}")


@app.command()
def approve(run_dir: Path, stage: str) -> None:
    """Mark a review checkpoint as approved (after you have checked/edited the stage JSON)."""
    from mmf.pipeline import approve as _approve

    _approve(run_dir, stage)
    typer.echo(f"approved stage {stage} in {run_dir}")


@app.command()
def manifest(paths: list[Path], out: Path = Path("data/manifest.json")) -> None:
    """Record sha256 of input documents."""
    from mmf.pipeline import manifest_for_paths

    out.write_text(json.dumps(manifest_for_paths(paths), indent=2) + "\n")
    typer.echo(f"wrote {out}")


if __name__ == "__main__":
    app()
