# MMF architecture

This document is the contract between components. Code that disagrees with it is a bug in one or the other; fix the contract first.

## Principles that shape the code

1. **Typed handoffs only.** Components exchange pydantic models (`src/mmf/schemas/`). No component reads another's prose.
2. **Constrained by validators, not by prompts.** A prompt asks the model to use only documented variables; a validator *rejects* output that does not. Every stage runs through `llm/structured.generate`, which parses, validates, feeds errors back, and retries up to `max_retries`. Failures surface to the human; they are never silently accepted.
3. **Documentation in, never data.** MMF reads codebooks, user guides and manuscripts. It never reads row-level CDC or NCFRP data.
4. **Local by default, cloud by explicit consent.** Credentials come only from `MMF_*` environment variables (no key files), a cloud backend needs `allow_cloud: true` per run, and only institutional credentials are acceptable for this institute-funded project.
5. **Provenance for every byte of output.** `RunManifest` records input hashes, config hash, backend, model and model digest, prompt hashes, seed, temperature, and every LLM call (attempts, success, raw log file).
6. **Humans gate the science.** Stages B (schema map) and C (gaps) stop for review. The investigator edits the JSON and approves before D runs. The redesigned C (`mmf ideate`) ends at a shortlist from which the investigator picks 5 gaps.
7. **Reproducibility is measured.** Seeds and temperatures are fixed per stage and logged, but identical outputs are not assumed (C1 samples at 0.9). Internal validation (README, Phase 2; protocol in `evaluation_protocol.md`) measures run-to-run agreement.

## Data flow

```
manuscripts (pdf/docx/md/txt)    ──► ingest.pdf ──► Document(pages[])
codebooks  (pdf/xlsx/docx/txt)   ──► ingest.pdf ──► Document ──► ingest.codebook ──► DataSource(variables[])
                                                            pass1 regex  + pass2 LLM  → reconcile (name must appear on cited page)
                                                         └► ingest.audit ──► sources/<id>.audit.json (independent check, see below)

Document ───► A  a_decompose   ──► ManuscriptDecomposition   (per chunk: profile call + claims call; validator: every quote verbatim;
                                                               gate: ≥1 variable and ≥1 claim per manuscript, else stop)
A + DataSource ► B  b_schema_map ──► SchemaMap               (validator: variable ∈ DataSource, compatibility ∈ enum,
                                                               concept ∈ concepts sent, ≥1 mapping; refuses an empty concept list)
B + A + DataSource ► b_crosscheck ──► B_check.json          (embedding pathway; flags only)   ⏸ review_B.md
A + B ──────► C  c_gaps         ──► GapSet                   (legacy, used by `mmf run`; validator: claim ids exist, refs resolve,
                                                               exactly n gaps, prior_art) ⏸ review_C.md
C ─────────► D  d_strategy      ──► StrategySet              (validator: all refs resolve, enum design/model, rate models need an
                                                               offset or a denominator_source, derived inputs resolve)
D + DataSource ► E e_feasibility ──► FeasibilitySet          (deterministic resolution + year overlap + cross-source; LLM caveats)
all ────────► report.markdown   ──► report.md
```

Codebook sources live in `data/codebooks/` and `data/documentation/`. `ingest/pdf.py` loads `.pdf` (pymupdf), `.xlsx`, `.docx` and plain `.md`/`.txt`.

### Redesigned Component C (C0–C5, `mmf ideate`)

`mmf ideate CONFIG --run-dir DIR` runs on a run whose B is approved (`Run.ideate`, `pipeline.py`). It is not yet part of `mmf run`: `mmf run` still calls the legacy `c_gaps`, and D still reads `C_gaps.json`. Modules: `components/c_ideas.py` (C0, C1), `components/c_narrow.py` (C2–C5), `components/roles.py` (source roles). Schemas: `schemas/ideas.py`.

