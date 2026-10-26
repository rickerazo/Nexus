"""Provenance for one pipeline run."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class InputRecord(BaseModel):
    path: str
    sha256: str
    role: str = Field(description="manuscript | codebook")


class LLMCallRecord(BaseModel):
    stage: str
    prompt_name: str
    prompt_sha256: str
    model: str
    model_digest: str | None
    seed: int
    temperature: float
    attempts: int
    ok: bool
    log_file: str


class RunManifest(BaseModel):
    run_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    mmf_version: str
    config_sha256: str
    backend: str
    model: str
    seed: int
    temperature: float
    inputs: list[InputRecord] = Field(default_factory=list)
    calls: list[LLMCallRecord] = Field(default_factory=list)
    stage_hashes: dict[str, str] = Field(default_factory=dict, description="stage -> sha256 of its inputs (cache key).")
