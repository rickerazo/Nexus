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

    def __init__(self, model: str, api_key: str | None, base_url: str | None = None) -> None:
        if not api_key:
            raise RuntimeError("cloud backend needs MMF_API_KEY (an institutional credential), none is set")
        self.model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)

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
