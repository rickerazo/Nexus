# Plan: B multi-variable split + per-call checkpoints, and Epic Cosmos addendum (2026-11-10)

Approved by the user on Tue 2026-11-10. Times are PST.

## Context
- Monday's restart of `runs/suid_poc_20261103` (at commit `f351764`) failed Mon 2026-11-09 at 16:03 PST.
  The failing call was `B_schema_map_3_0` (ncfrp_v51), the 9th of about 28 B calls.
- All four attempts listed several real variables in one `variable` field (`'INF3chlamydia, INF3gonorrhea'`,
  `'CIG0_R, CIG1_R, CIG2_R, CIG3_R'`). Every one of those names is documented. The validator still called the
  whole string undocumented, so the model was never told what to fix.
- B saved nothing until all its calls finished, so the 8 calls that had passed were lost.
- The user also asked to add Epic Cosmos as a data source. Its Data Dictionary is only available after logging
  into cosmos.epic.com. The user chose **Both**: a cited public stub now, and the real dictionary once they
  export it.

## Steps and status
| # | Step | Status |
|---|---|---|
| 1 | Validator: a multi-name `variable` passes if every part is documented. Otherwise it names only the bad parts and says "one variable name per mapping". | Done, `9d78c98` |
| 2 | `expand_multi`: split such rows into one row per variable (copying compatibility and rationale) and add a warning. | Done, `9d78c98` |
| 3 | Prompt: "`variable` holds exactly one name; write a separate mapping for each". | Done, `9d78c98` |
| 4 | Per-call checkpoints in `run_dir/checkpoints/B/<stage>_<key16>.json`, keyed by model, seed, temperature, num_ctx, prompt hash, rendered input and output schema. A hit is re-validated. A warning reports "resumed N of M". | Done, `9d78c98` |
| 5 | Tests: split, partly-undocumented rejection, a checkpoint surviving a failure, resume equal to a fresh run. Results: 52 pass, ruff and mypy clean. | Done |
| 6 | Offline replay of the failed call: attempt 1 now passes (4 rows split); attempt 4 is still rejected on 2 truly undocumented names. | Done |
| 7 | Preserve the failed logs (`runs/suid_poc_20261103.mon-failed.log`, `.driver.mon-failed.log`). Restart without `--auto-approve`. | Done, Tue 2026-11-10 14:09 PST |
| 8 | Cosmos public stub: [../data_sources/epic_cosmos.md](../data_sources/epic_cosmos.md). It is kept out of `codebooks:`. | Done, `483e06e` |
| 9 | Wait for `Stopped at review B` in `runs/suid_poc_20261103.driver.log` (about 4–5 h). If it fails, rerun the same command and B resumes from the checkpoints. | Done: stopped at review B Tue 2026-11-10 17:51 PST; all 28 calls passed and are checkpointed |
| 10 | Rerun once without approving: `uv run mmf run configs/suid.yaml --run-dir runs/suid_poc_20261103`. B is a cache hit; this adds `B_check.json` and the cross-check section in `review_B.md`. | Not needed: the same pass wrote both (agree 42, both_none 266, llm_outside_topk 24, possible_miss 46) |
| 11 | Propose a B edit list: cross-check flags first, then wrong or stretched mappings (e.g. SUID → infection variables), near-duplicates, and deleting the mouse/neuron concepts. **No edits to `B_schema.json` until the user approves.** | Done. Edits E1–E15 approved Wed 2026-11-11 and applied (see below) |
| 11a | Validator: a (concept, source) pair with no row, or a repeated (concept, source, variable) row, fails validation (was a warning). Approved 2026-11-11. | Done, 54 tests pass |
| 12 | Approve, then run to C. Review C the same way, with no edits to `C_gaps.json` without approval. Before D runs, propose making D's `Strategy` LLM-facing fields required and nullable, and get the user's go-ahead. Then D, E, the report and HANDOFF. | B approved Wed 2026-11-11; C stopped at review 14:57 PST (one attempt). C edits and the `Strategy` change approved 2026-11-11 (see below). D, E, report: pending |
| 13 | Cosmos, real dictionary: the user exports it (CSV or Excel) into `data/documentation/`. Check whether `pass1_table` handles `Table.Column` names; if not, add a Cosmos branch, bump `PARSER_VERSION` and add tests. Add `epic_cosmos` to `configs/suid.yaml`. This re-runs B in full. | Waiting on the user |

