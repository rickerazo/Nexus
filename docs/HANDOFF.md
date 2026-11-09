# Handoff: project state and next steps

*Last updated 2026-11-09 (Monday). Update this file whenever the state below changes.*

This is the entry point for anyone picking up Nexus/MMF: where the project stands, what is running, what to do next, and the decisions that are easy to get wrong. For *why* the code is built the way it is, read [architecture.md](architecture.md); for the scientific framing, [specific_aims.md](specific_aims.md).

---

## 1. Where things stand

| Area | State |
|---|---|
| Pipeline (Components A–E, CLI, report) | Implemented and tested: 49 tests, lint, strict mypy, CI on every push. |
| Codebook ingestion | 7 SUID sources parsed deterministically, **6,035 variables** (parser v4, 2026-11-09; was about 5,500). An independent audit runs on every ingest (§2). |
| Component A (manuscript decomposition) | **Fixed 2026-11-06** (commit `1407505`). Before this, every run extracted claims only; see §5. |
| Smoke run (test fixtures, local model) | Passes end to end; recorded and replayed in CI. |
| SUID proof-of-concept run | Weekend run failed Fri 2026-11-06 at the first Stage B call. **Restarted Mon 2026-11-09 ~14:47 PT** at commit `f351764` without `--auto-approve`. It will stop at review B (§2, §3). Plan: [plans/2026-11-09-ingest-audit-and-b-crosscheck.md](plans/2026-11-09-ingest-audit-and-b-crosscheck.md). |
| Evaluation protocol | Draft, **not frozen**. No scored runs exist yet. |
| Repository | `github.com/rickerazo/Nexus` (private), history pushed 2026-11-06. |

Any output from a run before 2026-11-06 (`runs/suid_poc_20261026`, `runs/smoke_20261026T220417`, and the first Stage A in `runs/suid_poc_20261103`) was built from claims-only decompositions. Do not use those outputs for anything.

## 2. The weekend run

**What it is.** No model is being trained. MMF uses a pre-trained local language model (`qwen2.5:14b` via Ollama) as-is. The weekend job is one full pass of the pipeline over the SUID inputs: it reads the documents and produces a research-strategy report.

| | |
|---|---|
| Command | `scripts/run_pipeline.sh configs/suid.yaml runs/suid_poc_20261103 --auto-approve` |
| Started | Fri 2026-11-06, about 14:54 PT, at commit `1407505` |
| Inputs | 3 documents: PCA manuscript, bed-sharing manuscript, PubMed abstracts. 7 codebooks: CDC linked birth/infant death 2015, CDC natality 2015, CDC code names, NFR-CRS v5.1, PRAMS Phase 7 ARF, PRAMS Phase 8 ARF, PRAMS Phase 8 Standard Section II. See [configs/suid.yaml](../configs/suid.yaml). |
| Expected duration | 10–15 h of model time: A about 3 h, B 28–56 calls (5–9 h), C–E about 2 h. It should finish Saturday. |
| Machine requirements | Ollama running (`ollama serve`), Mac open and on AC power. `caffeinate` prevents idle sleep. |

**Stages:**
1. **A** decomposes each document into claims, variables, designs and model classes.
2. **B** maps every extracted concept onto codebook variables.
3. **C** proposes 3 knowledge gaps.
4. **D** writes one strategy per gap.
5. **E** checks feasibility.
6. The run writes `report.md`.

**Outcome (checked Monday 2026-11-09): the run failed.** Stage A completed and is cached for all 3 documents. The run stopped Fri 17:15 on `B_schema_map_0_0` after 4 rejected attempts (about 9 min each). There is no `B_schema.json` and no `report.md`. Causes:
- **Codebook parser bug.** The NVSS branch of `pass1_regex` (`src/mmf/ingest/codebook.py`, about line 167) skips a variable when a blank line separates its name from its label. 12 variables are missing from `cdc_linkco15`: SEX, CIG_0–CIG_3, BFED, BMI, PAY, WIC, ILIVE, ILP_R, MHTR. The model correctly mapped infant sex to `SEX`, and the validator rejected it.
- **Model inconsistency.** Alternate attempts returned `variable: null` with `compatibility: proxy`. The validator is correct and stays as is.
- **Unchecked renaming.** B renamed most concepts ("bed sharing" became "Bed sharing as exposure"), and nothing checks names against the concepts sent.
- **Ingest cache key** has no parser version, so a parser fix would not re-ingest on its own. The B–E keys lack prompt hashes.

