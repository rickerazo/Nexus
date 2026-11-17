"""OpenAI-compatible cloud backend (OpenAI, Azure OpenAI, institutional gateways).

Requires an institutional credential in MMF_API_KEY and `allow_cloud: true` in the run config.
Never send restricted documents through this backend.
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from mmf.llm.base import LLMResponse


class OpenAICompatibleClient:
    backend = "openai_compatible"

    def __init__(
        self, model: str, api_key: str | None, base_url: str | None = None, max_output_tokens: int = 8192
    ) -> None:
        if not api_key:
            raise RuntimeError("cloud backend needs MMF_API_KEY (an institutional credential), none is set")
        self.model = model
        self.max_output_tokens = max_output_tokens
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def model_digest(self) -> str | None:
        return None  # OpenAI exposes no weight-level identifier; `system_fingerprint` is logged per call.

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
        fmt: Any = (
            {"type": "json_schema", "json_schema": {"name": "output", "schema": json_schema, "strict": False}}
            if json_schema is not None
            else {"type": "text"}
        )
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *(history or []), {"role": "user", "content": user}],  # type: ignore[list-item]
            response_format=fmt,
            seed=seed,
            temperature=temperature,
            max_tokens=self.max_output_tokens,
        )
        usage = resp.usage.model_dump() if resp.usage else {}
        usage["system_fingerprint"] = resp.system_fingerprint
        choice = resp.choices[0]
        return LLMResponse(
            text=choice.message.content or "",
            model=self.model,
            usage=usage,
            truncated=(choice.finish_reason == "length"),
        )
