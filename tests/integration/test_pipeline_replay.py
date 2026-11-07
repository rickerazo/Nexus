"""End-to-end A→E on the fixtures, replaying a recorded cassette (no model needed)."""

import json
from pathlib import Path

import pytest
from tests.integration.replay import ReplayClient

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
            Run(cfg, run_dir=run_dir, client=client).run()
        assert (run_dir / f"review_{stage}.md").exists()
        approve(run_dir, stage)
    report = Run(cfg, run_dir=run_dir, client=client).run()
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
