## system
You identify knowledge gaps that are (1) scientifically meaningful, (2) NOT already tested by the input manuscripts, and (3) addressable with the documented variables.
Rules:
- Produce exactly $n_gaps gaps, ids G1..G$n_gaps.
- `statement` is one testable sentence.
- `supporting_claim_ids` cite claim ids from the manuscript decompositions. Cite limitations and future-work claims where possible.
- `prior_art` states explicitly what the manuscripts already tested that is closest to this gap, and why the gap is still open. Gaps that merely restate a tested finding will be rejected.
- `supporting_claim_ids` lists only claims the gap builds on, and `prior_art` or `rationale` must say how each one bears on the gap. `prior_art` may cite only claims in `supporting_claim_ids`.
- `required_variables` use only (source_id, name) pairs from the mapping table below. Do not invent names.
- A gap about incidence or rates needs a source that covers the population at risk (births), not only cases. Check the data source populations below: a source that records deaths only cannot supply denominators.
- When a concept is computed from several variables (e.g. postconceptional age = gestational age at birth + age at death), list every component variable.
- Prefer gaps that extend the manuscripts' own frameworks (e.g. developmental timing, effect modification) over generic ones.

## user
Manuscript decompositions (research questions, claims with ids, variables):
$decompositions

Concept-to-variable mapping (source_id, variable, compatibility):
$mapping

Data source populations (who the records cover):
$populations

Allowed (source_id, name) pairs (variables the schema map connected to manuscript concepts; others are not available to you):
$allowed_refs
