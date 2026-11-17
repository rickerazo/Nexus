"""Local backend via Ollama (default). Uses schema-constrained decoding and a fixed seed."""

from __future__ import annotations

from typing import Any

import ollama

from mmf.llm.base import LLMResponse


class OllamaClient:
    backend = "ollama"

    def __init__(
        self,
        model: str,
        host: str = "http://localhost:11434",
        num_ctx: int = 32768,
        max_output_tokens: int = 8192,
    ) -> None:
        self.model = model
        self.num_ctx = num_ctx
        self.max_output_tokens = max_output_tokens
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
        self,
        system: str,
        user: str,
        json_schema: dict[str, Any],
        *,
        seed: int,
        temperature: float,
        history: list[dict[str, str]] | None = None,
    ) -> LLMResponse:
        return self._chat(system, user, json_schema, seed=seed, temperature=temperature, history=history)

    def complete_text(self, system: str, user: str, *, seed: int, temperature: float) -> LLMResponse:
        return self._chat(system, user, None, seed=seed, temperature=temperature, history=None)

    def _chat(
        self,
        system: str,
        user: str,
        json_schema: dict[str, Any] | None,
        *,
        seed: int,
        temperature: float,
        history: list[dict[str, str]] | None,
    ) -> LLMResponse:
        messages = [{"role": "system", "content": system}, *(history or []), {"role": "user", "content": user}]
        resp = self._client.chat(
            model=self.model,
            messages=messages,
            format=json_schema,
            options={
                "seed": seed,
                "temperature": temperature,
                "num_ctx": self.num_ctx,
                "num_predict": self.max_output_tokens,
            },
            keep_alive="30m",
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
            truncated=(resp.done_reason == "length"),
        )


class OllamaEmbedder:
    """Local embeddings via Ollama (e.g. mxbai-embed-large). Requires `ollama pull <model>`."""

    def __init__(self, model: str, host: str = "http://localhost:11434", batch_size: int = 64) -> None:
        self.model = model
        self.batch_size = batch_size
        self._client = ollama.Client(host=host)
        self._digest: str | None = None

    def model_digest(self) -> str | None:
        if self._digest is None:
            for m in self._client.list().models:
                if m.model == self.model or (m.model or "").split(":")[0] == self.model.split(":")[0]:
                    self._digest = m.digest
                    break
        return self._digest

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            resp = self._client.embed(model=self.model, input=texts[i : i + self.batch_size], keep_alive="5m")
            out.extend(list(map(float, v)) for v in resp.embeddings)
        return out
