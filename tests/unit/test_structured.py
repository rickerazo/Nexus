"""The retry loop with a fake client: rejected output is re-prompted with the problems."""

from pathlib import Path

import pytest
from pydantic import BaseModel

from mmf.llm.base import LLMResponse
from mmf.llm.prompts import Prompt
from mmf.llm.structured import GenerationFailedError, generate


class Out(BaseModel):
    n: int


class FakeClient:
    backend, model = "fake", "fake-1"

    def __init__(self, answers):
        self.answers, self.calls = list(answers), []

    def model_digest(self):
        return "deadbeef"

    def complete_json(self, system, user, json_schema, *, seed, temperature):
        self.calls.append(user)
        return LLMResponse(text=self.answers.pop(0), model=self.model)


PROMPT = Prompt(name="p", system="s", user_template="u", sha256="0")


def test_retry_feeds_back_problems(tmp_path: Path):
    client = FakeClient(['{"n": 1}', '{"n": 2}'])
    obj, rec = generate(
        client,
        PROMPT,
        "go",
        Out,
        stage="t",
        seed=0,
        temperature=0,
        validators=[lambda o: [] if o.n == 2 else ["n must be 2"]],
        log_dir=tmp_path,
    )
    assert obj.n == 2 and rec.attempts == 2 and rec.ok and rec.model_digest == "deadbeef"
    assert "n must be 2" in client.calls[1]
    assert list(tmp_path.glob("*_t.json"))


def test_retry_also_feeds_back_earlier_problems():
    # 2026-11-11 smoke D: shown only the latest problem, the model alternated between two mistakes
    client = FakeClient(['{"n": 1}', '{"n": 3}', '{"n": 2}'])

    def check(o):
        return {1: ["n must not be 1"], 3: ["n must not be 3"]}.get(o.n, [])

    obj, rec = generate(client, PROMPT, "go", Out, stage="t", seed=0, temperature=0, validators=[check])
    assert obj.n == 2 and rec.attempts == 3
    assert "Earlier answers" not in client.calls[1]
    latest, earlier = client.calls[2].split("Earlier answers were also rejected")
    assert "n must not be 3" in latest and "n must not be 1" not in latest
    assert "n must not be 1" in earlier


def test_unparseable_then_failure():
    client = FakeClient(["not json", '{"n": "x"}'])
    with pytest.raises(GenerationFailedError) as e:
        generate(client, PROMPT, "go", Out, stage="t", seed=0, temperature=0, max_retries=1)
    assert e.value.attempts == 2


def test_cloud_backend_requires_explicit_opt_in():
    from mmf.llm.structured import make_client

    with pytest.raises(PermissionError):
        make_client("openai_compatible", "m", ollama_host="x", num_ctx=1, api_key="k")
    with pytest.raises(RuntimeError, match="MMF_API_KEY"):
        make_client("openai_compatible", "m", ollama_host="x", num_ctx=1, allow_cloud=True, api_key=None)


def test_settings_ignore_key_files(monkeypatch, tmp_path):
    from mmf.config import Settings

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("MMF_API_KEY=should-not-load\nOPENAI_API_KEY=nope\n")
    monkeypatch.delenv("MMF_API_KEY", raising=False)
    assert Settings().api_key is None


def test_truncated_output_is_rejected_and_reprompted(tmp_path: Path):
    """A response cut at the output-token cap is never parsed; the retry asks for a shorter answer."""

    class TruncatingClient(FakeClient):
        def complete_json(self, system, user, json_schema, *, seed, temperature):
            self.calls.append(user)
            text = self.answers.pop(0)
            return LLMResponse(text=text, model=self.model, truncated=(text == "CUT"))

    client = TruncatingClient(["CUT", '{"n": 1}'])
    obj, rec = generate(client, PROMPT, "go", Out, stage="t", seed=0, temperature=0, log_dir=tmp_path)
    assert obj.n == 1 and rec.attempts == 2
    assert "cut off" in client.calls[1]


def test_component_a_chunk_schemas_cap_list_sizes():
    from mmf.components.a_decompose import MAX_CLAIMS_PER_CHUNK, MAX_VARIABLES_PER_CHUNK, ChunkClaims, ChunkProfile

    assert ChunkClaims.model_json_schema()["properties"]["claims"]["maxItems"] == MAX_CLAIMS_PER_CHUNK
    assert ChunkProfile.model_json_schema()["properties"]["variables"]["maxItems"] == MAX_VARIABLES_PER_CHUNK


def test_component_a_chunk_schemas_require_every_field():
    """Root cause of the claims-only Component A outputs: a grammar-constrained decoder may omit any key that
    is not `required`. Every LLM-facing field must stay required."""
    from mmf.components.a_decompose import ChunkClaims, ChunkProfile
    from mmf.components.b_schema_map import MappingOut, SchemaMapOut
    from mmf.schemas.strategy import OutcomeSpec, Strategy

    for model in (ChunkProfile, ChunkClaims, SchemaMapOut, MappingOut, Strategy, OutcomeSpec):
        schema = model.model_json_schema()
        assert set(schema["required"]) == set(schema["properties"]), model.__name__


def test_salvage_prunes_failing_items_on_final_attempt_only(tmp_path: Path):
    class Items(BaseModel):
        xs: list[int]

    def bad_evens(o):
        return [f"item {x}: must be odd" for x in o.xs if x % 2 == 0]

    def salvage(o, problems):
        bad = {int(p.split()[1].rstrip(":")) for p in problems}
        return Items(xs=[x for x in o.xs if x not in bad]), [f"item {x}" for x in o.xs if x in bad]

    client = FakeClient(['{"xs": [1, 2]}', '{"xs": [1, 4]}'])
    obj, rec = generate(
        client,
        PROMPT,
        "go",
        Items,
        stage="t",
        seed=0,
        temperature=0,
        validators=[bad_evens],
        max_retries=1,
        salvage=salvage,
        log_dir=tmp_path,
    )
    assert obj.xs == [1] and rec.ok and rec.attempts == 2 and rec.dropped == ["item 4"]
    assert len(client.calls) == 2  # the first failure was re-prompted, not salvaged


def test_component_a_salvage_drops_named_claims_and_variables():
    from mmf.components.a_decompose import ChunkClaims, ChunkProfile, drop_ungrounded
    from mmf.schemas.manuscript import Claim, VariableMention

    claims = ChunkClaims(
        claims=[
            Claim(id="C1", kind="finding", statement="a", quote="q", page=1),
            Claim(id="C2", kind="finding", statement="b", quote="q", page=1),
        ]
    )
    pruned, dropped = drop_ungrounded(claims, ["claim C2: not verbatim ..."])
    assert [c.id for c in pruned.claims] == ["C1"] and dropped == ["claim C2: b"]

    profile = ChunkProfile(
        research_questions=[],
        data_sources_used=[],
        designs=[],
        model_classes=[],
        variables=[
            VariableMention(concept="sex", role="exposure", operationalization="o", quote="q", page=1),
            VariableMention(concept="age", role="covariate", operationalization="a", quote="q", page=1),
        ],
    )
    pruned_p, dropped_p = drop_ungrounded(profile, ["variable 'sex': not verbatim ..."])
    assert [v.concept for v in pruned_p.variables] == ["age"] and dropped_p == ["variable 'sex': o"]
