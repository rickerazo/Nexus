"""The ingestion audit is an independent check on the codebook parser."""

from pathlib import Path

import pytest
from tests.conftest import FIXTURES

from mmf.config import RunConfig, SourceSpec
from mmf.ingest import codebook
from mmf.ingest.audit import audit_codebook, find_anchors
from mmf.ingest.pdf import Document, Page, load_document
from mmf.llm.structured import StageInputError
from mmf.pipeline import Run
from mmf.schemas import DataSource


def _ds(doc: Document, drop: str | None = None) -> DataSource:
    vs = [v for v in codebook.pass1_regex(doc) if v.name != drop]
    return DataSource(id="nvss", title="t", document_path="p", document_sha256="x", variables=vs)


def test_anchor_reconciliation():
    doc = load_document(FIXTURES / "mini_nvss_guide.txt")
    assert len(find_anchors(doc)) == 7
    assert audit_codebook(doc, _ds(doc)).unmatched_anchors == []
    misses = audit_codebook(doc, _ds(doc, drop="SEX")).unmatched_anchors
    assert [(m.position, m.file, m.text, m.extracted) for m in misses] == [("475", "P,G", "SEX", [])]


def test_census_lists_unextracted_identifiers():
    doc = Document(
        path="p",
        sha256="x",
        title="t",
        pages=[Page(number=3, text="Variable | Label\nMAGER9 | Mother's age\nCIG_REC | Smoking\nNOTE\nBFED\nBFED\n")],
    )
    ds = DataSource(id="s", title="t", document_path="p", document_sha256="x", variables=[])
    ds.variables = [v for v in codebook.pass1_table(doc) if v.name == "MAGER9"]
    census = {c.token: c for c in audit_codebook(doc, ds).census}
    assert set(census) == {"CIG_REC", "BFED"}  # MAGER9 was extracted; NOTE is a layout word
    assert census["BFED"].count == 2 and census["BFED"].page == 3
    assert census["CIG_REC"].context == "CIG_REC | Smoking"


def test_pipeline_stops_on_unmatched_anchor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    real = codebook.build_datasource

    def lossy(doc, source_id, client, **kw):  # a parser that silently drops SEX
        ds, rejected, recs = real(doc, source_id, client, **kw)
        ds.variables = [v for v in ds.variables if v.name != "SEX"]
        return ds, rejected, recs

    monkeypatch.setattr("mmf.pipeline.build_datasource", lossy)
    cfg = RunConfig(
        manuscripts=[],
        codebooks=[SourceSpec(id="nvss", path=FIXTURES / "mini_nvss_guide.txt", title="t", llm_extract=False)],
        out_dir=tmp_path,
        cache_dir=tmp_path / "cache",
    )
    run = Run(cfg, run_dir=tmp_path / "run", client=object())  # type: ignore[arg-type]
    with pytest.raises(StageInputError, match="1 field header"):
        run.ingest_sources()
    assert (tmp_path / "run" / "sources" / "nvss.audit.json").exists()
