"""Run configuration and environment settings."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Backend = Literal["ollama", "openai"]


class Settings(BaseSettings):
    """Secrets and host settings. Loaded from the environment or ~/.config/nexus/.env."""

    model_config = SettingsConfigDict(
        env_file=(Path.home() / ".config" / "nexus" / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    openai_api_key: str | None = None
    ollama_host: str = "http://localhost:11434"


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
