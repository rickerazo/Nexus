# Plan: fix the SUID run's Stage B failure, and add independent cross-checks to ingestion and Stage B

*Written 2026-11-09. To be copied into the repo as `docs/plans/2026-11-09-ingest-audit-and-b-crosscheck.md` (step 0).*

## Context

The weekend run `runs/suid_poc_20261103` (started Fri 2026-11-06 14:54, commit `1407505`, `--auto-approve`) **did not finish**. Stage A completed and is cached for all 3 documents. The run stopped Fri 17:15 on the first of 28 Stage B calls (`B_schema_map_0_0`, 4 rejected attempts of about 9 min each). There is no `report.md` and no `B_schema.json`.

Diagnosis:

1. **Ingest bug (root cause).** At `src/mmf/ingest/codebook.py:167`, the NVSS-layout branch requires `lines[i + 1]` to be non-empty and uses it as the label. In `LinkCO15Guide.pdf`, some names are followed by a blank line before the label, so those variables are silently skipped. **12 linked-file variables are missing:** SEX, CIG_0–CIG_3, BFED, BMI, PAY, WIC, ILIVE, ILP_R, MHTR. The model correctly mapped infant sex to `SEX`; the validator rejected it because the parsed codebook lacked `SEX`. cdc_natl15 is unaffected.
2. **Model inconsistency.** The model returned `variable: null` with `compatibility: proxy`. The validator is correct; we leave it alone and rely on retries.
3. **Unchecked concept renaming.** B returned "Bed sharing as exposure", "Sex as stratifier", "Adult neurogenesis" (sent as "adult neurogenesis") and so on. About 36 of 50 names per attempt did not match the concepts sent, and nothing checks for this.
4. **Provenance gaps.** The ingest cache key (`pipeline.py:143`) has no parser version, so a parser fix would not re-ingest. The B–E cache keys do not include prompt hashes (A's key does, at `pipeline.py:170`).
5. **Stage A quality** (for the record). There were 54 distinct concepts going into B, of which about 32 are mouse or neuron measures from the literature abstracts. Two SUID-relevant literature claims were dropped as ungrounded (maternal obesity PAF 5.4%; maternal chlamydia/gonorrhea). Questionable roles in the bed-sharing paper: "PCA" labelled outcome, "chronological age" labelled offset. Near-duplicate concepts remain (sex / infant sex / sex (male, female); 3× PCA; SUID ×2; birthweight ×2).

User decisions (2026-11-09):

- Fix the parser **and** add a second, independent pathway that checks it.
- Add an embedding-based "fingerprint" pathway to Stage B as an independent check on the LLM's mappings.
- Concept-name check approved: canonicalize case differences and a trailing "as <role>"; reject everything else.
- Mouse/neuron concepts: option (a). Keep them through B and delete them during B review. Cost reduction comes later (HANDOFF §4 item 6).
- Leave the null-variable/`proxy` validator as is.
- **Sequencing: restart early.** Phase 1 contains the minimal fixes and restarts the run. Phase 2 builds the cross-checks while B runs and applies them to B's output before review.
- Embedding model: **`mxbai-embed-large`** via local Ollama (not yet pulled).

## Step 0: Permanent record (do first, docs only)

- Copy this plan to `docs/plans/2026-11-09-ingest-audit-and-b-crosscheck.md`.
- `docs/HANDOFF.md`:
  - §1: SUID row becomes "Weekend run **failed** Fri 17:15 at first B call; see plan".
  - §2: add an "Outcome" paragraph with the diagnosis above.
  - §3: add "do the plan's Phase 1 first".
  - §4: add Phase 2 items, the B–E prompt-hash provenance gap, and the near-duplicate concept issue.
  - Bump the "Last updated" date.
- Update memory `nexus-mmf-project-state.md` with a pointer to the plan file.
- Commit (docs only). The user pushes; the deploy key needs their passphrase.

## Phase 1: Minimal fixes, then restart (before any B time is spent)

1. **Parser fix** in `codebook.py`, NVSS branch (~line 167). Use the next non-empty line within 3 lines as the label, rejecting it if it matches `_POSITION`/`_LEN`. Start the levels scan after the label's index. Leave the `MHTR` label wart ("…Inches 282") as is and note it.
2. **Parser version in the ingest cache key.** Add `PARSER_VERSION = "2"` in `codebook.py` and include it in `_h(...)` at `pipeline.py:143`. All 7 codebooks re-ingest deterministically in seconds (`llm_extract: false`). No manual deletion is needed.
3. **Prompt hashes in the B–E cache keys** (`pipeline.py` `stage_b`…`stage_e`), using the same pattern as `a_decompose.prompt_hashes()`. Nothing downstream is cached yet, so this costs nothing now and keeps later prompt edits from reusing stale B output.
4. **Concept-name check in B** (`src/mmf/components/b_schema_map.py`):
   - Build `map_validator` per batch, taking the batch's `(concept, role)` list.
   - `canonical_concept(returned, batch)` returns the exact match; else a case-insensitive match; else the name with a trailing `\s+as\s+(an?\s+)?<sent role>$` stripped and matched case-insensitively. Otherwise it returns `None`, which raises the problem "concept {x!r} was not in the list; copy the concept name exactly as given".
   - After `generate` accepts, rewrite names to canonical form. Record each rewrite count as a warning, e.g. `B_schema_map_0_0: 31 concept names canonicalized`. That keeps "nothing silently repaired" (`structured.py:60-65`) true in spirit.
   - Coverage: report (concept, source) pairs with no row as **warnings, not rejections**, to avoid retry blow-up.
   - `map_schema` returns warnings, and `stage_b` appends them to `manifest.warnings`.
   - `collect_concepts` must keep the role for the check; it already carries `role; operationalization`. Expose role separately.
5. **Prompt render** (`src/mmf/prompts/b_schema_map.md` plus the render in `map_schema`): concepts as `- "bed sharing" (role: exposure) — <operationalization>`, plus the rule "copy each concept name exactly; do not append the role". This reduces retries; the validator is still the guarantee.
6. **Tests** (`tests/unit/test_ingest.py`, `tests/unit/test_components.py`):
   - Add an NVSS block to `tests/fixtures/mini_nvss_guide.txt` with a blank line between `SEX` and "Sex of Infant" (levels M/Male, F/Female), and a `WIC` block whose label equals its name. Assert both parse with labels and levels.
   - `canonical_concept`: exact, case, "as <role>", wrong role is rejected, unknown is rejected.
   - The validator rejects an unknown concept.
   - The replay integration test still passes; re-record a cassette only if the B prompt change requires it.
7. **Gate:** `uv run pytest`, lint, strict mypy all green. Re-ingest the real codebooks with a one-off check that `cdc_linkco15` now has `SEX`, `CIG_0..3`, `BFED`, `BMI`, `PAY`, `WIC`, `ILIVE`, `ILP_R`, `MHTR` (233 → 245 variables), and that the other 6 counts are unchanged.
8. **Preserve Friday's logs.** `run_pipeline.sh` overwrites `$RD.log`. Copy `runs/suid_poc_20261103.log` to `runs/suid_poc_20261103.fri-failed.log`, and do the same for `driver.log`. Commit Phase 1 (code). The user pushes.
9. **Restart** (Ollama is up; check with `curl -s localhost:11434/api/tags`), without `--auto-approve`:
   `nohup scripts/run_pipeline.sh configs/suid.yaml runs/suid_poc_20261103 > runs/suid_poc_20261103.driver.log 2>&1 &`
   A is a cache hit. B makes 28 calls, about 4–5 h or more with retries. It stops with `Stopped at review B` (rc 2) and writes `review_B.md`.

## Phase 2: Independent pathways (build while B runs)

Do not change anything in B's cache key during Phase 2 (decompositions, sources, model, b_max params, B prompt). Otherwise B's hours of calls rerun. The new checks are separate artifacts with their own keys.

### 2a. Ingestion audit (an independent check on the parser)

New `src/mmf/ingest/audit.py` with `audit_codebook(doc, ds) -> CodebookAudit` (pydantic model in `schemas/dataset.py`). It deliberately shares no extraction logic with `pass1_regex`.

- **Anchor reconciliation (hard check).** Find every NVSS position anchor: a `^\d{1,4}(-\d{1,4})?$` line followed by a length line and a file-flag line within the next non-empty lines. Each non-FILLER anchor must correspond to exactly one extracted variable whose `notes` position matches. Unmatched anchors are an ingest error (`StageInputError("ingest_<id>", ...)`). Under the "validators, not prompts" rule, a codebook silently missing variables must not reach B.
- **Identifier census (soft check).** Every standalone codebook-style token (`^[A-Z][A-Z0-9_]{2,23}$` on its own line or in a table name cell, not in `_STOPWORDS`, not an extracted name) is listed with page and context in `sources/<id>.audit.json`. The count goes to `manifest.warnings`. This should also expose the PRAMS P8 Std II parser gap (4 variables; HANDOFF 4.A.3).
- Wire it into `pipeline.ingest_sources()` after `build_datasource`, and on cache hits too (as A's gate does at `pipeline.py:184`). Write the audit file. The audit does not alter the `DataSource`, so B's key is unchanged.
- Tests: fixture with an anchor whose variable is missing raises an error; census lists an unextracted identifier.
- Validate on all 7 real codebooks. Expect 0 unmatched anchors after the Phase 1 fix. Read each census with the user before tightening anything.

### 2b. Stage B embedding cross-check (an independent check on LLM mappings)

The LLM pathway is unchanged and still decides the mappings. The embedding pathway independently ranks the codebook variables for each concept. Disagreements are flagged for the human reviewer, and neither pathway overrides the other.

- **Embedder.** Add an `Embedder` protocol in `src/mmf/llm/base.py`, and `OllamaEmbedder` in `src/mmf/llm/ollama.py` using `ollama.Client.embed(model, input=[...])` with batching and a digest from `list()`. It is local only; the cloud backend gets none. Prerequisite: `ollama pull mxbai-embed-large`.
- **Config** (`src/mmf/config.py` `RunConfig`): `embed_model: str = "mxbai-embed-large"`, `b_check_top_k: int = 10`, `b_check_miss_threshold: float` (provisional; calibrate on this run and record the value and why). Add `numpy` to `pyproject.toml` dependencies; about 5.5k × 1024 cosine products in pure Python would be slow.
- **Fingerprints** (new `src/mmf/components/b_crosscheck.py`):
  - Each variable becomes `"{name}: {label}. Values: {levels[:8] joined}. {notes}"`. The label and levels carry the meaning that opaque codenames (CIG_0, BFED) lack.
  - Each concept becomes `"{concept} ({role}): {operationalization}"`, with mxbai's query prefix `"Represent this sentence for searching relevant passages: "`.
  - Cache vectors under `cfg.cache_dir/embeddings/<model-digest>/<sha256(text)>.json`.
- **Verdict per (concept, source)**, comparing B's LLM row to that source's embedding top-k:
  - `agree`: the LLM variable is in the top-k.
  - `llm_outside_topk`: a possible stretch or wrong mapping.
  - `possible_miss`: the LLM said none, but the top-1 score ≥ threshold.
  - `both_none`.
  - Each record also carries the top-k `(name, label, score)`.
- **Schema:** `SchemaCheck` in `schemas/dataset.py`.
- **Pipeline:** a new `stage_b_check(smap, decs, sources)` between `stage_b` and its review gate. Key = `_h(smap json, sources json, embed_model, digest, k, threshold)`; stored as `B_check.json`. Restructure `stage_b` so the gate runs after the check.
  - Since `review_B.md` exists with `approved: false`, the next run rewrites it with the check included (`_review_gate`, `pipeline.py:119-126`).
- **Review rendering:** extend `render_review` / `src/mmf/report/templates/review.md.j2` with an optional "Cross-check (embedding vs LLM)" section above the JSON. It lists `llm_outside_topk` and `possible_miss` first, with top-3 candidates and labels, then counts.
- **Tests:** a fake embedder (deterministic vectors) gives verdict logic for all 4 cases, cache-key stability, and a review render containing the section.
- **Not in scope (record in HANDOFF §4):**
  - Using retrieval to narrow the variables shown to the LLM (a big B speed-up). This would make the pathways non-independent, so it needs its own design and evaluation decision.
  - The validators-off (L−) ablation must also be able to turn this check off.

### Phase 2 gate and apply

- Full test suite, lint and mypy pass; commit Phase 2. The user pushes.
- When the run stops at review B, rerun `uv run mmf run configs/suid.yaml --run-dir runs/suid_poc_20261103`. Sources are a cache hit with the audit applied, and B is a cache hit. The B check runs in minutes, and `review_B.md` is regenerated with the cross-check.

## Phase 3: Review and finish (the original Monday checklist)

1. **Review B with the user**, using `B_check` flags first. Propose edits as a list (wrong or stretched mappings, vague names, near-duplicates, and deletion of the about 32 mouse/neuron concepts) and **do not edit `B_schema.json` until approved**. Then approve: set `review_B.md` to `approved: true` or run `uv run mmf approve runs/suid_poc_20261103 B`.
2. Rerun `scripts/run_pipeline.sh configs/suid.yaml runs/suid_poc_20261103` (no `--auto-approve`). C runs and stops at review C.
3. Review `C_gaps.json` / `review_C.md` in the same way, then approve and rerun. D and E run (about 2 h) and `report.md` is written. `driver.log` ends `DONE`.
4. Update HANDOFF §1–3 with the outcome and commit. The user pushes.

## Critical files

- `src/mmf/ingest/codebook.py` (parser fix, `PARSER_VERSION`)
- `src/mmf/ingest/audit.py` (new)
- `src/mmf/pipeline.py` (cache keys, audit wiring, `stage_b_check`, gate order)
- `src/mmf/components/b_schema_map.py` (concept check, warnings)
- `src/mmf/components/b_crosscheck.py` (new)
- `src/mmf/llm/base.py` and `src/mmf/llm/ollama.py` (Embedder)
- `src/mmf/config.py`, `src/mmf/schemas/dataset.py`
- `src/mmf/prompts/b_schema_map.md`
- `src/mmf/report/markdown.py` and `templates/review.md.j2`
- `pyproject.toml` (numpy)
- `tests/unit/test_ingest.py`, `tests/unit/test_components.py`, `tests/fixtures/mini_nvss_guide.txt`
- `docs/architecture.md` (document both pathways), `docs/HANDOFF.md`

## Verification

- Phase 1: `uv run pytest`, lint and mypy are green. `cdc_linkco15` has 245 variables including the 12, and other counts are unchanged. The restarted run reaches `Stopped at review B` with `B_schema.json` present. No B concept names outside the sent set. `manifest.json` warnings list the canonicalization counts.
- Phase 2: the tests above pass. `sources/*.audit.json` exist with 0 unmatched anchors. `B_check.json` exists and `review_B.md` shows the cross-check section. Spot-check: `Infant sex`→`SEX` is `agree`; `Maternal smoking during pregnancy`→`CIG_*` for cdc_linkco15 is not `possible_miss`; mouse concepts are `both_none`.
- End: `driver.log` ends with `DONE`, and `report.md` exists and was reviewed at B and C.

## Restart prompt (paste after clearing context)

> Read `docs/plans/2026-11-09-ingest-audit-and-b-crosscheck.md` and `docs/HANDOFF.md`. Check `git log` and `git status` to see which steps are already done; step 0 (record) should be committed. Then continue from the first unfinished step. Phase 1 is the parser fix with `PARSER_VERSION`, prompt hashes in the B–E cache keys, the B concept-name check with canonicalization and warnings, tests, preserving Friday's logs, committing, and restarting `runs/suid_poc_20261103` without `--auto-approve` in the background. Then Phase 2 (ingestion audit and the mxbai-embed-large B cross-check) while B runs, without touching anything in B's cache key. Ollama may need `ollama serve`, and `ollama pull mxbai-embed-large` before 2b. Don't edit `B_schema.json` or `C_gaps.json` until I approve a proposed edit list. Commit at the end of each phase; I push myself because the deploy key needs my passphrase.
