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
    assert "period 2010-2019 is outside prams's coverage 2016-2021" in problems
    # a case-only design cannot talk about risk
    co = c_narrow.grounding_validator(DESIGNS["case_only"], ROLES, SPECS, {"m.C1"})
    p = co(_answer(statement="Does gestation modify SUID risk?", reference_sources=[], variables=["ncfrp:GEST"]))
    assert any("cannot estimate incidence or risk" in x for x in p)
    # not groundable: only the reason is checked
    assert check(_answer(groundable=False, why_not="No source records the exposure among the cases at all.")) == []
    assert check(_answer(groundable=False, why_not="no")) != []


def test_answer_model_restricts_sources_and_variables():
    model = c_narrow.answer_model(ROLES, ["ncfrp:SMOKE", "prams:WT"])
    schema = json.dumps(model.model_json_schema())
    assert '"enum": ["ncfrp:SMOKE", "prams:WT"]' in schema
    ok = _answer(variables=["ncfrp:SMOKE", "prams:WT"]).model_dump_json()
    assert model.model_validate_json(ok).variables == ["ncfrp:SMOKE", "prams:WT"]
    with pytest.raises(pydantic.ValidationError):
        model.model_validate_json(_answer(variables=["ncfrp:NOPE"]).model_dump_json())
    with pytest.raises(pydantic.ValidationError):
        model.model_validate_json(_answer(case_sources=["prams"]).model_dump_json())


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
    bad = _answer(variables=["ncfrp:SMOKE"]).model_dump_json()  # missing the weight and a prams variable
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
