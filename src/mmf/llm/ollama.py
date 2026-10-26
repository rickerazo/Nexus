"""Local backend via Ollama (default). Uses schema-constrained decoding and a fixed seed."""

from __future__ import annotations

from typing import Any

import ollama

from mmf.llm.base import LLMResponse


class OllamaClient:
    backend = "ollama"

    def __init__(self, model: str, host: str = "http://localhost:11434", num_ctx: int = 32768) -> None:
        self.model = model
        self.num_ctx = num_ctx
        self._client = ollama.Client(host=host)
        self._digest: str | None = None

    def model_digest(self) -> str | None:
        if self._digest is None:
            for m in self._client.list().models:
                if m.model == self.model or (m.model or "").startswith(self.model):
                    self._digest = m.digest
                    break
        return self._digest

    def complete_json(
        self, system: str, user: str, json_schema: dict[str, Any], *, seed: int, temperature: float
    ) -> LLMResponse:
        resp = self._client.chat(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            format=json_schema,
            options={"seed": seed, "temperature": temperature, "num_ctx": self.num_ctx},
        )
        usage = {
            "prompt_tokens": resp.prompt_eval_count,
            "completion_tokens": resp.eval_count,
            "total_duration_ns": resp.total_duration,
        }
        return LLMResponse(
            text=resp.message.content or "",
            model=self.model,
            model_digest=self.model_digest(),
            usage=usage,
        )
