"""Controlled vocabularies.

Strategies may only use designs and model classes listed here. Extending MMF to a new
domain means extending these enums (and their descriptions), not loosening the validators.
"""

from enum import StrEnum


class StudyDesign(StrEnum):
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    NESTED_CASE_CONTROL = "nested_case_control"
    CROSS_SECTIONAL = "cross_sectional"
    POPULATION_INCIDENCE = "population_incidence"
    CASE_CROSSOVER = "case_crossover"
    ECOLOGICAL = "ecological"


class ModelClass(StrEnum):
    LOGISTIC_REGRESSION = "logistic_regression"
    CONDITIONAL_LOGISTIC = "conditional_logistic"
    LOG_BINOMIAL = "log_binomial"
    POISSON_REGRESSION = "poisson_regression"
    NEGATIVE_BINOMIAL = "negative_binomial"
    COX_PROPORTIONAL_HAZARDS = "cox_proportional_hazards"
    TIME_STRATIFIED = "time_stratified"
    GENERALIZED_ADDITIVE = "generalized_additive"
    LINEAR_REGRESSION = "linear_regression"


DESIGN_DESCRIPTIONS: dict[StudyDesign, str] = {
    StudyDesign.COHORT: "Follow a defined population forward; outcome incidence by exposure.",
    StudyDesign.CASE_CONTROL: "Cases vs sampled controls; exposure odds compared.",
    StudyDesign.NESTED_CASE_CONTROL: "Case-control sampled from within an enumerated cohort.",
    StudyDesign.CROSS_SECTIONAL: "Exposure and outcome measured at one time.",
    StudyDesign.POPULATION_INCIDENCE: "Counts of events over a denominator population (rates).",
    StudyDesign.CASE_CROSSOVER: "Each case serves as its own control across time windows.",
    StudyDesign.ECOLOGICAL: "Group-level exposure and outcome.",
}

MODEL_DESCRIPTIONS: dict[ModelClass, str] = {
    ModelClass.LOGISTIC_REGRESSION: "Binary outcome; odds ratios.",
    ModelClass.CONDITIONAL_LOGISTIC: "Binary outcome with matched sets.",
    ModelClass.LOG_BINOMIAL: "Binary outcome; risk ratios directly.",
    ModelClass.POISSON_REGRESSION: "Counts/rates with offset; assumes mean = variance.",
    ModelClass.NEGATIVE_BINOMIAL: "Overdispersed counts/rates with offset.",
    ModelClass.COX_PROPORTIONAL_HAZARDS: "Time-to-event; hazard ratios.",
    ModelClass.TIME_STRATIFIED: "Any of the above fit separately within time strata (e.g. PCA windows).",
    ModelClass.GENERALIZED_ADDITIVE: "Smooth nonlinear terms (e.g. risk as a smooth function of age).",
    ModelClass.LINEAR_REGRESSION: "Continuous outcome.",
}


def vocab_text() -> str:
    """Render both vocabularies for inclusion in prompts."""
    lines = ["Allowed study designs:"]
    lines += [f"- {d.value}: {DESIGN_DESCRIPTIONS[d]}" for d in StudyDesign]
    lines.append("Allowed model classes:")
    lines += [f"- {m.value}: {MODEL_DESCRIPTIONS[m]}" for m in ModelClass]
    return "\n".join(lines)
