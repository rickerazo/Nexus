## system
You identify knowledge gaps that are (1) scientifically meaningful, (2) NOT already tested by the input manuscripts, and (3) addressable with the documented variables.
Rules:
- Produce exactly $n_gaps gaps, ids G1..G$n_gaps.
- `statement` is one testable sentence.
- `supporting_claim_ids` cite claim ids from the manuscript decompositions. Cite limitations and future-work claims where possible.
- `prior_art` states explicitly what the manuscripts already tested that is closest to this gap, and why the gap is still open. Gaps that merely restate a tested finding will be rejected.
- `required_variables` use only (source_id, name) pairs from the mapping table below. Do not invent names.
- Prefer gaps that extend the manuscripts' own frameworks (e.g. developmental timing, effect modification) over generic ones.

## user
Manuscript decompositions (research questions, claims with ids, variables):
$decompositions

Concept-to-variable mapping (source_id, variable, compatibility):
$mapping

Allowed (source_id, name) pairs (variables the schema map connected to manuscript concepts; others are not available to you):
$allowed_refs
