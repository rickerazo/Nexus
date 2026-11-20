# Manuscript-to-Model Framework (MMF) AKA Nexus

A structured, human-in-the-loop pipeline for translating scientific manuscripts and dataset documentation into testable, data-aligned research strategies.

---

## Overview

The **Manuscript-to-Model Framework (MMF)** formalizes a critical but underdeveloped step in scientific research:

> translating existing knowledge into feasible study designs.

In practice, researchers must:
- read prior manuscripts
- identify knowledge gaps
- map those gaps to available datasets
- define appropriate analytical models

This process is:
- manual
- time-intensive
- investigator-dependent
- not reproducible

MMF provides a structured, reproducible approach to this step by combining:

- **manuscript-level knowledge extraction**
- **dataset schema mapping**
- **constrained generative AI assistance**
- **explicit feasibility validation**

Importantly, MMF does **not** perform statistical analysis or generate conclusions.
All scientific decisions, modeling, and interpretation remain under human control.

---

## Motivation

Recent work in SUID (Sudden Unexpected Infant Death) has shown that:

- aligning infants by **postconceptional age (PCA)** reveals developmental structure in risk
- important effects (e.g., sex differences) are **time-dependent**, not constant

However, identifying these structures required:
- iterative hypothesis refinement
- manual alignment between theory and data
- repeated model experimentation

MMF is motivated by the need to **systematize this reasoning process**.

---

## What MMF Produces

MMF does not produce results or papers.

It produces **structured research strategies**, including:

### 1. Knowledge Gaps
- Explicit, testable
- Consistent with prior manuscripts
- Constrained by available data

### 2. Research Strategies
Each strategy includes:
- research question
- outcome definition
- exposure variables
- interaction structure
- recommended study design
- appropriate model class
  - e.g., logistic regression
  - negative binomial models
  - time-stratified approaches

### 3. Feasibility Mapping
- variable availability across datasets
- measurement compatibility
- missingness and limitations
- dataset-specific constraints

---

## Core Principles

### 1. AI as assistant, not decision-maker
- AI proposes structured outputs
- humans validate, select, and implement

### 2. Constrained generation
All outputs must be:
- grounded in real dataset variables
- consistent with known study designs
- analytically feasible

### 3. Reproducibility
- same inputs → same outputs
- pipeline is deterministic given inputs and model

### 4. Separation of roles
| Component | Responsibility |
|----------|----------------|
| MMF | strategy generation |
| Researcher | model implementation, inference, interpretation |

---

## Architecture (High-Level)

MMF is organized as a modular pipeline:

### Component A — Manuscript Decomposition
Extract:
- variables
- conceptual structure
- modeling approaches
- known limitations

---

### Component B — Data Schema Mapping
Parse dataset documentation to identify:
- available variables
- measurement definitions
- overlaps and inconsistencies

---

### Component C — Knowledge Gap Identification
Identify 2–3 gaps that are:
- scientifically meaningful
- not already addressed
- supported by available data

---

### Component D — Strategy Generation
For each gap:
- define research question
- map variables
- propose interaction structures
- recommend model class

---

### Component E — Feasibility Mapping
Evaluate:
- data availability
- compatibility across sources
- modeling constraints

---

## System Design

### Language Model Layer
- Runs a local LLM through Ollama by default (`qwen2.5:14b`); any Ollama model can be configured
- Designed for:
  - privacy
  - reproducibility
  - offline execution

---

### Application Layer (Python)
- modular pipeline implementation
- structured input/output (JSON or YAML)
- reproducible runs

---

### Output Layer
- human-readable reports
- machine-readable strategy objects

---

## Development Plan

### Phase 1 — Pipeline Construction
- define structured prompts
- implement Components A–E
- standardize output schemas

---

### Phase 2 — Internal Validation
- run MMF on known manuscript + dataset pairs
- assess:
  - feasibility of outputs
  - alignment with domain knowledge
  - novelty vs triviality

---

### Phase 3 — Proof of Concept (SUID)
Apply MMF to:

- developmental timing manuscript (PCA framework)
- sleep environment manuscript (bed sharing + exposures)

Goal:
- generate 2–3 candidate strategies
- select one
- implement using standard epidemiologic methods

---

### Phase 4 — Deployment
- package as a reusable Python tool
- enable:
  - local execution
  - domain adaptation
  - reproducible workflows

---

## Validation Strategy

MMF is evaluated on:

- **Feasibility**
  Can the proposed strategy be implemented with available data?

- **Scientific alignment**
  Does it extend prior work coherently?

- **Interpretability**
  Are outputs meaningful to domain experts?

