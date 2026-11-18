## user
Now give your answer as JSON, following your reasoning above.
- `groundable`: false only if these sources cannot answer any version of the question for an epistemological, logical or logistical reason; then give that reason in `why_not` and fill the other fields as best you can. The years held are never such a reason. If true, `why_not` is "".
- `statement`: one testable sentence that fits the design. Use proportions or odds among cases unless a denominator source is used.
- `prior_art`: the closest tested work, citing claim ids, and why the question is still open; or "none in the inputs" with a reason. At least 15 words.
- `supporting_claim_ids`: claim ids the gap builds on (may be empty). Every claim id cited in `prior_art` must be listed here.
- Sources by role: as in your reasoning; the design needs $needs.
- `period_start`, `period_end`: the years the question needs, even beyond the years held (those will be acquired); not in the future.
- `variables`: every variable used, as `source_id:NAME` from the candidate list, including the survey weight of each population reference used. Each source listed under a role must contribute at least one variable.
- `cannot_establish`: what the design cannot establish.