## B review, applied Wed 2026-11-11 (PST)
- The original model output is kept as `runs/suid_poc_20261103/B_schema.pre-review.json`. The edits were applied by a script
  that rebuilds from that backup; the result passes `map_validator` with no duplicate rows and no missing pairs.
- 696 → 159 rows (70 direct, 27 derived, 15 proxy, 47 none); 54 → 22 concepts.
- E1 dropped the 32 mouse/neuron/cell concepts. E2 fixed rows the model filed under `sex (male, female)` and
  `birthweight (low, non-low)` instead of `sex` and `birthweight`. E3–E15 corrected mappings per concept: wrong
  NCFRP rows for SUID and sex removed; `UCOD`, `REGsuidcat`, `CAUicdcode`, `AGED`, `INFdayslive`, BMI, infection,
  bed-sharing and PRAMS gestation/birthweight variables added; compatibility made consistent.
- E5: natality `COMBGEST` kept for PCA as the person-time denominator (natality has no death age).
- Decision 2: `cdc_codenames` is no longer a mapping source. Its rows and summary are deleted from this run's B.

## C review, applied Wed 2026-11-11 (PST)
- Original kept as `runs/suid_poc_20261103/C_gaps.pre-review.json`; the edited file passes `gap_validator`, and every
  variable and concept it names is in the reviewed B.
- Problems in C's output: prior_art cited claims that were not in `supporting_claim_ids`, and the listed ones were
  unrelated; every gap used NCFRP variables only (deaths only, so no incidence denominators); PCA listed without
  age at death; G3 partly done already (the PCA manuscript stratified by breastfeeding at discharge).
- G1 (maternal BMI by PCA window) and G2 (smoking × preterm birth across PCA windows) kept and revised to cite the
  right claims and use `cdc_linkco15` variables. G3 replaced: SUID incidence by PCA for each cause-of-death subtype
  (R95, W75, R99), supported by `SUID_manuscript_v9_clean.C6` and `.C12`.

## D `Strategy` schema, approved Wed 2026-11-11
- `covariates`, `interactions`, `stratification`, `offset`, `time_scale` and `expected_direction` lose their defaults
  (lists must be given, possibly empty; `offset`/`time_scale` may be null). D's validator rejects an empty
  `expected_direction`. `Strategy` and `OutcomeSpec` join the every-field-required test.
- Evidence the defect was live: the recorded smoke run's D answers omitted `covariates`, `interactions`, `offset`
  and `stratification` in both strategies. The smoke cassette is re-recorded with the new schema.

## C fixes, Wed 2026-11-11 (`02f48fc`), at the user's request before D
- C rejects supporting claims not discussed in prior_art/rationale, and prior_art citing unlisted claims. The
  model's original SUID gaps fail 7 such checks; the reviewed gaps pass.
- Codebook entries carry a `population`; C's prompt shows them and says incidence needs a births denominator and
  that a derived concept (PCA) lists every component. C's cache key includes the populations.
- A regenerated B or C clears its review approval (found while making this change: the old gate would have passed
  regenerated, unreviewed gaps to D).
- D was stopped at 15:21 PST before writing anything. C is rerun with the fixed prompt and stops for a new review.
  The reviewed gaps are kept as `C_gaps.reviewed-2026-11-11.json` (approval: `review_C.approved-2026-11-11.md`).
- The rerun's gaps restated tested findings (sex-similar associations, `bedsharing_ms_v7.C6`, `.C15`) and were
  rejected; the reviewed gaps were restored and C approved (rerun kept as `C_gaps.rerun-rejected.json`).

## D fixes, Wed 2026-11-11 (approved by the user)
- **Births denominator (`1ca347e`).** The linked file has no births variable; its denominator is a count of birth
  records. Codebook entries take `denominator: true` (`cdc_linkco15`, `cdc_natl15`); `Strategy.denominator_source`
  (required, nullable) satisfies a rate model instead of an offset variable. Before this, D invented
  `POPULATION_DENOMINATOR`. D's cache key now includes the denominator sources and the `Strategy` schema.
- **Outcome subtypes.** D's first run (15:49–15:55 PST) passed G1 and G2 (`denominator_source: cdc_linkco15`) and
  failed G3 four times: the model stratified by `UCOD` to separate R95/W75/R99, and the rule "the outcome never
  appears elsewhere" rejected it. `OutcomeSpec.subtypes` (required list) declares the codes analysed separately;
  with 2+ subtypes the outcome variable may appear in stratification and interactions, never as an exposure or
  covariate. The validator was not relaxed for outcomes without subtypes. Declared subtypes must be used (the outcome
  variable must appear in stratification or an interaction): the first smoke recording listed the codes that define
  SUID as subtypes in strategies that do not compare them, which the report would have misstated.
