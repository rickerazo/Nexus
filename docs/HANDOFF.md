# Handoff: project state and next steps

*Last updated 2026-11-06 (Friday). Update this file whenever the state below changes.*

This is the entry point for anyone picking up Nexus/MMF: where the project stands, what is running, what to do next, and the decisions that are easy to get wrong. For *why* the code is built the way it is, read [architecture.md](architecture.md); for the scientific framing, [specific_aims.md](specific_aims.md).

---

## 1. Where things stand

| Area | State |
|---|---|
| Pipeline (Components A–E, CLI, report) | Implemented and tested: 36 tests, lint, strict mypy, CI on every push. |
| Codebook ingestion | 7 SUID sources parsed deterministically, about 5,500 variables. |
| Component A (manuscript decomposition) | **Fixed 2026-11-06** (commit `1407505`). Before this, every run extracted claims only; see §5. |
| Smoke run (test fixtures, local model) | Passes end to end; recorded and replayed in CI. |
| SUID proof-of-concept run | **Running over the weekend of 2026-11-06** (§2). First run with the Component A fix. |
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
3. **Fix the PRAMS Phase 8 Standard Section II parser.** It yields only 4 variables; its layout needs a dedicated deterministic pass in `src/mmf/ingest/codebook.py`.

**B. Make runs cheaper** (before any repeated runs)

4. **Stage B output is mostly "no match" rows.** Let the model return only real mappings and generate the "none" rows in code. This should cut B from hours to a fraction, and it matters because the evaluation needs k=5 repeats per condition.
5. Stage A quotes are still fragile. The model truncates them or appends page markers, and items that never ground are dropped. Track the dropped count per run; if it grows, consider asking for sentence-level quotes only.

**C. Build what the evaluation protocol assumes but doesn't yet exist** ([evaluation_protocol.md](evaluation_protocol.md))

6. A **validators-off switch** for the ablation condition (L−). There is currently no way to run it.
7. A **blinded rater-sheet export**: strategies to `blind_code` rows matching `evaluation/rater_sheet_template.csv`, with the key in the gitignored `evaluation/blinding_key.csv`.
8. **Single-manuscript configs** for metric 3 (retrospective recovery: run with the PCA manuscript only, then with bed-sharing only).
9. Decide on **condition O** (cloud). It needs institutional credentials; if there are none, drop it and say so in the protocol.
10. Recruit the **second blinded rater**.
11. **Freeze the protocol.** Record the commit hash in it and log any later deviations. Only runs after this point count.

**D. Then:** scored runs (Aim 3 validation), select one strategy, and implement it with standard epidemiologic methods. That last step is outside MMF.

## 5. Recent changes worth knowing

- **Component A fix (2026-11-06).**
  - **Cause:** the LLM-facing schema's list fields had defaults, so Ollama's grammar-constrained decoder let the model skip them. Every decomposition held claims only. Component B then received an empty concept list and mapped codebook labels onto themselves, and its validators passed.
  - **Fix:** two calls per chunk (study profile, then claims) with every field required. A manuscript with no variables or claims now stops the run (`StageInputError`), and B refuses an empty concept list.
  - **Rule:** never add defaults to LLM-facing models. A test enforces it.
- **Stage B batching.** Concepts are sent in batches capped by `b_max_mappings_per_call` (default 50), so a long concept list can't hit the output-token cap.
- **Stage A cache key** now includes the prompt hashes, so editing a prompt reruns A.

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
