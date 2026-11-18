## user
Task: propose exactly $n_ideas distinct research questions that use the design given at the end of this message. They form a pool that is checked and narrowed down later, so aim for range and originality; feasibility, novelty and importance are scored afterwards.
Rules:
- Ask questions a specialist would not think of first. Do not propose a question the manuscripts already answered, or one that only adds another risk factor or effect modifier to the models they fit.
- Respect the source roles: outcomes come only from case series, exposure prevalence only from population reference sources (using their survey weight), and the population at risk only from denominator sources. List each source you use under the role it plays in this question; leave a role empty if the question does not use it.
- `comparison`: who is compared with whom, in which period. Name the years the comparison needs. Years a source does not hold yet can be acquired, so never avoid a question because of them.
- Think outside the field's usual questions. At least $min_new ideas must be built mainly on inventory domains marked NEW (no manuscript uses them). The domain matches below show where a case series and a population reference record similar things, including comparisons no manuscript has made.
- `domains`: the ids (D1, D2, ...) of the inventory domains the question uses, only from sources you list under a role. Source fields take only the source ids shown, not domain names.
- `question`: one sentence. `why_open`: one or two sentences on why it is unanswered and what an answer would change. `data`: how those domains would be used.
- Do not invent variable names, and do not propose a question that needs data no source documents.

What the manuscripts studied:
$manuscripts

Concepts the schema map found in more than one source, by role:
$cross_role

Domain matches between case series and population reference (embedding similarity; both sides NEW first):
$matches

Data inventory (id source_id / domain name [NEW if no manuscript uses it, size, use by the manuscripts]: summary):
$inventory

Design for this request:
$design