- D does not checkpoint per call, so a failed D reruns every gap (about 3 min each).
- **Run completed 16:30 PST** (report written). E rated S1 and S2 blocked, S3 feasible; the blockers are parsing
  artefacts (`UCOD`/`AGED` bare labels and no levels; `BMI_R` one level). No strategy computed PCA.
- **Derived variables (approved 2026-11-11).** `Strategy.derived` (required list): name, formula, inputs, description;
  referenced as `derived:<NAME>`. D checks: inputs documented and from one source, formula uses exactly its inputs
  (plus a few functions), every declared derived variable used and every use declared, the outcome never derived,
  and a derived variable built from the outcome never an exposure or covariate. `all_refs()` expands derived
  references into their inputs, so E resolves them through the codebook. D and E rerun (D's key includes the schema).
- **Retry feedback is cumulative.** The first smoke recording with derived variables failed D: shown only the latest
  problem, the model alternated between unused outcome subtypes and an unused derived variable across all four
  attempts (attempt 1 had used PCA correctly). Each retry now also lists earlier attempts' problems. Applies to every
  stage; no check was relaxed.
- **Unused outcome subtypes are cleared, not rejected.** Two more smoke recordings failed D: the clearer "declared but
  not used" message fixed derived-variable use, but in 3 of 4 attempts the model listed the codes that define the
  outcome (R95/W75/R99) as subtypes. Subtypes with no stratification or interaction by the outcome have no effect, so
  they are now cleared deterministically and recorded in the call's `normalized` list (shown in the report), the same
  pattern as B's name canonicalization. Using the outcome in stratification or interactions without declared subtypes
  is still rejected. The prompt no longer gives copyable example codes.

## Deferred (to solve later)
- **Remove `cdc_codenames` from `configs/suid.yaml`** at the next full B rerun (parser fix or Cosmos). Changing the
  config now would change B's cache key and overwrite the reviewed `B_schema.json` with raw model output.
- **Linked file death date not extracted:** `DOD_YY`, `DOD_MM` (and `D_RESTATUS`, `DWEEKDAY`, `HOSPD`, `DOSTATE`,
  `DOCNTY`, `DRCNTY`, …) are in the `cdc_linkco15` identifier census but are not variables. "Year of birth or death" has
  birth year only. A parser fix bumps `PARSER_VERSION` and reruns B in full.
- **`b_check_miss_threshold` (0.65):** about half of the 46 `possible_miss` flags were real misses, often pointing
  at the wrong variable (`P_PRTERM`, `PREV_LBW`: *previous* births; mouse concepts matching `INF72breathe`). Use the
  reviewed B as the reference set for recalibration (HANDOFF §4 item 5b).
- **An edited `B_schema.json` is only schema-validated on reload** (`pipeline.py`, `stage_b`), not run through
  `map_validator`. A hand edit with a typo'd variable would pass. Consider validating it against the sources.
- **The stricter validator invalidates 9 of the 28 B checkpoints** (calls that left pairs without rows). They are
  regenerated only on the next B cache miss; this run's B is a cache hit and is unaffected.

- **E's cache key does not include the output schema** (D's does since `1ca347e`).
- **D does not checkpoint each call** the way B does.
- **D's PCA handling:** G3's attempts used age at death as the exposure with gestational age as a covariate,
  instead of PCA computed from both. Check the final strategies.
- **D's `outcome_refs` includes concepts A mislabelled as outcomes** (PCA in the bed-sharing paper), so `COMBGEST`
  and `AGED` count as valid outcomes.
- **`scripts/run_pipeline.sh` labels a stop by its loop counter** ("Stopped at review B" when it stopped at C).

## Rules
- Never push; the user pushes with the deploy key's passphrase.
- Local Ollama only. Start `ollama serve` if it is down.
- State all times in PST.

## Verification
- `uv run pytest`, `uv run ruff check src tests scripts`, `uv run mypy src`.
- `ls runs/suid_poc_20261103/checkpoints/B | wc -l` grows toward about 28.
- `tail -3 runs/suid_poc_20261103.driver.log` shows `Stopped at review B`.
