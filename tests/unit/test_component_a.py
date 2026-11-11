"""Component A's two-call flow and the empty-input gates, with a fake client (no LLM)."""

import json
import re

import pytest

from mmf.components.a_decompose import decompose, decomposition_problems
from mmf.components.b_schema_map import collect_concepts, map_schema
from mmf.llm.base import LLMResponse
from mmf.llm.structured import GenerationFailedError, StageInputError
from mmf.schemas import ManuscriptDecomposition
from mmf.schemas.manuscript import VariableMention

PCA_QUOTE = "We aligned infants by postconceptional age (gestational age at birth plus chronological age)."
SEX_QUOTE = "Male excess risk emerged only after 44 weeks postconceptional age."


def _var(concept, role, quote):
    return {"concept": concept, "role": role, "operationalization": "o", "quote": quote, "page": 1}


class SchemaRoutingClient:
    """Answers by the requested output schema: Component A profile/claims calls, or B schema maps."""

    backend, model = "fake", "fake-1"

    def __init__(self, profile=None, claims=None, schema_map=None):
        self.answers = {"profile": profile, "claims": claims, "map": schema_map}
        self.calls: list[tuple[str, str]] = []

    def model_digest(self):
        return "deadbeef"

    def complete_json(self, system, user, json_schema, *, seed, temperature):
        props = json_schema["properties"]
        kind = "claims" if "claims" in props else "profile" if "variables" in props else "map"
        self.calls.append((kind, user))
        answer = self.answers[kind]
        return LLMResponse(text=json.dumps(answer(user) if callable(answer) else answer), model=self.model)


def test_decompose_makes_profile_and_claims_calls_and_salvages(mini_manuscript_doc, tmp_path):
    profile = {
        "research_questions": ["When does male excess risk emerge?"],
        "data_sources_used": ["linked birth and infant death records"],
        "designs": ["population_incidence"],
        "model_classes": [],
        "variables": [
            _var("postconceptional age", "stratifier", PCA_QUOTE),
            _var("Postconceptional age", "stratifier", PCA_QUOTE),  # duplicate concept, other case
            _var("infant sex", "effect_modifier", SEX_QUOTE),
            _var("birth weight", "covariate", "Birth weight was recorded in grams for every infant."),  # ungrounded
        ],
    }
    claims = {"claims": [{"id": "C1", "kind": "finding", "statement": "s", "quote": SEX_QUOTE, "page": 1}]}
    client = SchemaRoutingClient(profile=profile, claims=claims)
    dec, recs = decompose(
        mini_manuscript_doc,
        "mini",
        client,
        seed=0,
        temperature=0,
        chunk_tokens=4000,
        max_retries=0,
        log_dir=tmp_path,
    )
    assert [k for k, _ in client.calls] == ["profile", "claims"]
    assert [r.stage for r in recs] == ["A_mini_0_profile", "A_mini_0_claims"]
    assert all(r.ok for r in recs)
    assert recs[0].dropped == ["variable 'birth weight': o"]
    assert [v.concept for v in dec.variables] == ["postconceptional age", "infant sex"]
    assert [c.id for c in dec.claims] == ["mini.C1"]
    assert dec.designs == ["population_incidence"] and dec.research_questions


def _dec(variables=(), claims=1, designs=(), models=()):
    from mmf.schemas import Claim

    return ManuscriptDecomposition(
        manuscript_id="m1",
        title="t",
        document_sha256="0" * 64,
        designs=list(designs),
        model_classes=list(models),
        variables=list(variables),
        claims=[Claim(id=f"m1.C{i}", kind="finding", statement="s", quote="q" * 20) for i in range(claims)],
    )


def test_decomposition_problems_fail_on_empty_and_warn_on_missing_design():
    errors, warnings = decomposition_problems(_dec(claims=0))
    assert any("no grounded variables" in e for e in errors) and any("no grounded claims" in e for e in errors)
    sex = VariableMention(concept="sex", role="exposure", operationalization="o", quote="q" * 20)
    errors, warnings = decomposition_problems(_dec(variables=[sex]))
    assert errors == [] and len(warnings) == 2
    assert decomposition_problems(_dec(variables=[sex], designs=["cohort"], models=["logistic_regression"])) == ([], [])


def test_schema_map_refuses_empty_concepts(sources):
    client = SchemaRoutingClient()
    with pytest.raises(StageInputError, match="no concepts to map"):
        map_schema([_dec()], sources, client, seed=0, temperature=0, max_retries=0, log_dir=None)
    assert client.calls == []


