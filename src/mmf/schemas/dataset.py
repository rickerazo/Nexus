"""Component B input/output: dataset documentation as structured variables."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class VariableType(StrEnum):
    BINARY = "binary"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    CONTINUOUS = "continuous"
    COUNT = "count"
    DATE = "date"
    TEXT = "text"
    UNKNOWN = "unknown"


class Variable(BaseModel):
    """One variable as documented in a codebook. `name` is the exact documented identifier."""

    name: str = Field(description="Exact variable name as printed in the codebook, e.g. MAGER9.")
    label: str = Field(description="Human-readable description from the codebook.")
    type: VariableType = VariableType.UNKNOWN
    levels: list[str] = Field(default_factory=list, description="Coded values with labels, e.g. '1 = Yes'.")
    years: list[int] = Field(
        default_factory=list,
        description="Years/phases in which the variable is available, if stated.",
    )
    page: int | None = Field(default=None, description="1-based page in the source document where defined.")
    notes: str = ""


class DataSource(BaseModel):
    """A dataset described by one documentation file (codebook, user guide, data dictionary)."""

    id: str = Field(description="Short slug, e.g. prams_p8_arf, cdc_linkco15.")
    title: str
    document_path: str
    document_sha256: str
    variables: list[Variable] = Field(default_factory=list)

    def lookup(self, name: str) -> Variable | None:
        key = name.strip().upper()
        for v in self.variables:
            if v.name.upper() == key:
                return v
        return None


class VariableRef(BaseModel):
    """A pointer to a variable in a specific source. Every ref must resolve via grounding."""

    source_id: str
    name: str

    def key(self) -> str:
        return f"{self.source_id}:{self.name.upper()}"


class ConceptMapping(BaseModel):
    """How one manuscript concept is (or is not) represented in one data source."""

    concept: str
    source_id: str
    variable: str | None = Field(default=None, description="Codebook variable name, or null if no equivalent.")
    compatibility: str = Field(description="One of: direct, proxy, derived, none.")
    rationale: str = ""


class SchemaMap(BaseModel):
    """Component B output: harmonized concept-to-variable map across all sources."""

    mappings: list[ConceptMapping] = Field(default_factory=list)
    source_summaries: dict[str, str] = Field(default_factory=dict, description="Per-source capability summary.")
