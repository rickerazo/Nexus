"""C redesign steps C2-C5 (dedupe, two-turn grounding, scoring, review), with fake clients and a keyword embedder."""

import json

import pydantic
import pytest
from tests.unit.test_crosscheck import KeywordEmbedder

from mmf.components import c_narrow
from mmf.components.b_crosscheck import VectorCache
from mmf.components.c_ideas import DESIGNS
from mmf.config import SourceSpec
from mmf.llm.base import LLMResponse
from mmf.schemas.dataset import DataSource, Variable
from mmf.schemas.ideas import (
    Candidate,
    DataInventory,
    GroundingAnswer,
    IdeaPool,
    ImportanceRating,
    InventoryDomain,
)
from mmf.schemas.manuscript import Claim, ManuscriptDecomposition

ROLES = {"ncfrp": ["case"], "prams": ["reference"], "natl": ["denominator"]}
SPECS = {
    "ncfrp": SourceSpec(id="ncfrp", path="x", roles=["case"], period=(2004, 2019)),
    "prams": SourceSpec(id="prams", path="x", roles=["reference"], period=(2016, 2021), weight_variable="WT"),
    "natl": SourceSpec(id="natl", path="x", roles=["denominator"], period=(2015, 2015)),
}


def _vectors():
    return VectorCache(KeywordEmbedder(), None).vectors


def _sources():
    def src(sid, *vs):
        return DataSource(id=sid, title=sid, document_path="p", document_sha256="0", variables=list(vs))

    return {
        "ncfrp": src(
            "ncfrp",
            Variable(name="SMOKE", label="Mother smoked", levels=["1 = Yes", "2 = No"]),
            Variable(name="SEXINF", label="Infant sex", levels=["1 = M"]),
            Variable(name="GEST", label="Gestation weeks"),
        ),
        "prams": src(
            "prams",
            Variable(name="SMK", label="Smoked in last 3 months", levels=["1 = Yes"]),
            Variable(name="WT", label="Analysis weight", type="continuous"),
        ),
        "natl": src("natl", Variable(name="SEX", label="Sex of infant", levels=["M", "F"])),
    }


def _cand(i, q, design="case_population", case=("ncfrp",), ref=("prams",), domains=()):
    return Candidate(
        id=f"I{i}",
        design=design,
        seed=0,
        model="m",
        question=q,
        comparison="cases vs population",
        why_open="w",
        case_sources=list(case),
        reference_sources=list(ref),
        denominator_sources=[],
        domains=list(domains),
        data="d",
    )


def _dec():
    return ManuscriptDecomposition(
        manuscript_id="m",
        title="Mini",
        document_sha256="0",
        claims=[
            Claim(id="m.C1", kind="finding", statement="Smoking raises SUID.", quote="q"),
            Claim(id="m.C2", kind="method", statement="Poisson model.", quote="q"),
            Claim(id="m.C3", kind="limitation", statement="Gestation was self-reported.", quote="q"),
        ],
    )


def _answer(**kw):
    base = dict(
        groundable=True,
        why_not="",
        statement="Is the proportion of smoking among cases higher than its weighted prevalence?",
        rationale="r",
        prior_art="m.C1 tested smoking as a risk factor in a rate model, but never against weighted population "
        "prevalence among mothers of live births.",
        supporting_claim_ids=["m.C1"],
        case_sources=["ncfrp"],
        reference_sources=["prams"],
        denominator_sources=[],
        period_start=2016,
        period_end=2019,
        required_concepts=["smoking"],
        variables=["ncfrp:SMOKE", "prams:SMK", "prams:WT"],
        cannot_establish="Causation; no individual linkage.",
    )
    base.update(kw)
    return GroundingAnswer(**base)


def test_dedupe_groups_near_duplicates_in_pool_order():
    pool = IdeaPool(
        candidates=[
            _cand(1, "smok smok among cases?"),
            _cand(2, "gestation among cases?"),
            _cand(3, "smok smok smok among cases again?"),
        ]
    )
    d = c_narrow.dedupe(pool, _vectors(), threshold=0.95)
    assert [(g.representative, g.members) for g in d.groups] == [("I1", ["I1", "I3"]), ("I2", ["I2"])]
    assert d.groups[0].max_similarity >= 0.95 and d.threshold == 0.95