def test_schema_map_batches_concepts_and_dedupes(sources):
    vs = [
        VariableMention(concept=c, role="exposure", operationalization="o", quote="q" * 20)
        for c in ["Sex", "sex", "maternal smoking", "maternal age", "gestation", "age at death"]
    ]
    assert [c.name for c in collect_concepts([_dec(variables=vs)])] == [
        "Sex",
        "maternal smoking",
        "maternal age",
        "gestation",
        "age at death",
    ]

    def one_row_per_concept(user):
        sent = re.findall(r'^- "(.+?)" \(role', user, flags=re.M)
        rows = [
            {"concept": c, "source_id": "cdc", "variable": None, "compatibility": "none", "rationale": ""} for c in sent
        ]
        return {"mappings": rows, "source_summaries": {}}

    client = SchemaRoutingClient(schema_map=one_row_per_concept)
    _, recs, warnings = map_schema(
        [_dec(variables=vs)],
        sources,
        client,
        seed=0,
        temperature=0,
        max_retries=0,
        log_dir=None,
        max_mappings_per_call=2,
    )
    # 5 concepts, 1 source per group, 2 mappings per call -> 3 batches
    assert [r.stage for r in recs] == ["B_schema_map_0_0", "B_schema_map_0_1", "B_schema_map_0_2"]
    assert warnings == []
    assert '- "age at death" (role: exposure)' in client.calls[-1][1] and '"Sex"' not in client.calls[-1][1]


def test_schema_map_canonicalizes_names_and_rejects_missing_rows(sources):
    vs = [
        VariableMention(concept=c, role=r, operationalization="o", quote="q" * 20)
        for c, r in [("bed sharing", "exposure"), ("infant sex", "stratifier")]
    ]
    answer = {
        "mappings": [
            {
                "concept": "Bed sharing as exposure",
                "source_id": "cdc",
                "variable": None,
                "compatibility": "none",
                "rationale": "",
            }
        ],
        "source_summaries": {},
    }
    client = SchemaRoutingClient(schema_map=answer)
    # a (concept, source) pair without a row is rejected (it used to pass with a warning)
    with pytest.raises(GenerationFailedError, match="no row for 'infant sex' / cdc"):
        map_schema([_dec(variables=vs)], sources, client, seed=0, temperature=0, max_retries=0, log_dir=None)
    answer["mappings"].append(_row("Infant Sex", "SEX", "direct"))
    smap, _, warnings = map_schema(
        [_dec(variables=vs)], sources, client, seed=0, temperature=0, max_retries=0, log_dir=None
    )
    assert [m.concept for m in smap.mappings] == ["bed sharing", "infant sex"]
    assert warnings == ["B_schema_map_0_0: 2 concept names canonicalized to the names sent"]


def _row(concept, variable, compat="proxy"):
    return {"concept": concept, "source_id": "cdc", "variable": variable, "compatibility": compat, "rationale": "r"}


def test_schema_map_splits_multi_variable_rows(sources):
    vs = [VariableMention(concept="maternal smoking", role="exposure", operationalization="o", quote="q" * 20)]
    answer = {"mappings": [_row("maternal smoking", "CIG_REC, MAGER9")], "source_summaries": {}}
    smap, _, warnings = map_schema(
        [_dec(variables=vs)],
        sources,
        SchemaRoutingClient(schema_map=answer),
        seed=0,
        temperature=0,
        max_retries=0,
        log_dir=None,
    )
    assert [(m.variable, m.compatibility, m.rationale) for m in smap.mappings] == [
        ("CIG_REC", "proxy", "r"),
        ("MAGER9", "proxy", "r"),
    ]
    assert warnings == ["B_schema_map_0_0: 1 multi-variable rows split into one row per variable"]


def test_schema_map_checkpoints_each_call_and_resumes(sources, tmp_path):
    vs = [
        VariableMention(concept=c, role="exposure", operationalization="o", quote="q" * 20)
        for c in ["infant sex", "maternal age"]
    ]
    good = {"infant sex": _row("infant sex", "SEX", "direct"), "maternal age": _row("maternal age", "MAGER9")}
    fail_second = {"on": True}

    def answer(user):
        (c,) = re.findall(r'^- "(.+?)" \(role', user, flags=re.M)
        if c == "maternal age" and fail_second["on"]:
            return {"mappings": [_row(c, "NOPE")], "source_summaries": {}}
        return {"mappings": [good[c]], "source_summaries": {}}

    kw = dict(seed=0, temperature=0, max_retries=0, log_dir=None, max_mappings_per_call=1, salt="s")
    ckpt = tmp_path / "ckpt"
    client = SchemaRoutingClient(schema_map=answer)
    with pytest.raises(Exception, match="no valid output"):
        map_schema([_dec(variables=vs)], sources, client, checkpoint_dir=ckpt, **kw)
    assert len(list(ckpt.glob("B_schema_map_0_0_*.json"))) == 1  # the finished call survived the failure
    assert not list(ckpt.glob("B_schema_map_0_1_*.json"))

    fail_second["on"] = False
    client = SchemaRoutingClient(schema_map=answer)
    resumed, recs, warnings = map_schema([_dec(variables=vs)], sources, client, checkpoint_dir=ckpt, **kw)
    assert [r.stage for r in recs] == ["B_schema_map_0_1"] and len(client.calls) == 1
    assert "B: resumed 1 of 2 calls from checkpoint" in warnings

    fresh, _, _ = map_schema([_dec(variables=vs)], sources, SchemaRoutingClient(schema_map=answer), **kw)
    assert resumed == fresh
