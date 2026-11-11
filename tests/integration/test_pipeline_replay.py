"""End-to-end A→E on the fixtures, replaying a recorded cassette (no model needed)."""

import json
from pathlib import Path

import pytest
from tests.integration.replay import ReplayClient
from tests.unit.test_crosscheck import KeywordEmbedder

from mmf.config import RunConfig, SourceSpec
from mmf.pipeline import ReviewPending, Run, approve

CASSETTE = Path(__file__).parent.parent / "fixtures" / "cassettes" / "smoke"
ROOT = Path(__file__).parent.parent.parent


@pytest.mark.skipif(
    not CASSETTE.exists(), reason="no recorded cassette; run scripts/smoke.sh and copy its llm_log here"
)
def test_pipeline_end_to_end_replay(tmp_path: Path) -> None:
    cfg = RunConfig(
        manuscripts=[ROOT / "tests/fixtures/mini_manuscript.md"],
        codebooks=[
            SourceSpec(id="cdc", path=ROOT / "tests/fixtures/mini_codebook.txt", title="Mini codebook (fixture)")
        ],
        model="replay",
        n_gaps=2,
        chunk_tokens=4000,
        out_dir=tmp_path,
        cache_dir=tmp_path / "cache",
    )
    run_dir = tmp_path / "run"
    client = ReplayClient(CASSETTE)
    for stage in ("B", "C"):
        with pytest.raises(ReviewPending):
            Run(cfg, run_dir=run_dir, client=client, embedder=KeywordEmbedder()).run()
        assert (run_dir / f"review_{stage}.md").exists()
        if stage == "B":
            assert (run_dir / "B_check.json").exists()
            assert "## Cross-check (embedding vs LLM)" in (run_dir / "review_B.md").read_text()
        approve(run_dir, stage)
    report = Run(cfg, run_dir=run_dir, client=client, embedder=KeywordEmbedder()).run()
    text = report.read_text()
    assert "## D. Strategies" in text and "Not assessed by MMF" in text
    dec = json.loads((run_dir / "A_mini_manuscript.json").read_text())
    assert any(v["role"] == "outcome" for v in dec["variables"]), "Component A extracted no outcome variable"
    manifest = (run_dir / "manifest.json").read_text()
    assert '"ok": false' not in manifest
    # every variable named in the report resolves to the fixture codebook
    import re

    names = set(re.findall(r"`cdc:([A-Z0-9_]+)`", text))
    assert names and names <= {"SEX", "MAGER9", "CIG_REC", "COMBGEST", "AGED", "UCOD"}

    # a stage that regenerates must stop for review again; the old approval must not carry over
    run = Run(cfg, run_dir=run_dir, client=client, embedder=KeywordEmbedder())
    assert "approved: true" in (run_dir / "review_C.md").read_text()
    run._reset_review("C")
    with pytest.raises(ReviewPending):
        run._review_gate("C", json_model(run_dir / "C_gaps.json"), "Knowledge gaps")


def json_model(path: Path):
    from mmf.schemas import GapSet

    return GapSet.model_validate_json(path.read_text())