def test_grounding_validator_enforces_the_design_checks():
    check = c_narrow.grounding_validator(DESIGNS["case_population"], ROLES, SPECS, {"m.C1", "m.C3"})
    assert check(_answer()) == []
    problems = " | ".join(
        check(
            _answer(
                variables=["ncfrp:SMOKE", "prams:SMK", "natl:SEX"],
                period_start=2010,
                period_end=2019,
            )
        )
    )
    assert "needs its survey weight: add prams:WT" in problems
    assert "natl:SEX is from natl, which is not listed" in problems
    assert "coverage" not in problems  # the years held are never checked
    assert any("in the future" in x for x in check(_answer(period_end=2999)))
    # a case-only design cannot talk about risk
    co = c_narrow.grounding_validator(DESIGNS["case_only"], ROLES, SPECS, {"m.C1"})
    p = co(_answer(statement="Does gestation modify SUID risk?", reference_sources=[], variables=["ncfrp:GEST"]))
    assert any("cannot estimate incidence or risk" in x for x in p)
    # not groundable: only the reason is checked
    assert check(_answer(groundable=False, why_not="No source records the exposure among the cases at all.")) == []
    assert check(_answer(groundable=False, why_not="no")) != []
    # ... and must not rest on the years held
    years = check(_answer(groundable=False, why_not="PRAMS Phase 8 does not cover 2015, so no common period exists."))
    assert years == [c_narrow.YEARS_FEEDBACK]


def test_years_not_held_are_recorded_not_rejected():
    a = _answer(
        denominator_sources=["natl"],
        variables=["ncfrp:SMOKE", "prams:SMK", "prams:WT", "natl:SEX"],
        period_start=2014,
        period_end=2023,
    )
    check = c_narrow.grounding_validator(DESIGNS["case_population"], ROLES, SPECS, {"m.C1"}, max_year=2025)
    assert check(a) == []
    assert c_narrow.years_to_acquire(a, SPECS) == [
        "ncfrp: 2020-2023 (held 2004-2019)",
        "prams: 2014-2015, 2022-2023 (held 2016-2021)",
        "natl: 2014, 2016-2023 (held 2015-2015)",
    ]
    assert c_narrow.years_to_acquire(_answer(), SPECS) == []


def test_bookkeeping_is_fixed_on_the_final_attempt():
    check = c_narrow.grounding_validator(DESIGNS["case_population"], ROLES, SPECS, {"m.C1", "m.C3"})
    a = _answer(variables=["ncfrp:SMOKE", "prams:SMK"], supporting_claim_ids=["m.C1", "m.C3"])
    problems = check(a)
    assert any("survey weight" in p for p in problems) and any("m.C3 is not discussed" in p for p in problems)
    fixed, notes = c_narrow.fix_bookkeeping(SPECS)(a, problems)
    assert check(fixed) == [] and fixed.variables[-1] == "prams:WT" and fixed.supporting_claim_ids == ["m.C1"]
    assert notes == ["added survey weight prams:WT", "removed undiscussed supporting claim m.C3"]
    assert a.variables == ["ncfrp:SMOKE", "prams:SMK"]  # the original is not modified


def test_answer_model_restricts_sources_and_variables():
    model = c_narrow.answer_model(ROLES, ["ncfrp:SMOKE", "prams:WT"], ["m.C1", "m.C3"])
    schema = json.dumps(model.model_json_schema())
    assert '"enum": ["ncfrp:SMOKE", "prams:WT"]' in schema and '"enum": ["m.C1", "m.C3"]' in schema
    ok = _answer(variables=["ncfrp:SMOKE", "prams:WT"]).model_dump_json()
    assert model.model_validate_json(ok).variables == ["ncfrp:SMOKE", "prams:WT"]
    with pytest.raises(pydantic.ValidationError):
        model.model_validate_json(_answer(variables=["ncfrp:NOPE"]).model_dump_json())
    with pytest.raises(pydantic.ValidationError):
        model.model_validate_json(_answer(case_sources=["prams"]).model_dump_json())
    with pytest.raises(pydantic.ValidationError):
        model.model_validate_json(_answer(variables=["ncfrp:SMOKE"], supporting_claim_ids=["C10"]).model_dump_json())


