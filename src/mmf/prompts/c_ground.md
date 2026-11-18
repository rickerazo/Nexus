## user
Task: turn the candidate research idea below into a study that these data can carry out, or conclude that they cannot. Think it through in prose; do not answer in JSON yet. Work through, in order:
1. The design. Restate the question so it fits the design given below. A design without a denominator source cannot estimate incidence, rates or risk: it compares proportions or odds among cases.
2. Sources by role. Which case series, population reference and denominator sources it uses, and why each plays that role.
3. Period. The years the question needs. The years listed for each source are the years held now; more years of every source can be acquired, so years not held are never a reason the question cannot be answered. Name the years that would have to be acquired.
4. Variables. For each concept, the candidate variables below that measure it, and how the measurement differs between sources (wording, timing, who reports it, coding of missing answers). A prevalence from a population reference needs its survey weight.
5. Biases: selection, information and confounding, specific to these sources.
6. What the design cannot establish.
7. Prior art: the closest thing the manuscripts' claims below already tested (cite claim ids), and why the question is still open; or that none of the claims is close.
8. Verdict: can these sources answer a version of the question? Only an epistemological, logical or logistical reason counts against it: a concept no source measures, a comparison the roles cannot support (for example a rate without a denominator source), measurements that cannot be made comparable, or data that cannot be obtained. The years held never count against it.

Candidate idea ($idea_id, design $design_name):
- Question: $question
- Comparison: $comparison
- Why open: $why_open
- Sources proposed: $sources
- Data: $data

Design:
$design

Manuscript claims (id [kind]: statement):
$claims

Candidate variables (source_id:NAME: label; values). Only these may be used:
$variables
