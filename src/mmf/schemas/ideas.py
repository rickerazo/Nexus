"""Component C redesign, steps C0 (data inventory) and C1 (idea generation).

C0 summarizes every documented variable into topic domains, so the gap finder sees all of the data and not only
the variables B mapped to manuscript concepts. C1 samples candidate research questions from six role-based designs at a
non-zero temperature. Neither output is used by D yet: grounding (C3) and scoring (C4) come next.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from mmf.schemas.gap import KnowledgeGap

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


class DomainMatch(BaseModel):
    """A case-series domain and the most similar population-reference domain (embedding cosine), so C1 can see
    comparisons across roles beyond the concepts the manuscripts named."""

    case: str = Field(description="'source_id / domain name' of the case-series domain.")
    reference: str
    score: float
    case_new: bool = Field(description="No variable of the case domain is used by the manuscripts.")
    reference_new: bool


class Idea(BaseModel):
    """One candidate research question, as returned by the model. Every field is required (grammar decoding)."""

    question: str = Field(description="One-sentence research question.")
    comparison: str = Field(description="Who is compared with whom, in which period.")
    why_open: str = Field(description="Why it is unanswered and what answering it would change.")
    case_sources: list[str] = Field(description="source_ids used as case series (outcomes come only from these).")
    reference_sources: list[str] = Field(description="source_ids used as population reference (prevalence).")
    denominator_sources: list[str] = Field(description="source_ids used for the population at risk.")
    domains: list[str] = Field(description="Inventory domains used, each copied as 'source_id / domain name'.")
    data: str = Field(description="How those domains and concepts would be used.")

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


# ---- C2-C4 -------------------------------------------------------------------------------


class IdeaGroup(BaseModel):
    """C2: near-duplicate ideas; the representative is the first in pool order."""

    representative: str
    members: list[str] = Field(description="Every idea id in the group, the representative first.")
    max_similarity: float = Field(
        description="Highest cosine between the representative and another member (0 if alone)."
    )


class DedupedPool(BaseModel):
    groups: list[IdeaGroup] = Field(default_factory=list)
    threshold: float = 0.0


class GroundingAnswer(BaseModel):
    """C3 JSON turn, as returned by the model. Source, variable and design-specific enums are narrowed per call;
    every field is required (grammar decoding)."""

    groundable: bool = Field(description="False if these data cannot answer any version of the idea.")
    why_not: str = Field(description="If groundable is false: which data or design element is missing. Else ''.")
    statement: str = Field(description="One testable sentence that fits the design and the data.")
    rationale: str = Field(description="Why the question matters and why it is open.")
    prior_art: str = Field(
        description="The closest work the manuscripts tested, with claim ids, or 'none in the inputs'."
    )
    supporting_claim_ids: list[str] = Field(description="Claim ids the gap builds on; may be empty.")
    case_sources: list[str]
    reference_sources: list[str]
    denominator_sources: list[str]
    period_start: int = Field(description="First calendar year the question needs (may be outside the years held).")
    period_end: int = Field(description="Last calendar year the question needs (may be outside the years held).")
    required_concepts: list[str]
    variables: list[str] = Field(description="'source_id:NAME' of every variable used, from the candidate list.")
    cannot_establish: str = Field(description="What this design cannot establish (causation, individual linkage, ...).")

    def by_role(self) -> dict[str, list[str]]:
        return {"case": self.case_sources, "reference": self.reference_sources, "denominator": self.denominator_sources}


class GroundedGap(KnowledgeGap):
    """A C3 gap: a KnowledgeGap (what D consumes) plus the design, the sources by role, the period and the reasoning."""

    idea_id: str
    design: str
    case_sources: list[str]
    reference_sources: list[str]
    denominator_sources: list[str]
    period_start: int
    period_end: int
    cannot_establish: str
    reasoning: str = Field(description="The free-text reasoning turn, kept for review.")
    years_to_acquire: list[str] = Field(
        default_factory=list,
        description="Per source, the years of the gap's period not held yet (computed). Years held are a data "
        "holding, not a limitation: they never exclude a gap.",
    )
    salvaged: list[str] = Field(
        default_factory=list,
        description="Bookkeeping fixed in code on the final attempt (survey weight added, uncited claims removed).",
    )


class DroppedIdea(BaseModel):
    idea_id: str
    reason: str


class Grounding(BaseModel):
    gaps: list[GroundedGap] = Field(default_factory=list)
    dropped: list[DroppedIdea] = Field(default_factory=list, description="Ideas the model judged not groundable.")
    failed_calls: list[str] = Field(default_factory=list)


class ImportanceRating(BaseModel):
    """C4 importance, as returned by the model."""

    reason: str = Field(description="Two sentences: what an answer would change, and for whom.")
    importance: int = Field(ge=1, le=5, description="1 = trivial ... 5 = would change practice or understanding.")


class GapScore(BaseModel):
    gap_id: str
    idea_id: str
    design: str
    novelty: float = Field(description="1 - max cosine to any extracted manuscript claim (computed).")
    nearest_claim: str
    feasibility: float = Field(description="Share of required variables with documented levels or type (computed).")
    importance: int
    importance_reason: str
    score: float = Field(description="novelty x feasibility; importance only filters.")
    shortlisted: bool = False
    skipped_reason: str = ""


class Shortlist(BaseModel):
    scores: list[GapScore] = Field(default_factory=list)
    rule: str = ""
