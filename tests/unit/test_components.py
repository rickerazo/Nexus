"""Validators are the constraint mechanism; test them without any LLM."""

from mmf.components.b_schema_map import Concept, canonical_concept, map_validator
from mmf.components.c_gaps import gap_validator
from mmf.components.d_strategy import strategy_validator
from mmf.components.e_feasibility import deterministic_report
from mmf.schemas import (
    Claim,
    ClaimKind,
    GapSet,
    KnowledgeGap,
    ManuscriptDecomposition,
    OutcomeSpec,
    Strategy,
    VariableRef,
)
from mmf.schemas.dataset import ConceptMapping, SchemaMap
from mmf.validate.vocab import ModelClass, StudyDesign

REF = lambda n: VariableRef(source_id="cdc", name=n)  # noqa: E731


def _dec():
    return ManuscriptDecomposition(
        manuscript_id="m1",
        title="t",
        document_sha256="0" * 64,
        claims=[Claim(id="m1.C1", kind=ClaimKind.LIMITATION, statement="s", quote="q" * 20, page=1)],
    )


def _gap(**kw):
    base = dict(
        id="G1",
        statement="s",
        rationale="r",
        prior_art="word " * 20,
        supporting_claim_ids=["m1.C1"],
        required_concepts=["sex"],
        required_variables=[REF("SEX")],
    )
    base.update(kw)
    return KnowledgeGap(**base)


def test_gap_validator_accepts_grounded_gap(sources):
    assert gap_validator([_dec()], sources, 1)(GapSet(gaps=[_gap()])) == []


def test_gap_validator_rejects_bad_claim_and_variable_and_count(sources):
    problems = gap_validator([_dec()], sources, 2)(
        GapSet(gaps=[_gap(supporting_claim_ids=["m1.C9"], required_variables=[REF("GHOST")], prior_art="short")])
    )
    joined = " ".join(problems)
    assert (
        "expected exactly 2" in joined and "unknown claim ids" in joined and "GHOST" in joined and "prior_art" in joined
    )


def _strategy(**kw):
    base = dict(
        id="S1",
        gap_id="G1",
        research_question="q",
        outcome=OutcomeSpec(variable=REF("UCOD"), definition="d"),
        exposures=[REF("CIG_REC")],
        interactions=[[REF("SEX"), REF("CIG_REC")]],
        design=StudyDesign.POPULATION_INCIDENCE,
        model_class=ModelClass.NEGATIVE_BINOMIAL,
        offset=REF("BIRTHS"),
        rationale="word " * 25,
    )
    base.update(kw)
    return Strategy(**base)


def test_strategy_validator_requires_offset_for_rate_models(sources):
    assert strategy_validator(_gap(), sources)(_strategy()) == []
    problems = strategy_validator(_gap(), sources)(
        _strategy(offset=None, interactions=[[REF("SEX")]], covariates=[REF("NOPE")])
    )
    joined = " ".join(problems)
    assert "offset" in joined and "2+ variables" in joined and "NOPE" in joined


def test_strategy_enums_are_enforced_by_schema():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        _strategy(model_class="random_forest")


def test_feasibility_year_overlap_blocker(sources):
    rep = deterministic_report(_strategy(exposures=[REF("CIG_REC"), REF("COMBGEST")]), sources)
    assert any("common year" in b for b in rep.blockers)
    rep2 = deterministic_report(_strategy(), sources)
    assert rep2.feasible and "statistical power" in rep2.not_assessed


def test_strategy_validator_outcome_rules(sources):
    # outcome doubling as exposure is rejected
    p = strategy_validator(_gap(), sources)(_strategy(outcome=OutcomeSpec(variable=REF("CIG_REC"), definition="d")))
    assert any("also appears as exposure" in x for x in p)
    # outcome must be among mapped outcome variables when B mapped any
    p = strategy_validator(_gap(), sources, outcome_refs={"cdc:AGED"})(_strategy())
    assert any("mapped from an outcome concept" in x for x in p)
    assert strategy_validator(_gap(), sources, outcome_refs={"cdc:UCOD"})(_strategy()) == []
    # time-to-event models need a time axis
    p = strategy_validator(_gap(), sources)(_strategy(model_class=ModelClass.COX_PROPORTIONAL_HAZARDS, offset=None))
    assert any("time_scale" in x for x in p)
    assert (
        strategy_validator(_gap(), sources)(
            _strategy(model_class=ModelClass.COX_PROPORTIONAL_HAZARDS, offset=None, time_scale=REF("AGED"))
        )
        == []
    )


def test_all_refs_deduplicated():
    s = _strategy(covariates=[REF("CIG_REC")])
    keys = [r.key() for r in s.all_refs()]
    assert len(keys) == len(set(keys))


