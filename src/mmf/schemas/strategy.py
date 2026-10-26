"""Component D output: one research strategy per gap."""

from __future__ import annotations

from pydantic import BaseModel, Field

from mmf.schemas.dataset import VariableRef
from mmf.validate.vocab import ModelClass, StudyDesign


class OutcomeSpec(BaseModel):
    variable: VariableRef
    definition: str = Field(description="How the outcome is defined from the variable (e.g. ICD codes, levels).")


class Strategy(BaseModel):
    id: str = Field(description="S1, S2, ...")
    gap_id: str
    research_question: str
    outcome: OutcomeSpec
    exposures: list[VariableRef]
    covariates: list[VariableRef] = Field(default_factory=list)
    interactions: list[list[VariableRef]] = Field(
        default_factory=list, description="Each inner list is one interaction term (2+ variables)."
    )
    stratification: list[VariableRef] = Field(default_factory=list)
    offset: VariableRef | None = Field(default=None, description="Denominator variable for rate models.")
    time_scale: VariableRef | None = Field(
        default=None, description="Time axis for time-to-event or time-stratified models (e.g. age at death)."
    )
    design: StudyDesign
    model_class: ModelClass
    rationale: str
    expected_direction: str = Field(default="", description="What result would support/refute the gap statement.")

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
