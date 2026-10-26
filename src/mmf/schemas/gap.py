"""Component C output: explicit, testable knowledge gaps."""

from __future__ import annotations

from pydantic import BaseModel, Field

from mmf.schemas.dataset import VariableRef


class KnowledgeGap(BaseModel):
    id: str = Field(description="G1, G2, ...")
    statement: str = Field(description="One-sentence, testable statement of what is not yet known.")
    rationale: str = Field(description="Why this follows from the manuscripts' findings and limitations.")
    prior_art: str = Field(description="What the input manuscripts already tested that is adjacent to this gap.")
    supporting_claim_ids: list[str] = Field(description="Claim ids from Component A that motivate the gap.")
    required_concepts: list[str] = Field(description="Concepts that must be measurable to address the gap.")
    required_variables: list[VariableRef] = Field(
        description="Codebook variables (from Component B) that operationalize the concepts."
    )


class GapSet(BaseModel):
    gaps: list[KnowledgeGap] = Field(default_factory=list)
