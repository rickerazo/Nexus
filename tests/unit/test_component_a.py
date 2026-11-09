"""Component A's two-call flow and the empty-input gates, with a fake client (no LLM)."""

import json

import pytest

from mmf.components.a_decompose import decompose, decomposition_problems
from mmf.components.b_schema_map import collect_concepts, map_schema
from mmf.llm.base import LLMResponse
from mmf.llm.structured import StageInputError
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
        return LLMResponse(text=json.dumps(self.answers[kind]), model=self.model)


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
    client = SchemaRoutingClient(schema_map={"mappings": [], "source_summaries": {}})
    _, recs, _ = map_schema(
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
    assert '- "age at death" (role: exposure)' in client.calls[-1][1] and '"Sex"' not in client.calls[-1][1]


def test_schema_map_canonicalizes_names_and_warns_on_missing_rows(sources):
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
    smap, _, warnings = map_schema(
        [_dec(variables=vs)], sources, client, seed=0, temperature=0, max_retries=0, log_dir=None
    )
    assert [m.concept for m in smap.mappings] == ["bed sharing"]
    assert warnings == [
        "B_schema_map_0_0: 1 concept names canonicalized to the names sent",
        "B_schema_map_0_0: no row for 1 (concept, source) pair(s): infant sex / cdc",
    ]