```
DataSource + B ─► C0 c_ideas.build_inventory ──► DataInventory   C_inventory.json   (every variable grouped into topic domains;
                                                                                     338 domains in the SUID run)
A + C0 + roles ─► C1 c_ideas.generate_ideas  ──► IdeaPool        C_ideas.json, C_ideas.md, C_domain_matches.json
                     6 designs × seeds [0, 1, 2] × 5 ideas, temperature 0.9 (c_ideation_temperature)
C1 ────────────► C2 c_narrow.dedupe           ──► DedupedPool     C_dedupe.json      (mxbai cosine ≥ 0.93 joins a group)
C2 + sources ──► C3 c_narrow.ground_ideas     ──► Grounding       C_grounding.json   (two turns: free-text reasoning at 0.7,
                     then JSON at 0 against the nearest variables; design checks in code)
C3 ────────────► C4 c_narrow.rate_importance + shortlist ──► Shortlist  C_shortlist.json
C4 ────────────► C5 c_narrow.review_markdown ──► review_C_shortlist.md  ⏸ the investigator picks 5 of 10
```

- **Designs (C1).** `c_ideas.DESIGNS`: `case_population`, `exposure_rates`, `case_case`, `case_only`, `trends`, `measurement`. Each states the roles it needs (case series, population reference, denominator). Each idea names its sources by role.
- **Grounding (C3).** The JSON turn's source, variable and design enums are narrowed per call. Code checks roles, design needs, survey weights, variables and cited claims. On the final attempt a bookkeeping salvage (`fix_bookkeeping`) drops stray variables and idle sources, adds missing survey weights and fixes cited-claim lists; every fix is recorded in `salvaged`. Years outside a source's `period` never reject an idea: they are recorded as `years_to_acquire`. A model verdict of not groundable goes to `dropped` with its reason.
- **Scoring (C4).** Novelty = 1 − max cosine to any extracted manuscript claim. Feasibility = share of required variables with documented levels or type. Importance (1–5) is a model rating that only filters (`c_min_importance`, default 3). Score = novelty × feasibility. The shortlist (`c_shortlist`, default 10) skips gaps too similar to one already chosen (`c_shortlist_max_similarity`).
- **Review (C5).** `review_C_shortlist.md` lists the funnel counts, the selection rule and the 10 gaps with checkboxes. Nothing downstream reads it yet; the investigator's 5 picks become D's input in a later step.
- **Checkpoints.** Every accepted call is saved under `checkpoints/C_inventory/`, `C_ideas/`, `C_ground/` and `C_importance/`, so an interrupted run resumes. Stage caches use `C_inventory`, `C_ideas`, `C_ground` and `C_shortlist` keys, which include the prompt hashes and logic versions (`C1_LOGIC_VERSION`, `C3_LOGIC_VERSION`).
- **SUID run (2026-11-19).** 85 ideas → 78 grounded, 2 not groundable, 5 failed → 10 shortlisted.

### Source specification (`SourceSpec`, `config.py`)

Each entry under `codebooks:` in a run config describes one source. Besides `id`, `path`, `title` and `llm_extract`:

| Field | Meaning |
|---|---|
| `roles` | `case` (case series; outcomes come only from these), `denominator` (population at risk), `reference` (exposure prevalence in the general population; never an outcome). Empty = a lookup list, not a dataset. `denominator: true` implies the `denominator` role. |
| `population` | Who the records cover. Shown to C. |
| `unit` | What one record is (e.g. one live birth). |
| `years`, `period` | Period covered, as text and as `[first, last]` years held. Years outside `period` are recorded as years to acquire, never a rejection. |
| `weight_variable` | Survey weight every prevalence from this source must use (e.g. `WTANAL`). C3 adds it if missing. |
| `linkage` | What the records can be linked to. Without a linkage, case–reference comparisons are group-level. |
| `geography` | Geographic detail available, including none. |
| `missing` | How missing and don't-know answers are coded. |

`roles.role_problems` stops the run (`StageInputError`) if the roles are inconsistent with the sources.

## Independent pathways (checks that share no logic with what they check)

Each pathway is a second, differently built way of answering the same question. It flags disagreement and never overrides or repairs the primary output.

**Ingestion audit** (`ingest/audit.py`, run on every ingest including cache hits). It shares no regexes, helpers or stopwords with `ingest/codebook.py`.
- *Anchor reconciliation (hard).* Every NVSS `Position / Len / File-flag` header must correspond to exactly one extracted variable with the same position and file flag. Otherwise ingestion stops with `StageInputError`, so a codebook silently missing variables never reaches B. On 2026-11-09 this found 25 `cdc_linkco15` variables the parser dropped (mixed-case names such as `OEGest_Comb`, inline labels, split names).
- *Identifier census (soft).* Codebook-style identifiers standing alone on a line, or in a table's first cell, that are not extracted names are listed in `sources/<id>.audit.json`, and their count becomes a manifest warning. Most entries are SAS format names and capitalized prose. On 2026-11-09 the census exposed PRAMS sections without a Q# column (birth-certificate, analytic and forced-skip variables), which added about 520 PRAMS variables.

