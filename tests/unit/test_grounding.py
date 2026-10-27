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


def test_stitched_sentences_pass_but_paraphrase_fails(mini_manuscript_doc):
    from mmf.validate.grounding import quote_problems

    stitched = "Male excess risk emerged only after 44 weeks postconceptional age. A limitation is that the sleep environment was not available in the linked birth-death files."
    assert quote_problems(stitched, mini_manuscript_doc) == []
    mixed = "Male excess risk emerged only after 44 weeks postconceptional age. Boys were at higher risk after forty-four weeks."
    probs = quote_problems(mixed, mini_manuscript_doc)
    assert len(probs) == 1 and "Boys were" in probs[0]
    near_miss = "Male excess risk emerged only after 44 weeks of postconceptional age, and prenatal smoking was associated with earlier onset."
    probs = quote_problems(near_miss, mini_manuscript_doc)
    assert len(probs) == 1 and "Closest text" in probs[0] and "44 weeks postconceptional age" in probs[0]
