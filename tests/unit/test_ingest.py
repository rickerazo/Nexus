from mmf.ingest.chunk import chunk_document
from mmf.ingest.codebook import pass1_regex, reconcile
from mmf.ingest.pdf import Document, Page
from mmf.schemas import Variable


def test_pass1_table_layout(mini_codebook_doc):
    vars_ = {v.name: v for v in pass1_regex(mini_codebook_doc)}
    assert set(vars_) == {"SEX", "MAGER9", "CIG_REC", "COMBGEST", "AGED", "UCOD"}
    assert vars_["SEX"].label == "Sex of infant"
    assert vars_["SEX"].levels == ["1=MALE", "2=FEMALE"]
    assert vars_["MAGER9"].notes == "format=AGE9F"
    assert vars_["CIG_REC"].page == 1


def test_reconcile_rejects_invented_names(mini_codebook_doc):
    p1 = pass1_regex(mini_codebook_doc)
    p2 = [
        Variable(name="SEX", label="Infant sex", type="binary", page=1),
        Variable(name="DOB_TT", label="Time of birth", page=1),  # not in text -> rejected
    ]
    accepted, rejected = reconcile(mini_codebook_doc, p1, p2)
    names = {v.name for v in accepted}
    assert "DOB_TT" not in names and [r.name for r in rejected] == ["DOB_TT"]
    assert next(v for v in accepted if v.name == "SEX").type == "binary"  # enriched from pass 2


def test_chunking_never_splits_pages():
    doc = Document(path="p", sha256="x", title="t", pages=[Page(number=i, text="word " * 400) for i in range(1, 6)])
    chunks = chunk_document(doc, max_tokens=1500)
    assert len(chunks) > 1
    covered = [n for c in chunks for n in range(c.first_page, c.last_page + 1)]
    assert covered == [1, 2, 3, 4, 5]
    assert all("[page" in c.text for c in chunks)


def test_sha256_cache_roundtrip(tmp_path, mini_manuscript_doc):
    from mmf.ingest.pdf import load_document

    src = tmp_path / "m.md"
    src.write_text("# T\n\nbody")
    d1 = load_document(src, cache_dir=tmp_path / "cache")
    d2 = load_document(src, cache_dir=tmp_path / "cache")
    assert d1 == d2 and (tmp_path / "cache" / f"{d1.sha256}.json").exists()


def test_pass1_nvss_layout():
    from tests.conftest import FIXTURES

    from mmf.ingest.pdf import load_document

    vars_ = {v.name: v for v in pass1_regex(load_document(FIXTURES / "mini_nvss_guide.txt"))}
    assert set(vars_) == {"FAGE11", "FRACE31"}
    assert vars_["FAGE11"].label == "Father's Age Recode 11"
    assert vars_["FAGE11"].levels == ["01=Under 15 years", "02=15-19 years"]
    assert vars_["FAGE11"].notes == "position=149-150; file=P,G"