def test_source_groups_and_restriction(sources):
    from mmf.components.common import allowed_refs_text, mapped_keys, source_groups
    from mmf.schemas import ConceptMapping, SchemaMap

    groups = source_groups(sources, max_vars=3)
    assert len(groups) == 3 and sum(len(g["cdc"].variables) for g in groups) == 7
    smap = SchemaMap(
        mappings=[
            ConceptMapping(concept="sex", source_id="cdc", variable="sex", compatibility="direct"),
            ConceptMapping(concept="x", source_id="cdc", variable=None, compatibility="none"),
        ]
    )
    assert mapped_keys(smap) == {"cdc:SEX"}
    assert allowed_refs_text(sources, only=mapped_keys(smap)) == "(cdc, SEX)"


BATCH = [Concept("bed sharing", "exposure", "o"), Concept("infant sex", "effect_modifier", "o")]


def test_canonical_concept():
    assert canonical_concept("bed sharing", BATCH) == "bed sharing"
    assert canonical_concept("Bed Sharing", BATCH) == "bed sharing"
    assert canonical_concept("Bed sharing as exposure", BATCH) == "bed sharing"
    assert canonical_concept("infant sex as an effect modifier", BATCH) == "infant sex"
    assert canonical_concept("infant sex as effect_modifier", BATCH) == "infant sex"
    assert canonical_concept("bed sharing as outcome", BATCH) is None  # not the role it was sent with
    assert canonical_concept("Sex as stratifier", BATCH) is None
    assert canonical_concept("adult neurogenesis", BATCH) is None


def test_map_validator_rejects_unknown_concept(sources):
    def m(concept):
        return SchemaMap(
            mappings=[
                ConceptMapping(concept="bed sharing", source_id="cdc", variable=None, compatibility="none"),
                ConceptMapping(concept=concept, source_id="cdc", variable="SEX", compatibility="direct"),
            ]
        )

    check = map_validator(sources, BATCH)
    assert check(m("Infant sex")) == []
    assert check(m("sex of the infant")) == [
        "concept 'sex of the infant' was not in the list; copy the concept name exactly as given",
        "no row for 'infant sex' / cdc; return at least one row for every concept in every data source "
        "(variable null and compatibility 'none' when nothing matches)",
    ]


def test_map_validator_rejects_misfiled_duplicate_rows(sources):
    # 2026-11-10: the model filed the 'sex' rows under 'sex (male, female)', doubling one concept and
    # leaving the other unmapped; both used to pass with only a warning
    batch = [Concept("sex (male, female)", "stratifier", "o"), Concept("sex", "stratifier", "o")]
    row = ConceptMapping(concept="sex (male, female)", source_id="cdc", variable="SEX", compatibility="direct")
    problems = map_validator(sources, batch)(SchemaMap(mappings=[row, row.model_copy()]))
    assert problems == [
        "duplicate rows for 'sex (male, female)' / cdc / SEX; give each concept, source and variable only once, "
        "under the concept name it belongs to",
        "no row for 'sex' / cdc; return at least one row for every concept in every data source "
        "(variable null and compatibility 'none' when nothing matches)",
    ]
    fixed = [row, row.model_copy(update={"concept": "sex"})]
    assert map_validator(sources, batch)(SchemaMap(mappings=fixed)) == []


def test_map_validator_duplicates_count_after_split_and_canonicalization(sources):
    batch = [Concept("bed sharing", "exposure", "o")]
    rows = [
        ConceptMapping(concept="bed sharing", source_id="cdc", variable="SEX, MAGER9", compatibility="proxy"),
        ConceptMapping(concept="Bed sharing as exposure", source_id="cdc", variable="mager9", compatibility="proxy"),
    ]
    (problem,) = map_validator(sources, batch)(SchemaMap(mappings=rows))
    assert problem.startswith("duplicate rows for 'bed sharing' / cdc / mager9;")


def test_map_validator_rejects_empty_mappings(sources):
    # a summaries-only answer passed validation on 2026-11-09 because `mappings` had a default
    assert map_validator(sources, BATCH)(SchemaMap(source_summaries={"cdc": "s"})) == [
        "no mappings were returned; return one mapping per concept per data source listed"
    ]


def test_map_validator_multi_variable_rows(sources):
    def one(variable):
        row = ConceptMapping(concept="bed sharing", source_id="cdc", variable=variable, compatibility="proxy")
        return map_validator(sources)(SchemaMap(mappings=[row]))

    assert one("SEX, MAGER9") == []
    assert one("SEX; MAGER9") == []
    (problem,) = one("SEX, NOPE")
    assert "'NOPE' not documented in cdc" in problem and "one variable name per mapping" in problem
    assert "'SEX'" not in problem
    assert one("NOPE") == ["mapping for 'bed sharing': 'NOPE' is not a documented variable in cdc"]