Stage A quality on this run:
- 54 distinct concepts reach B (28 B calls); about 32 are mouse or neuron measures from the abstracts.
- 4 literature claims were dropped as ungrounded, including two SUID-relevant ones (maternal obesity PAF; maternal chlamydia/gonorrhea).
- Questionable roles in the bed-sharing paper: PCA labelled outcome, chronological age labelled offset.
- Near-duplicate concepts survive (sex / infant sex / sex (male, female); PCA ×3).

**Monday 2026-11-09 fixes and restart.**
- **Parser fixes (cdc_linkco15).** The blank-line bug recovered the 12 variables above. The new ingestion audit's anchor reconciliation then found 25 more (mixed-case `OEGest_*`, `PWgt_R`, `u*` items; inline labels such as `MBSTATE_REC`; split `F_MM_ PLAC`). Total 233 → 270.
- **Parser fixes (PRAMS ARFs).** The audit's identifier census showed both ARFs missing about half their variables: suffixed or wrapped Q# cells (`4d_L11a`, `18k_ARS`+`C`) and whole sections without a Q# column (birth certificate, analytic, forced-skip `SLEEPPOS`). P7 170 → 386, P8 177 → 485. The other codebooks are unchanged. `PARSER_VERSION` = 4 and is part of the ingest key.
- **B.** Concept names must match the names sent; case differences and "as <role>" are canonicalized and counted in warnings. The prompt now renders `"name" (role: …)`. B–E keys include prompt hashes. B also accepted an answer with **no mappings** (`SchemaMap.mappings` had a default, the same failure as A before `1407505`). B now decodes into an all-required schema and rejects empty answers.
- **Restarts.** B was restarted three times on Monday, each time within its first call, as each fix landed. Friday's logs are kept as `runs/suid_poc_20261103.fri-failed.log` and `.driver.fri-failed.log`.
- **Cross-check.** The B embedding cross-check (`B_check.json`) is built. B's cache key is untouched, so after B stops, `uv run mmf run configs/suid.yaml --run-dir runs/suid_poc_20261103` adds the check in minutes and rewrites `review_B.md` with a cross-check section. See [architecture.md](architecture.md#independent-pathways-checks-that-share-no-logic-with-what-they-check).

`manifest.json` still holds 9 calls from the pre-fix Nov 3 run (no `_profile`/`_claims` suffix); ignore those. Decisions and the full fix plan: [plans/2026-11-09-ingest-audit-and-b-crosscheck.md](plans/2026-11-09-ingest-audit-and-b-crosscheck.md).

**Already confirmed (Friday evening).** Stage A extracted:
- PCA manuscript: 12 variables, 14 claims; design `population_incidence`; model classes `negative_binomial`, `time_stratified`, `poisson_regression`, `generalized_additive`.
- Bed-sharing manuscript: 17 variables, 30 claims.

**`--auto-approve`** skips the two human review stops (B and C) so the run doesn't sit idle all weekend. **The resulting report is unreviewed.** §3 turns it into a reviewed one.

**Monitoring and recovery:**
```bash
tail -f runs/suid_poc_20261103.log              # live log
cat runs/suid_poc_20261103.driver.log           # ends with "DONE …" or the failure reason
```
- **The run died** (reboot, Ollama stopped): run `ollama serve`, then rerun the same command. Completed stages are cached, so it resumes where it stopped.
- **`Stopped: … no grounded variables extracted`**: the new Stage A gate fired. That document produced nothing usable. Inspect `runs/suid_poc_20261103/A_<doc>.json` and the matching `llm_log/` transcripts.

