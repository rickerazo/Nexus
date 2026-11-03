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


def test_component_a_chunk_schema_caps_list_sizes():
    from mmf.components.a_decompose import MAX_CLAIMS_PER_CHUNK, ChunkDecomposition

    props = ChunkDecomposition.model_json_schema()["properties"]
    assert props["claims"]["maxItems"] == MAX_CLAIMS_PER_CHUNK
    assert props["variables"]["maxItems"] == MAX_CLAIMS_PER_CHUNK
