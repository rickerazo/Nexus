"""Backend-agnostic LLM interface. All components call `structured.generate`, never a backend."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    text: str
    model: str
    model_digest: str | None = None
    usage: dict[str, Any] = Field(default_factory=dict)
    truncated: bool = Field(default=False, description="True if the backend stopped at the output-token limit.")


class LLMClient(Protocol):
    backend: str
    model: str

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
        """Return a JSON document conforming (as far as the backend can enforce) to `json_schema`. `history` holds
        earlier turns of the same conversation (user and assistant messages) between the system message and `user`."""
        ...

    def complete_text(self, system: str, user: str, *, seed: int, temperature: float) -> LLMResponse:
        """Free-text answer (the reasoning turn of a two-turn call)."""
        ...

    def model_digest(self) -> str | None:
        """A stable identifier of the exact model weights, if the backend exposes one."""
        ...


class Embedder(Protocol):
    """Text embeddings for independent cross-checks (never for generation). Local backends only."""

    model: str

    def embed(self, texts: list[str]) -> list[list[float]]:
        """One vector per text, in order."""
        ...

    def model_digest(self) -> str | None:
        """A stable identifier of the exact model weights, if the backend exposes one."""
        ...
