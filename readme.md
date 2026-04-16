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
- important effects (e.g., sex differences) are **time-dependent**, not constant  [oai_citation:0‡Erazo_SUID_manuscript_v1.docx](sediment://file_000000007b14722f996d5cc0b0dcfa45)  

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
- Supports local LLMs (e.g., LLaMA, Mistral)
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

- developmental timing manuscript (PCA framework)  [oai_citation:1‡Erazo_SUID_manuscript_v1.docx](sediment://file_000000007b14722f996d5cc0b0dcfa45)  
- sleep environment manuscript (bed sharing + exposures)  [oai_citation:2‡bedsharing_ms_v3.docx](sediment://file_000000000c08722fafbd176c53084484)  

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

🚧 Early development  

- [x] Conceptual framework defined  
- [x] Proposal and Specific Aims drafted  [oai_citation:3‡outline.md](sediment://file_00000000ff5871fd8386d39728bad647)  [oai_citation:4‡specific_aims.md](sediment://file_00000000e8bc71f89b28e0292df104c9)  
- [ ] Pipeline implementation in progress  
- [ ] SUID proof-of-concept pending  

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