## 3. Monday checklist

Phases 1 and 2 of [the 2026-11-09 plan](plans/2026-11-09-ingest-audit-and-b-crosscheck.md) are done. When the driver log says `Stopped at review B`:
- Rerun once without approving: `uv run mmf run configs/suid.yaml --run-dir runs/suid_poc_20261103`. It adds `B_check.json` and the cross-check section to `review_B.md`.
- Then follow the checklist below, starting at step 2 and reviewing the cross-check flags first in step 3.
- Do not edit `B_schema.json` or `C_gaps.json` until the investigator has approved a proposed edit list.

1. Confirm the run finished: `driver.log` ends with `DONE`, and `report.md` exists.
2. In `manifest.json`, scan for calls with `"ok": false`, the `dropped` lists (claims or variables removed because their quotes weren't verbatim), and `warnings`.
3. **Review B.** Open `B_schema.json` and fix wrong or stretched mappings by hand. Watch for vague concept names (the smoke run produced a concept called just "outcome"). Literature-only concepts that will never map, such as mouse or neuron measures, can simply be deleted.
4. Rerun the same command. Editing B invalidates C, D and E, so they recompute (about 2 h).
5. **Review C.** Read `C_gaps.json` and `review_C.md`, edit as needed, and rerun. D and E recompute.
6. Read `report.md`. It is now reviewed. Update §1 and §2 of this file with the outcome.

## 4. Where to go next (priority order)

**A. Make the first SUID result trustworthy** (this week)
1. Complete the §3 review cycle.
2. **Record the code version in each run.** `RunManifest` stores prompt, model and input hashes but not the git commit. Add the commit hash and a dirty-tree flag. Small change, and it closes a real provenance gap.
3. **Fix the PRAMS Phase 8 Standard Section II parser.** It yields only 4 variables; its layout needs a dedicated deterministic pass in `src/mmf/ingest/codebook.py`. The identifier census does not detect this layout, so check it by hand.
4. **Make D's LLM-facing schema all-required before D runs.** `Strategy` lets the model omit `covariates`, `offset`, `interactions`, `stratification`, `time_scale` and `expected_direction` (the defaults bug class). Make them required and nullable, as A and B now are, and add the model to `test_component_a_chunk_schemas_require_every_field`. C is protected by its exact-count validator.
5. **Near-duplicate concepts** from A (case-insensitive exact dedup only). Consider normalized dedup or merge them during B review.
5a. **Read the identifier census files with the investigator** (`runs/suid_poc_20261103/sources/*.audit.json`) before tightening the parser further. Known leftovers:
    - Mostly SAS format names.
    - One split name (`VT_NONHISPANIC_WHIT` + `E`).
    - Label and level warts: `MHTR` "…Inches 282", `RF_PHYPE` "…321", `BMI` level `282=…`, `DWgt_R` level `303=…`, `SLEEPPOS_RAW` "…SLEEPPO S".
    - B shows labels only; levels feed the embedding check.
5b. **Recalibrate `b_check_miss_threshold`** (provisional 0.65) on the reviewed B output.

**B. Make runs cheaper** (before any repeated runs)

6. **Stage B output is mostly "no match" rows.** Let the model return only real mappings and generate the "none" rows in code. This should cut B from hours to a fraction, and it matters because the evaluation needs k=5 repeats per condition.
7. Stage A quotes are still fragile. The model truncates them or appends page markers, and items that never ground are dropped. Track the dropped count per run; if it grows, consider asking for sentence-level quotes only.

**C. Build what the evaluation protocol assumes but doesn't yet exist** ([evaluation_protocol.md](evaluation_protocol.md))

8. A **validators-off switch** for the ablation condition (L−). There is currently no way to run it. It must also set `b_crosscheck: false` and decide whether the ingestion audit's hard check stays on.
9. A **blinded rater-sheet export**: strategies to `blind_code` rows matching `evaluation/rater_sheet_template.csv`, with the key in the gitignored `evaluation/blinding_key.csv`.
10. **Single-manuscript configs** for metric 3 (retrospective recovery: run with the PCA manuscript only, then with bed-sharing only).
11. Decide on **condition O** (cloud). It needs institutional credentials; if there are none, drop it and say so in the protocol.
12. Recruit the **second blinded rater**.
13. **Freeze the protocol.** Record the commit hash in it and log any later deviations. Only runs after this point count.

**D. Then:** scored runs (Aim 3 validation), select one strategy, and implement it with standard epidemiologic methods. That last step is outside MMF.

## 5. Recent changes worth knowing

- **Component A fix (2026-11-06).**
  - **Cause:** the LLM-facing schema's list fields had defaults, so Ollama's grammar-constrained decoder let the model skip them. Every decomposition held claims only. Component B then received an empty concept list and mapped codebook labels onto themselves, and its validators passed.
  - **Fix:** two calls per chunk (study profile, then claims) with every field required. A manuscript with no variables or claims now stops the run (`StageInputError`), and B refuses an empty concept list.
  - **Rule:** never add defaults to LLM-facing models. A test enforces it.
- **Stage B batching.** Concepts are sent in batches capped by `b_max_mappings_per_call` (default 50), so a long concept list can't hit the output-token cap.
- **Stage A cache key** now includes the prompt hashes, so editing a prompt reruns A. Since 2026-11-09, B–E keys do too, and the ingest key includes `PARSER_VERSION`.
- **Independent pathways (2026-11-09).** An ingestion audit and a B embedding cross-check; see [architecture.md](architecture.md). Embeddings use local `mxbai-embed-large` (`ollama pull mxbai-embed-large`).

## 6. Operating rules and decisions

- **Local model only by default.** Ollama is not auto-started on the development Mac: run `ollama serve` first. Throughput is about 9 tokens/s, so long runs need the Mac open and on power. Use `scripts/run_pipeline.sh`, which wraps the run in `caffeinate`.
- **No personal LLM credentials.** This is an institute-funded project. The cloud backend runs only with `allow_cloud: true` in the run config and an institutional key in `MMF_API_KEY`. Never send restricted documents to a cloud backend.
- **Documentation in, never data.** MMF reads codebooks, guides and manuscripts, never row-level CDC, PRAMS or NCFRP data. `data/` and `runs/` are gitignored; inputs are traced by sha256 in `data/manifest.json`.
- **Codebooks are parsed by code, not the model** (`llm_extract: false`). At local speed, model enrichment would take hours per codebook.
- **Validators, not prompts, provide the guarantees.** If output is wrong, tighten a validator; don't relax one to make a run pass.
- **GitHub access from the work Mac** is through a repo-only, passphrase-protected deploy key configured in this repo's local git config. No account-wide credentials live on this machine. Commits use the GitHub no-reply address.

## 7. Map of the repository

| Path | What it is |
|---|---|
| [README.md](../README.md) | Overview, principles, quickstart |
| [docs/architecture.md](architecture.md) | Component contract, schemas, data flow, failure modes |
| [docs/evaluation_protocol.md](evaluation_protocol.md) | Validation protocol (draft) |
| [docs/specific_aims.md](specific_aims.md), [docs/outline.md](outline.md) | Proposal |
| `src/mmf/` | Package: `components/` (A–E), `ingest/`, `llm/`, `prompts/`, `schemas/`, `validate/`, `pipeline.py`, `cli.py` |
| `configs/` | `suid.yaml` (proof of concept), `smoke.yaml` (fixtures) |
| `scripts/` | `run_pipeline.sh` (long runs), `smoke.sh`, `fetch_pubmed.py` (literature input) |
| `evaluation/` | Rubric, rater sheet template, `analyze_eval.py` |
| `tests/` | Unit tests and a replay integration test (recorded model responses, no model needed) |
| `legacy/` | Read-only exploratory scripts that preceded the package |
