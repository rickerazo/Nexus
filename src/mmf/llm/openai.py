"""OpenAI backend. Kept for head-to-head evaluation against the local backend.

Never send restricted documents through this backend.
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from mmf.llm.base import LLMResponse


class OpenAIClient:
    backend = "openai"

    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model = model
        self._client = OpenAI(api_key=api_key)

    def model_digest(self) -> str | None:
        return None  # OpenAI exposes no weight-level identifier; `system_fingerprint` is logged per call.

    def complete_json(
        self, system: str, user: str, json_schema: dict[str, Any], *, seed: int, temperature: float
    ) -> LLMResponse:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "output", "schema": json_schema, "strict": False},
            },
            seed=seed,
            temperature=temperature,
        )
        usage = resp.usage.model_dump() if resp.usage else {}
        usage["system_fingerprint"] = resp.system_fingerprint
        return LLMResponse(text=resp.choices[0].message.content or "", model=self.model, usage=usage)
