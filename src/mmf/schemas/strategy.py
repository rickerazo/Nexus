"""Component D output: one research strategy per gap."""

from __future__ import annotations

from pydantic import BaseModel, Field

from mmf.schemas.dataset import VariableRef
from mmf.validate.vocab import ModelClass, StudyDesign


class OutcomeSpec(BaseModel):
    variable: VariableRef
    definition: str = Field(description="How the outcome is defined from the variable (e.g. ICD codes, levels).")
    subtypes: list[str] = Field(
        description="Codes or levels of the outcome variable analysed separately (e.g. ['R95', 'W75', 'R99']); "
        "empty if the outcome is analysed as one event. With 2+ subtypes the outcome variable may appear in "
        "stratification and interactions, where it stands for the subtype."
    )


class Strategy(BaseModel):
    id: str = Field(description="S1, S2, ...")
    gap_id: str
    research_question: str
    outcome: OutcomeSpec
    exposures: list[VariableRef]
    # No defaults on these (LLM-facing): a grammar-constrained decoder may omit any field that is not required,
    # which is how Stage A lost every variable before 2026-11-06. Empty lists and nulls must be stated explicitly.
    covariates: list[VariableRef]
    interactions: list[list[VariableRef]] = Field(description="Each inner list is one interaction term (2+ variables).")
    stratification: list[VariableRef]
    offset: VariableRef | None = Field(description="Denominator variable for rate models; null if none.")
    denominator_source: str | None = Field(
        description="For rate models without an offset variable: the source whose records are the population at "
        "risk; the denominator is the count of its records per stratum. Null otherwise."
    )
    time_scale: VariableRef | None = Field(
        description="Time axis for time-to-event or time-stratified models (e.g. age at death); null if none."
    )
    design: StudyDesign
    model_class: ModelClass
    rationale: str
    expected_direction: str = Field(description="What result would support/refute the gap statement.")

    def all_refs(self) -> list[VariableRef]:
        refs = [self.outcome.variable, *self.exposures, *self.covariates, *self.stratification]
        for term in self.interactions:
            refs.extend(term)
        if self.offset:
            refs.append(self.offset)
        if self.time_scale:
            refs.append(self.time_scale)
        seen: set[str] = set()
        unique = []
        for r in refs:
            if r.key() not in seen:
                seen.add(r.key())
                unique.append(r)
        return unique


class StrategySet(BaseModel):
    strategies: list[Strategy] = Field(default_factory=list)
