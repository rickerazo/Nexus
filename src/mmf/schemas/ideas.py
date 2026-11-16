"""Component C redesign, steps C0 (data inventory) and C1 (idea generation).

C0 summarizes every documented variable into topic domains, so the gap finder sees all of the data and not only
the variables B mapped to manuscript concepts. C1 samples candidate research questions from six role-based designs at a
non-zero temperature. Neither output is used by D yet: grounding (C3) and scoring (C4) come next.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

MAX_DOMAINS_PER_BLOCK = 8


class BlockDomain(BaseModel):
    """One contiguous run of variables in a block, as returned by the model."""

    start: str = Field(description="Exact name of the first variable of this domain.")
    name: str = Field(description="Short topic name, 2-6 words.")
    summary: str = Field(description="One sentence naming what the variables in this domain measure.")


class BlockDomains(BaseModel):
    domains: list[BlockDomain] = Field(max_length=MAX_DOMAINS_PER_BLOCK)


class InventoryDomain(BaseModel):
    source_id: str
    name: str
    summary: str
    variables: list[str] = Field(description="Every variable in the domain, in document order.")
    used: list[str] = Field(description="Variables of this domain that B mapped to a manuscript concept.")


class DataInventory(BaseModel):
    domains: list[InventoryDomain] = Field(default_factory=list)


class Idea(BaseModel):
    """One candidate research question, as returned by the model. Every field is required (grammar decoding)."""

    question: str = Field(description="One-sentence research question.")
    comparison: str = Field(description="Who is compared with whom, in which period.")
    why_open: str = Field(description="Why it is unanswered and what answering it would change.")
    case_sources: list[str] = Field(description="source_ids used as case series (outcomes come only from these).")
    reference_sources: list[str] = Field(description="source_ids used as population reference (prevalence).")
    denominator_sources: list[str] = Field(description="source_ids used for the population at risk.")
    data: str = Field(description="Which domains and concepts of those sources it would use.")

    def by_role(self) -> dict[str, list[str]]:
        return {"case": self.case_sources, "reference": self.reference_sources, "denominator": self.denominator_sources}


class IdeaBatch(BaseModel):
    ideas: list[Idea]


class Candidate(Idea):
    id: str = Field(description="I1, I2, ... in generation order.")
    design: str
    seed: int
    model: str


class IdeaPool(BaseModel):
    candidates: list[Candidate] = Field(default_factory=list)
    failed_calls: list[str] = Field(default_factory=list, description="Calls with no valid output after retries.")
