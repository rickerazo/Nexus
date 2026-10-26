from pathlib import Path

import pytest

from mmf.ingest.pdf import load_document
from mmf.schemas import DataSource, Variable

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def mini_codebook_doc():
    return load_document(FIXTURES / "mini_codebook.txt")


@pytest.fixture
def mini_manuscript_doc():
    return load_document(FIXTURES / "mini_manuscript.md")


@pytest.fixture
def sources() -> dict[str, DataSource]:
    ds = DataSource(
        id="cdc",
        title="mini",
        document_path="x",
        document_sha256="0" * 64,
        variables=[
            Variable(name="SEX", label="Sex of infant", page=1),
            Variable(name="MAGER9", label="Mother's age recode 9", page=1),
            Variable(name="CIG_REC", label="Cigarette smoking", page=1, years=[2015, 2016]),
            Variable(name="COMBGEST", label="Combined gestation", page=1, years=[2017]),
            Variable(name="BIRTHS", label="Live births (denominator)", page=1),
        ],
    )
    return {"cdc": ds}
