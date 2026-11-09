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
    assert set(vars_) == {"FAGE11", "FRACE31", "SEX", "WIC", "OEGest_R3", "MBSTATE_REC", "F_MM_PLAC"}
    assert vars_["FAGE11"].label == "Father's Age Recode 11"
    assert vars_["FAGE11"].levels == ["01=Under 15 years", "02=15-19 years"]
    assert vars_["FAGE11"].notes == "position=149-150; file=P,G"
    # a blank line between the name and its label (LinkCO15Guide) must not drop the variable
    assert vars_["SEX"].label == "Sex of Infant"
    assert vars_["SEX"].levels == ["M=Male", "F=Female"]
    assert vars_["SEX"].notes == "position=475; file=P,G"
    # a label identical to the name is still a label
    assert vars_["WIC"].label == "WIC"
    assert vars_["WIC"].levels == ["Y=Yes", "N=No"]  # stops before the mixed-case header that follows
    assert vars_["OEGest_R3"].label == "Obstetric Estimate Recode 3"  # mixed-case name
    assert vars_["OEGest_R3"].levels == ["1=Under 37 weeks"]
    assert vars_["MBSTATE_REC"].label == "Mother's Nativity"  # name and label on one line
    assert vars_["MBSTATE_REC"].levels == ["1=Born in the U.S."]
    assert vars_["F_MM_PLAC"].label == "Reporting Flag for Perineal Laceration"  # name split by the PDF


def test_chunking_splits_oversized_single_page():
    text = "\n\n".join(f"paragraph {i} " + "word " * 120 for i in range(30))
    doc = Document(path="p", sha256="x", title="t", pages=[Page(number=1, text=text)])
    chunks = chunk_document(doc, max_tokens=1000)
    assert len(chunks) > 3
    assert all(c.first_page == 1 and c.last_page == 1 for c in chunks)
    assert all(len(c.text) // 3 <= 1000 + 50 for c in chunks)
    joined = "".join(c.text.replace("\n[page 1]\n", "") for c in chunks)
    assert all(f"paragraph {i} " in joined for i in range(30))


def _doc(*pages: str) -> Document:
    return Document(path="p", sha256="x", title="t", pages=[Page(number=i, text=t) for i, t in enumerate(pages, 1)])


def test_pass1_prams_suffixed_and_wrapped_qnum():
    page = "\n".join(
        [
            "Q#",
            "Variable",
            "SAS Label",
            "Format",
            "Codes",
            "4c",
            "BPG_DEPRS8",
            "Health prob -- Depression",
            "NY1F",
            "1=NO",
            "2=YES",
            "4d_L11a",
            "HTH_ASMA",
            "Health prob -- Asthma",
            "NY1F",
            "1=NO",
            "2=YES",
            "18k_ARS",
            "C",
            "PG8_GUM",
            "Health prob during preg -- Gum disease",
            "NY1F",
            "1=NO",
            "2=YES",
        ]
    )
    vars_ = {v.name: v for v in pass1_regex(_doc(page))}
    assert set(vars_) == {"BPG_DEPRS8", "HTH_ASMA", "PG8_GUM"}
    assert vars_["BPG_DEPRS8"].levels == ["1=NO", "2=YES"]  # does not absorb the next row
    assert vars_["HTH_ASMA"].label == "Health prob -- Asthma"
    assert vars_["PG8_GUM"].notes == "format=NY1F"


def test_pass1_prams_section_without_qnum():
    page = "\n".join(
        [
            "PRAMS Phase 8 Analytic Variables",
            "Variable",
            "SAS Label",
            "Format",
            "Codes",
            "CIG_PRIOR",
            "No. of cigarettes smoked daily",
            "- prior to preg",
            "BCF",
            ".U=UNKNOWN",
            "PREV_LBW",
            "Previous live birth -- low birth weight (FORCED",
            "SKIP)",
            ".B=DK/BLANK",
            "1=NO",
            "SLEEPOWN",
            "Sleep -- baby alone (FORCED SKIP)",
            "FREQ5F",
            "1=ALWAYS",
            "2=OFTEN/ALMOST",
            "ALWAYS",
            "SLEEPPOS",
            "Sleeping position -- baby (FORCED SKIP)",
            "SLEEPPOS",
            ".S=SKIP",
            "1=SIDE",
            "2=BACK",
        ]
    )
    vars_ = {v.name: v for v in pass1_regex(_doc(page))}
    assert set(vars_) == {"CIG_PRIOR", "PREV_LBW", "SLEEPOWN", "SLEEPPOS"}
    assert vars_["CIG_PRIOR"].label == "No. of cigarettes smoked daily - prior to preg"
    assert vars_["CIG_PRIOR"].notes == "format=BCF"
    assert vars_["PREV_LBW"].label == "Previous live birth -- low birth weight (FORCED SKIP)"
    assert vars_["SLEEPOWN"].levels == ["1=ALWAYS", "2=OFTEN/ALMOST ALWAYS"]  # wrapped code label
    assert vars_["SLEEPPOS"].notes == "format=SLEEPPOS"  # format named like the variable
    assert vars_["SLEEPPOS"].levels == [".S=SKIP", "1=SIDE", "2=BACK"]
    # the unnumbered pass only reads pages without a Q# column
    assert "CIG_PRIOR" not in {v.name for v in pass1_regex(_doc("Q#\n" + page))}