- **Reproducibility**
  Do identical inputs produce identical outputs?

---

## Relevance and Innovation

MMF introduces a new layer in scientific infrastructure:

> a reproducible interface between knowledge and data

Unlike typical AI applications in science, MMF:

- does not generate conclusions
- does not replace statistical modeling
- does not operate unconstrained

Instead, it:

- formalizes expert reasoning
- enforces data realism
- supports high-dimensional hypothesis exploration

---

## Use Cases

- epidemiologic study design
- multi-dataset integration planning
- hypothesis refinement
- grant development
- cross-project synthesis

---

## Limitations

- dependent on input quality (manuscripts, data dictionaries)
- may generate low-novelty strategies without proper constraints
- does not evaluate statistical power or causal validity
- requires domain expertise for final decision-making

---

## Status

🚧 Early development (November 2026)

**Picking the project up? Start with [docs/HANDOFF.md](docs/HANDOFF.md)**: current state, what is running, and next steps.

- [x] Conceptual framework defined
- [x] Proposal and Specific Aims drafted — see [docs/outline.md](docs/outline.md), [docs/specific_aims.md](docs/specific_aims.md)
- [x] Pipeline implemented (Components A–E, validators, provenance, review checkpoints) — see [docs/architecture.md](docs/architecture.md)
- [x] Codebook ingestion for the SUID sources (CDC linked birth/infant death, CDC natality, NFR-CRS v5.1, PRAMS Phases 7–8): 6,035 documented variables, parsed deterministically and audited on every ingest
- [x] End-to-end smoke run on test fixtures with the local model; replayed in CI without a model
- [x] Component A fixed to extract variables and study design, and to stop on empty extraction (2026-11-06)
- [x] First full SUID proof-of-concept run, A–E (report v2, 2026-11-11)
- [x] Component C redesigned (`mmf ideate`: inventory, ideas by study design, dedupe, grounding with design checks in code, scoring, shortlist; 2026-11-12 to 11-19)
- [x] Benchmark against Biomni on the same local model (2026-11-19): see [the report](docs/reports/2026-11-19-mmf-first-runs-and-biomni-benchmark.md)
- [ ] Blinded expert rating of the 27 benchmark questions (`runs/biomni_20261118/rater_sheet.md`)
- [ ] Rerun D and E on the investigator's 5 picks from the new shortlist
- [ ] Internal validation (protocol in [docs/evaluation_protocol.md](docs/evaluation_protocol.md) is a draft and must be frozen before any scored run)
- Pinned, only if funded: the Biomni benchmark with a large cloud model through an institutional endpoint

Known issue: the PRAMS Phase 8 Standard Section II codebook parses to only 4 variables; its layout needs a dedicated parser.

The exploratory scripts that preceded this package are kept read-only in [legacy/ai_for_science/](legacy/ai_for_science/).

---

## Quickstart

```bash
# 1. environment (uv manages Python 3.12 and the lockfile)
uv sync

# 2. local model (default backend; no API key needed)
ollama serve &
ollama pull qwen2.5:14b

# 3. tests (no LLM calls)
uv run pytest

# 4. parse a codebook into documented variables
uv run mmf ingest data/codebooks/PRAMS_Phase_8_ARF_Codebook.pdf --id prams_p8_arf

# 5. run the pipeline; it stops at review checkpoints (B: schema map, C: gaps)
uv run mmf run configs/suid.yaml
uv run mmf approve runs/<run_dir> B      # after checking/editing B_schema.json
uv run mmf run configs/suid.yaml --run-dir runs/<run_dir>

# long runs: keeps the Mac awake, logs to runs/<run_dir>.log; --auto-approve skips the
# review stops (the report is then UNREVIEWED: review B and C afterwards and re-run)
scripts/run_pipeline.sh configs/suid.yaml runs/<run_dir> [--auto-approve]
```

**LLM backends.** The default is local Ollama: nothing leaves the machine and no credential is needed. An OpenAI-compatible cloud backend (`backend: openai_compatible`) exists for institutional endpoints and for the evaluation's local-vs-cloud comparison. It refuses to run unless the run config sets `allow_cloud: true` and `MMF_API_KEY` (plus optional `MMF_API_BASE_URL`) is exported in the shell; no key file is ever loaded. This project is institute-funded: use only institutional credentials, never a personal account, and never send restricted documents to a cloud backend. See `.env.example`.

---

## Key Takeaway

MMF does not automate science.

It **formalizes and accelerates the translation of knowledge into testable study design**, making a critical step in research:

- explicit
- reproducible
- scalable

---

## Author

Ricardo Erazo, PhD
Seattle Children’s Research Institute

---
