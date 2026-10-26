"""Run configuration and environment settings."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Backend = Literal["ollama", "openai_compatible"]


class Settings(BaseSettings):
    """Host settings and (optional) cloud API credentials.

    Read ONLY from explicit environment variables prefixed MMF_; no key file is loaded
    automatically. Cloud credentials must belong to the project (institutional), never a
    personal account, and are used only when a RunConfig sets `allow_cloud: true`.
    """

    model_config = SettingsConfigDict(env_prefix="MMF_", extra="ignore")
    ollama_host: str = "http://localhost:11434"
    api_key: str | None = None
    api_base_url: str | None = None  # OpenAI-compatible endpoint (institutional gateway, Azure, etc.)


class SourceSpec(BaseModel):
    id: str = Field(description="Slug used in VariableRef.source_id.")
    path: Path
    title: str | None = None


class RunConfig(BaseModel):
    """Everything that determines a run's outputs. Its sha256 is part of the run id."""

    manuscripts: list[Path]
    codebooks: list[SourceSpec]
    backend: Backend = "ollama"
    model: str = "qwen2.5:14b"
    allow_cloud: bool = Field(
        default=False,
        description="Must be true to use a non-local backend. Documents then leave the machine; "
        "only institutional credentials may be used and restricted documents must not be sent.",
    )
    seed: int = 0
    temperature: float = 0.0
    num_ctx: int = Field(default=32768, description="Context window to request from Ollama.")
    chunk_tokens: int = Field(default=12000, description="Max approx tokens per document chunk.")
    max_retries: int = Field(default=3, description="Re-prompts after a validation failure.")
    n_gaps: int = 3
    out_dir: Path = Path("runs")
    cache_dir: Path = Path(".cache/documents")

    @classmethod
    def from_yaml(cls, path: Path | str) -> RunConfig:
        data = yaml.safe_load(Path(path).read_text())
        return cls.model_validate(data)

    def sha256(self) -> str:
        return hashlib.sha256(self.model_dump_json(exclude={"out_dir", "cache_dir"}).encode()).hexdigest()
