from mmf.schemas import VariableRef
from mmf.validate.grounding import quote_found, resolve_refs, unresolved_problems


def test_verbatim_quote_found(mini_manuscript_doc):
    ok, page = quote_found("Male excess risk emerged only after 44 weeks", mini_manuscript_doc)
    assert ok and page == 1


def test_quote_tolerates_whitespace_and_case(mini_manuscript_doc):
    ok, _ = quote_found("male EXCESS risk   emerged only after 44 weeks postconceptional age", mini_manuscript_doc)
    assert ok


def test_paraphrase_rejected(mini_manuscript_doc):
    ok, _ = quote_found("Boys were at higher risk after forty-four weeks of postconceptional age", mini_manuscript_doc)
    assert not ok


def test_short_quote_rejected(mini_manuscript_doc):
    assert quote_found("risk", mini_manuscript_doc) == (False, None)


def test_resolve_refs(sources):
    res = resolve_refs(
        [
            VariableRef(source_id="cdc", name="sex"),
            VariableRef(source_id="cdc", name="NOPE"),
            VariableRef(source_id="zzz", name="SEX"),
        ],
        sources,
    )
    assert [r.resolved for r in res] == [True, False, False]
    assert res[0].variable.name == "SEX"
    assert len(unresolved_problems([r.ref for r in res], sources)) == 2