**Stage B embedding cross-check** (`components/b_crosscheck.py`, local `mxbai-embed-large` through Ollama). Each variable is embedded as `NAME: label. Values: up to 8 levels.` (layout notes such as position and format are dropped). Each concept is embedded as `concept (role): operationalization` with mxbai's query prefix. For every (concept, source), the pathway compares B's LLM mapping with the embedding top-k (default 10):
- `agree`: the LLM's variable is in the top-k.
- `llm_outside_topk`: a possible stretch or wrong mapping.
- `possible_miss`: the LLM mapped nothing, but the top candidate's cosine is ≥ `b_check_miss_threshold`.
- `both_none`: neither pathway finds a match.

`review_B.md` lists the first two verdicts above the JSON.
- The check has its own cache entry (`B_check`), so it never invalidates B.
- `b_crosscheck: false` turns it off (needed for the validators-off ablation).
- Vectors are cached under `.cache/embeddings/<model>/<digest>/`.

*Threshold calibration (2026-11-09, provisional): 0.65.* On the SUID run, the best-candidate cosine was 0.65–0.81 for the SUID-relevant concepts (sex→`SEX` 0.81, gestational age 0.79, maternal BMI 0.79, smoking 0.72, bed sharing→`CIRroomshare` 0.65). For the ~32 mouse/neuron literature concepts it was 0.55–0.68, and 3 of them exceed 0.65. A false flag costs a reviewer a glance, while a miss is what the check exists to catch, so the threshold sits at the bottom of the SUID-relevant range. Recalibrate on reviewed B output.

**Not done, deliberately:** using embedding retrieval to narrow the variables shown to the LLM would speed up B a lot, but it would make the two pathways dependent. That needs its own design and evaluation decision.

## Schemas (src/mmf/schemas)

| Model | Produced by | Key invariants |
|---|---|---|
| `Variable`, `DataSource` | ingest.codebook | `Variable.name` exactly as printed; `page` cited. |
| `VariableRef(source_id, name)` | B, C, D | Must resolve via `validate.grounding.resolve_refs`. |
| `Claim(id, kind, statement, quote, page)` | A | `quote` verbatim (normalized whitespace/ligatures; fuzzy ≥0.92 fallback for PDF noise). |
| `ChunkProfile`, `ChunkClaims` | A (LLM-facing) | every field `required` in the JSON schema: a grammar-constrained decoder may omit any non-required key, which is how Component A once returned claims only. Never add defaults to LLM-facing models. |
| `ManuscriptDecomposition` | A | claim ids unique and prefixed by manuscript id; variables deduplicated by (concept, role); ≥1 variable and ≥1 claim (missing designs/model classes are manifest warnings). |
| `SchemaMap.mappings[ConceptMapping]` | B | `variable` null ⇔ `compatibility == "none"`; `concept` is a name that was sent, canonicalized (case, trailing "as <role>") with the rewrite count in manifest warnings. The LLM decodes into `SchemaMapOut`/`MappingOut`, with every field required. |
| `CodebookAudit`, `SchemaCheck` | ingest.audit, b_crosscheck | Independent checks; never consumed by a stage. |
| `KnowledgeGap` | C (legacy) | ≥1 supporting claim, ≥1 required variable, non-trivial `prior_art`. |
| `DataInventory`, `IdeaPool`, `DedupedPool`, `Grounding` (`GroundedGap`), `Shortlist` (`GapScore`) | C0–C4 (`schemas/ideas.py`) | `Idea` and `GroundingAnswer` are LLM-facing: every field required. `GroundedGap` extends `KnowledgeGap` with design, sources by role, period, reasoning, `years_to_acquire` and `salvaged`. |
| `Strategy` | D | `design: StudyDesign`, `model_class: ModelClass` (enums in `validate/vocab.py`); interactions have ≥2 refs. A rate model needs an `offset` variable or a `denominator_source` (a source with the `denominator` role; the denominator is its record count per stratum). `outcome.subtypes` lists outcome codes analysed separately (e.g. R95, W75, R99). `derived` declares computed variables (e.g. PCA = `COMBGEST + AGED / 7`) whose inputs must resolve; refer to them as `{source_id: "derived"}`. `time_scale` is the time axis for time-to-event or time-stratified models, or null. Every field is required. |
| `FeasibilityReport` | E | `feasible` ⇔ no blockers and all refs resolved; `not_assessed` always lists power and causality. |
| `RunManifest` | pipeline | one `LLMCallRecord` per generate() call. |

