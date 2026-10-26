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