def test_candidate_variables_include_nearest_cited_domain_and_weight():
    inv = DataInventory(
        domains=[InventoryDomain(source_id="ncfrp", name="Birth", summary="s", variables=["GEST"], used=[])]
    )
    idea = _cand(1, "smok among cases", domains=["ncfrp / Birth"])
    cands = c_narrow.candidate_variables(idea, inv, _sources(), SPECS, _vectors(), per_source=1, per_domain=1)
    keys = [f"{s}:{v.name}" for s, v in cands]
    assert keys[:2] == ["ncfrp:SMOKE", "ncfrp:GEST"]  # nearest first, then the cited domain's variable
    assert "prams:WT" in keys and "prams:SMK" in keys and "natl:SEX" in keys


class TwoTurnClient:
    backend, model = "fake", "fake-1"

    def __init__(self, texts, answers):
        self.texts, self.answers, self.json_calls, self.text_calls = list(texts), list(answers), [], []

    def model_digest(self):
        return "d"

    def complete_text(self, system, user, *, seed, temperature):
        self.text_calls.append((user, temperature))
        return LLMResponse(text=self.texts.pop(0), model=self.model)

    def complete_json(self, system, user, json_schema, *, seed, temperature, history=None):
        self.json_calls.append((user, temperature, history))
        return LLMResponse(text=self.answers.pop(0), model=self.model)


def test_ground_ideas_two_turns_drop_and_failure(tmp_path):
    pool = IdeaPool(
        candidates=[
            _cand(1, "smok among cases?"),
            _cand(2, "gestation among cases?", design="case_only", ref=()),
            _cand(3, "sex among cases?"),
        ]
    )
    deduped = c_narrow.dedupe(pool, _vectors(), threshold=0.999)
    assert len(deduped.groups) == 3
    good = _answer().model_dump_json()
    dropped = _answer(groundable=False, why_not="No case source records gestation in a usable way here.")
    bad = _answer(variables=["prams:SMK", "prams:WT"]).model_dump_json()  # the case source contributes nothing
    client = TwoTurnClient(["think 1", "think 2", "think 3"], [good, dropped.model_dump_json(), bad, bad])
    g, _ = c_narrow.ground_ideas(
        pool,
        deduped,
        [_dec()],
        DataInventory(),
        _sources(),
        SPECS,
        ROLES,
        "ROLES",
        client,
        _vectors(),
        per_source=3,
        per_domain=2,
        seed=0,
        reason_temperature=0.7,
        temperature=0.0,
        max_retries=1,
        log_dir=None,
        checkpoint_dir=tmp_path,
    )
    assert [x.id for x in g.gaps] == ["G1"] and g.gaps[0].idea_id == "I1" and g.gaps[0].reasoning == "think 1"
    assert [v.key() for v in g.gaps[0].required_variables] == ["ncfrp:SMOKE", "prams:SMK", "prams:WT"]
    assert [d.idea_id for d in g.dropped] == ["I2"] and g.failed_calls == ["C_ground_I3"]
    first_user, temp, history = client.json_calls[0]
    assert temp == 0.0 and history[1] == {"role": "assistant", "content": "think 1"}
    assert "m.C1 [finding]: Smoking raises SUID." in history[0]["content"]
    assert "Poisson" not in history[0]["content"] and client.text_calls[0][1] == 0.7
    assert "at least 1 case series source(s), at least 1 population reference source(s)" in first_user
    # rerun resumes both turns from checkpoints for the accepted and dropped ideas
    again = TwoTurnClient(["think 3"], [bad, bad])
    g2, _ = c_narrow.ground_ideas(
        pool,
        deduped,
        [_dec()],
        DataInventory(),
        _sources(),
        SPECS,
        ROLES,
        "ROLES",
        again,
        _vectors(),
        per_source=3,
        per_domain=2,
        seed=0,
        reason_temperature=0.7,
        temperature=0.0,
        max_retries=1,
        log_dir=None,
        checkpoint_dir=tmp_path,
    )
    # the failed idea's reasoning turn was checkpointed too: only its JSON turn is asked again
    assert g2.gaps == g.gaps and again.text_calls == [] and len(again.json_calls) == 2


