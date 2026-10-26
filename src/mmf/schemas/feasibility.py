"""Component E output: can this strategy be run with the documented data?"""

from __future__ import annotations

from pydantic import BaseModel, Field

from mmf.schemas.dataset import Variable, VariableRef

NOT_ASSESSED_DEFAULT = [
    "statistical power",
    "causal validity / confounding adequacy",
    "actual missingness rates (documentation only; no row-level data read)",
]


class VariableResolution(BaseModel):
    ref: VariableRef
    resolved: bool
    variable: Variable | None = None
    note: str = ""


class FeasibilityReport(BaseModel):
    strategy_id: str
    resolutions: list[VariableResolution]
    blockers: list[str] = Field(
        default_factory=list, description="Conditions that make the strategy infeasible as stated."
    )
    caveats: list[str] = Field(default_factory=list, description="Limitations that do not block but must be reported.")
    cross_source_notes: list[str] = Field(default_factory=list)
    not_assessed: list[str] = Field(default_factory=lambda: list(NOT_ASSESSED_DEFAULT))

    @property
    def feasible(self) -> bool:
        return not self.blockers and all(r.resolved for r in self.resolutions)


class FeasibilitySet(BaseModel):
    reports: list[FeasibilityReport] = Field(default_factory=list)
