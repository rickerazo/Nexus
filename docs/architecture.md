# MMF architecture

This document is the contract between components. Code that disagrees with it is a bug in one or the other; fix the contract first.

## Principles that shape the code

1. **Typed handoffs only.** Components exchange pydantic models (`src/mmf/schemas/`). No component reads another's prose.
2. **Constrained by validators, not by prompts.** A prompt asks the model to use only documented variables; a validator *rejects* output that does not. Every stage runs through `llm/structured.generate`, which parses, validates, feeds errors back, and retries up to `max_retries`. Failures surface to the human; they are never silently accepted.
3. **Documentation in, never data.** MMF reads codebooks, user guides and manuscripts. It never reads row-level CDC or NCFRP data.
4. **Local by default, cloud by explicit consent.** Credentials come only from `MMF_*` environment variables (no key files), a cloud backend needs `allow_cloud: true` per run, and only institutional credentials are acceptable for this institute-funded project.
5. **Provenance for every byte of output.** `RunManifest` records input hashes, config hash, backend, model and model digest, prompt hashes, seed, temperature, and every LLM call (attempts, success, raw log file).
6. **Humans gate the science.** Stages B (schema map) and C (gaps) stop for review. The investigator edits the JSON and approves before D runs.
7. **Reproducibility is measured.** Seed and temperature are fixed and logged, but identical outputs are not assumed; Phase 4 measures run-to-run agreement.

## Data flow

```
manuscripts (pdf/docx/md) ──► ingest.pdf ──► Document(pages[])
codebooks  (pdf)          ──► ingest.pdf ──► Document ──► ingest.codebook ──► DataSource(variables[])
                                                            pass1 regex  + pass2 LLM  → reconcile (name must appear on cited page)

Document ───► A  a_decompose   ──► ManuscriptDecomposition   (validator: every quote found verbatim in Document)
A + DataSource ► B  b_schema_map ──► SchemaMap               (validator: variable ∈ DataSource, compatibility ∈ enum)   ⏸ review_B.md
A + B ──────► C  c_gaps         ──► GapSet                   (validator: claim ids exist, refs resolve, exactly n gaps, prior_art) ⏸ review_C.md
C ─────────► D  d_strategy      ──► StrategySet              (validator: all refs resolve, enum design/model, offset for rate models)
D + DataSource ► E e_feasibility ──► FeasibilitySet          (deterministic resolution + year overlap + cross-source; LLM caveats)
all ────────► report.markdown   ──► report.md
```

## Schemas (src/mmf/schemas)

| Model | Produced by | Key invariants |
|---|---|---|
| `Variable`, `DataSource` | ingest.codebook | `Variable.name` exactly as printed; `page` cited. |
| `VariableRef(source_id, name)` | B, C, D | Must resolve via `validate.grounding.resolve_refs`. |
| `Claim(id, kind, statement, quote, page)` | A | `quote` verbatim (normalized whitespace/ligatures; fuzzy ≥0.92 fallback for PDF noise). |
| `ManuscriptDecomposition` | A | claim ids unique and prefixed by manuscript id. |
| `SchemaMap.mappings[ConceptMapping]` | B | `variable` null ⇔ `compatibility == "none"`. |
| `KnowledgeGap` | C | ≥1 supporting claim, ≥1 required variable, non-trivial `prior_art`. |
| `Strategy` | D | `design: StudyDesign`, `model_class: ModelClass` (enums in `validate/vocab.py`); interactions have ≥2 refs; rate models need `offset`. |
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
  sources/<id>.json    DataSource per codebook; <id>.rejected.json = LLM proposals that failed reconcile
  A_<manuscript>.json
  B_schema.json  review_B.md
  C_gaps.json    review_C.md
  D_strategies.json
  E_feasibility.json
  report.md
  llm_log/<ts>_<stage>.json
```

Stage caching: `manifest.stage_hashes[stage]` is the sha256 of the stage's inputs (upstream JSON + model + relevant config). A stage reruns only if that hash changed or its file is missing. Editing `B_schema.json` by hand therefore invalidates C, D, E automatically.

## Review checkpoints

`review_B.md` / `review_C.md` are rendered with front matter `approved: false`. The pipeline exits with code 2 and prints the resume command. The investigator inspects, optionally edits the stage JSON, then sets `approved: true` (or `mmf approve <run_dir> B`) and re-runs. The approved JSON, not the markdown, feeds downstream stages.

## Extending to a new domain

1. Add the dataset's documentation under `data/codebooks/` and, if its layout is new, a deterministic pass in `ingest/codebook.py` (keep the reconcile rule unchanged).
2. Extend `validate/vocab.py` enums if the domain needs designs or model classes not listed. Do not relax validators.
3. Prompts are domain-neutral; domain knowledge enters through the manuscripts and codebooks.

## What MMF does not do

No statistical modelling, no inference, no power calculation, no causal assessment, no reading of row-level data. Every report says so.