def test_scores_and_selection_rule():
    srcs = _sources()
    from mmf.schemas.dataset import VariableRef
    from mmf.schemas.ideas import GroundedGap

    def gap(i, statement, variables):
        return GroundedGap(
            id=f"G{i}",
            statement=statement,
            rationale="r",
            prior_art="p",
            supporting_claim_ids=[],
            required_concepts=[],
            required_variables=[VariableRef(source_id=s, name=n) for s, n in variables],
            idea_id=f"I{i}",
            design="case_population",
            case_sources=["ncfrp"],
            reference_sources=[],
            denominator_sources=[],
            period_start=2016,
            period_end=2019,
            cannot_establish="c",
            reasoning="t",
        )

    gaps = [
        gap(1, "smok smok", [("ncfrp", "SMOKE")]),
        gap(2, "gestation neuron", [("ncfrp", "SMOKE"), ("ncfrp", "GEST")]),  # GEST has no levels or type
        gap(3, "gestation neuron neuron", [("ncfrp", "SMOKE")]),
        gap(4, "neuron", [("ncfrp", "SMOKE")]),
    ]
    assert c_narrow.feasibility(gaps[1], srcs) == 0.5
    ratings = {f"G{i}": ImportanceRating(reason="r", importance=imp) for i, imp in ((1, 4), (2, 4), (3, 4), (4, 2))}
    sl = c_narrow.shortlist(gaps, srcs, [_dec()], ratings, _vectors(), size=2, min_importance=3, max_similarity=0.9)
    by = {s.gap_id: s for s in sl.scores}
    assert by["G1"].nearest_claim == "m.C1" and by["G1"].novelty < by["G3"].novelty
    assert by["G4"].skipped_reason == "importance 2 < 3"
    assert {s.gap_id for s in sl.scores if s.shortlisted} == {"G3", "G1"}
    assert by["G2"].skipped_reason == "too similar to G3"
    md = c_narrow.review_markdown(IdeaPool(), c_narrow.dedupe(IdeaPool(), _vectors(), 0.9), _grounding(gaps), sl)
    assert "## [ ] G3 (case_population, from I3) gestation neuron neuron" in md and "importance 2 < 3" in md


def _grounding(gaps):
    from mmf.schemas.ideas import Grounding

    return Grounding(gaps=gaps)


def test_c3_and_c4_prompts_are_primed():
    from mmf.llm.prompts import load_primed_prompt

    for name in ("c_ground", "c_ground_answer", "c_importance"):
        p = load_primed_prompt(name, "ROLES")
        assert p.system.rstrip().endswith("ROLES")


def test_more_bookkeeping_is_fixed_but_design_needs_still_fail():
    claims = {"m.C1", "m.C3", "x.C3"}
    check = c_narrow.grounding_validator(DESIGNS["case_population"], ROLES, SPECS, claims)
    fix = c_narrow.fix_bookkeeping(SPECS, claims)
    # a stray variable, an idle denominator is left alone (no variable needed), a cited but unlisted claim
    a = _answer(
        variables=["ncfrp:SMOKE", "prams:SMK", "prams:WT", "natl:SEX"],
        prior_art=_answer().prior_art + " See also m.C1 and m.C3.",
    )
    fixed, notes = fix(a, check(a))
    assert check(fixed) == [] and "natl:SEX" not in fixed.variables
    assert fixed.supporting_claim_ids == ["m.C1", "m.C3"]
    assert notes == ["dropped variable natl:SEX (source not listed)", "added cited claim m.C3"]
    # an ambiguous bare id is not guessed
    b = _answer(prior_art=_answer().prior_art + " Compare C3.")
    fixed_b, _ = fix(b, check(b))
    assert any("cites C3" in p for p in check(fixed_b))
    # a case source with no variable is dropped, and then the design lacks a case series: still fails
    c = _answer(variables=["prams:SMK", "prams:WT"])
    fixed_c, notes_c = fix(c, check(c))
    assert notes_c == ["dropped ncfrp as case series (no variable used)"]
    assert any("needs at least 1 case series" in p for p in check(fixed_c))
