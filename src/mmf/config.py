"""Run configuration and environment settings."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Backend = Literal["ollama", "openai_compatible"]
SourceRole = Literal["case", "denominator", "reference"]


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
    llm_extract: bool = Field(
        default=True,
        description="Run the LLM enrichment pass (pass 2). False = deterministic pass only; use for "
        "tabular codebooks where the deterministic parser is complete, or to save time.",
    )
    denominator: bool = Field(
        default=False,
        description="True if this source's records are the population at risk (e.g. one record per live birth), so "
        "a rate model can use the count of its records per stratum as the denominator.",
    )
    population: str | None = Field(
        default=None,
        description="Who the records cover (e.g. 'infant deaths only; no births'). Shown to Component C so it can "
        "tell which sources can supply incidence denominators.",
    )
    roles: list[SourceRole] = Field(
        default_factory=list,
        description="What the source can play in a design: 'case' (a case series: outcomes come only from case "
        "sources), 'denominator' (the population at risk), 'reference' (exposure prevalence in the general "
        "population; never an outcome). Empty = a lookup list, not a dataset. `denominator: true` implies "
        "'denominator'.",
    )
    unit: str | None = Field(default=None, description="What one record is (e.g. 'one live birth').")
    years: str | None = Field(default=None, description="Period covered, as documented by the investigator.")
    geography: str | None = Field(default=None, description="Geographic detail available, including none.")
    linkage: str | None = Field(default=None, description="What the records can be linked to, if anything.")
    weight_variable: str | None = Field(
        default=None, description="Survey weight that every prevalence from this source must use (e.g. WTANAL)."
    )
    missing: str | None = Field(default=None, description="How missing and don't-know answers are coded and handled.")

    @model_validator(mode="after")
    def _denominator_role(self) -> SourceSpec:
        if self.denominator and "denominator" not in self.roles:
            self.roles = [*self.roles, "denominator"]
        self.denominator = "denominator" in self.roles
        return self


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
    max_output_tokens: int = Field(
        default=8192,
        description="Hard cap on tokens generated per LLM call; a cut-off answer is rejected and re-prompted.",
    )
    max_retries: int = Field(default=3, description="Re-prompts after a validation failure.")
    n_gaps: int = 3
    b_max_vars_per_call: int = Field(
        default=600, description="Component B maps concepts against at most this many variables per LLM call."
    )
    b_max_mappings_per_call: int = Field(
        default=50,
        description="Component B asks for at most this many concept x source mappings per LLM call (~100 output "
        "tokens each), so a long concept list cannot hit max_output_tokens.",
    )
    b_crosscheck: bool = Field(
        default=True,
        description="Run the embedding cross-check on Component B's mappings (flags only; never changes B). "
        "Set false for the validators-off (L-) ablation.",
    )
    embed_model: str = Field(default="mxbai-embed-large", description="Local Ollama embedding model for B's check.")
    b_check_top_k: int = Field(default=10, description="An LLM mapping agrees if its variable is in the top k.")
    b_check_miss_threshold: float = Field(
        default=0.65,
        description="Cosine similarity at or above which a 'none' mapping with a strong embedding candidate is "
        "flagged as a possible miss. Provisional; see docs/architecture.md for its calibration.",
    )
    c_inventory_block_vars: int = Field(
        default=150, description="C0 summarizes at most this many consecutive variables per call into domains."
    )
    c_ideation_model: str | None = Field(
        default=None, description="Local model for C1 idea generation only; null = `model`."
    )
    c_ideation_temperature: float = Field(
        default=0.9,
        description="C1 samples at this temperature (other stages use `temperature`); diversity is the point of C1.",
    )
    c_ideation_seeds: list[int] = Field(default=[0, 1, 2], description="One C1 call per (lens, seed).")
    c_ideas_per_call: int = Field(default=5, description="Ideas requested from each C1 call.")
    out_dir: Path = Path("runs")
    cache_dir: Path = Path(".cache/documents")

    @classmethod
    def from_yaml(cls, path: Path | str) -> RunConfig:
        data = yaml.safe_load(Path(path).read_text())
        return cls.model_validate(data)

    def sha256(self) -> str:
        return hashlib.sha256(self.model_dump_json(exclude={"out_dir", "cache_dir"}).encode()).hexdigest()