## LLM layer (src/mmf/llm)

- `base.LLMClient` protocol: `complete_json(system, user, json_schema, seed, temperature)`.
- `ollama.OllamaClient` (default): schema-constrained decoding (`format=<json schema>`), `seed`, `temperature`, `num_ctx`; captures the model digest.
- `openai.OpenAICompatibleClient`: any OpenAI-compatible endpoint (`MMF_API_BASE_URL`), `response_format=json_schema`, `seed`; logs `system_fingerprint`. Constructed only when the run config sets `allow_cloud: true` and `MMF_API_KEY` holds an institutional credential; the manifest records `allow_cloud`. Never for restricted documents.
- `prompts.load_prompt(name)`: reads `prompts/<name>.md` (`## system` / `## user` sections, `$placeholders`), returns its sha256.
- `structured.generate(...)`: the only call site. Returns `(object, LLMCallRecord)`; raises `GenerationFailedError` after retries. Writes a full transcript JSON per call to `llm_log/`.

## Run directory

```
runs/<UTC timestamp>_<config hash[:8]>/
  manifest.json        provenance (see above)
  config.yaml          the RunConfig actually used
  sources/<id>.json    DataSource per codebook; <id>.rejected.json = LLM proposals that failed reconcile;
                       <id>.audit.json = ingestion audit (anchors, identifier census)
  A_<manuscript>.json
  B_schema.json  B_check.json  review_B.md
  C_gaps.json    review_C.md                     (legacy C, `mmf run`)
  C_inventory.json  C_ideas.json  C_ideas.md  C_domain_matches.json
  C_dedupe.json  C_grounding.json  C_shortlist.json  review_C_shortlist.md   (C0–C5, `mmf ideate`)
  D_strategies.json
  E_feasibility.json
  report.md
  llm_log/<ts>_<stage>.json   A: A_<ms>_<chunk>_{profile,claims}; B: B_schema_map_<group>_<concept batch>
  checkpoints/{B,C_inventory,C_ideas,C_ground,C_importance}/   one file per accepted call; resumes a stopped run
```

Stage caching: `manifest.stage_hashes[stage]` is the sha256 of the stage's inputs (upstream JSON + model + relevant config + the stage's prompt hashes, so editing a prompt reruns that stage; ingestion also includes `codebook.PARSER_VERSION`, so a parser fix re-ingests). A stage reruns only if that hash changed or its file is missing. Editing `B_schema.json` by hand therefore invalidates C, D, E automatically.

## Review checkpoints

`review_B.md` / `review_C.md` are rendered with front matter `approved: false`. The pipeline exits with code 2 and prints the resume command. The investigator inspects, optionally edits the stage JSON, then sets `approved: true` (or `mmf approve <run_dir> B`) and re-runs. The approved JSON, not the markdown, feeds downstream stages.

`mmf ideate` stops at `review_C_shortlist.md`, which has no front matter: the investigator ticks 5 of the 10 gaps. Wiring those picks into D is an open step.

## Failure modes that stop a run

- `GenerationFailedError`: a stage's output still failed validation after `max_retries` re-prompts. The failed call is recorded in the manifest (it counts toward grounding-rate metrics).
- `StageInputError`: a stage's input is unusable, e.g. Component A extracted no variables or no claims from a manuscript, or Component B received no concepts. The CLI exits with code 1. Empty input is never passed downstream, because a model would fill the gap with something ungrounded that validators cannot catch (B once mapped codebook labels onto themselves).

## Extending to a new domain

1. Add the dataset's documentation under `data/codebooks/` or `data/documentation/`, give it a `SourceSpec` entry with its roles, and, if its layout is new, a deterministic pass in `ingest/codebook.py` (keep the reconcile rule unchanged).
2. Extend `validate/vocab.py` enums if the domain needs designs or model classes not listed. Do not relax validators.
3. Prompts are domain-neutral; domain knowledge enters through the manuscripts and codebooks.

## What MMF does not do

No statistical modelling, no inference, no power calculation, no causal assessment, no reading of row-level data. Every report says so.
