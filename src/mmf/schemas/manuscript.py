"""Component A output: structured decomposition of one manuscript."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from mmf.validate.vocab import ModelClass, StudyDesign


class ClaimKind(StrEnum):
    FINDING = "finding"
    HYPOTHESIS = "hypothesis"
    METHOD = "method"
    LIMITATION = "limitation"
    FUTURE_WORK = "future_work"


class Claim(BaseModel):
    """A statement extracted from the manuscript, anchored to a verbatim quote."""

    id: str = Field(description="Stable id, e.g. C1, C2.")
    kind: ClaimKind
    statement: str = Field(description="Faithful paraphrase of the claim.")
    quote: str = Field(description="Verbatim span from the manuscript supporting the statement.")
    page: int | None = None


class VariableRole(StrEnum):
    OUTCOME = "outcome"
    EXPOSURE = "exposure"
    COVARIATE = "covariate"
    STRATIFIER = "stratifier"
    OFFSET = "offset"
    EFFECT_MODIFIER = "effect_modifier"


class VariableMention(BaseModel):
    """A concept the manuscript measured or modelled, and how it was operationalized."""

    concept: str = Field(description="Domain concept, e.g. 'postconceptional age'.")
    role: VariableRole
    operationalization: str = Field(description="How the manuscript measured/derived it.")
    quote: str
    page: int | None = None


class ManuscriptDecomposition(BaseModel):
    manuscript_id: str
    title: str
    document_sha256: str
    research_questions: list[str] = Field(default_factory=list)
    designs: list[StudyDesign] = Field(default_factory=list)
    model_classes: list[ModelClass] = Field(default_factory=list)
    data_sources_used: list[str] = Field(default_factory=list, description="Datasets named in the manuscript.")
    variables: list[VariableMention] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)

    def claims_of(self, kind: ClaimKind) -> list[Claim]:
        return [c for c in self.claims if c.kind == kind]
