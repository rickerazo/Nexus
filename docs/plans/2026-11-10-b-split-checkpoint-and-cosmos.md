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

- **C's validator does not check that supporting claims relate to the gap**, nor that prior_art cites only
  listed claims.
- **C's prompt does not say NCFRP holds deaths only** (no denominators), so the model reached for NCFRP variables in
  incidence questions.
- **D–E cache keys do not include the output schema.** A run dir holding a D result from an older schema fails to
  load rather than recomputing.
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
