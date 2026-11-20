## Ricardo Erazo, PhD
## Draft proposal
# SPECIFIC AIMS

## Manuscript-to-Model Framework (MMF):
### A Structured, AI-Assisted Approach to Reproducible Study Design

## Significance

Scientific progress depends on the ability to translate existing findings into new, testable research questions. However, the step linking completed manuscripts to data-driven study design remains informal, investigator-dependent, and not reproducible. Researchers must manually synthesize prior work, identify knowledge gaps, map those gaps to available datasets, and define feasible analytical strategies. This process is time-intensive, inconsistent, and difficult to standardize across projects.

At the same time, generative artificial intelligence (AI) tools offer new capabilities for large-scale text synthesis and cross-referencing. However, their use in scientific research has been limited by a lack of structure, insufficient grounding in real data, and concerns about reproducibility and scientific rigor.

We propose the Manuscript-to-Model Framework (MMF), a structured, human-in-the-loop workflow that uses AI to support, but not replace, scientific reasoning. MMF systematically translates prior manuscripts and dataset documentation into testable, data-aligned research strategies, including clearly defined knowledge gaps, variable mappings, and appropriate model classes. By formalizing this previously implicit step, MMF aims to improve efficiency, reproducibility, and alignment between theory and data.

## Innovation

MMF introduces three key innovations:

1. Formalization of a missing step in scientific workflows
   MMF defines a reproducible process for translating prior findings into feasible study designs, a step that is currently unstructured and rarely documented.

2. Constrained, data-grounded AI integration
   AI outputs are explicitly restricted to:
   - variables present in real datasets
   - valid study designs
   - appropriate statistical model classes
   This avoids unconstrained hypothesis generation and ensures practical feasibility.

3. Human-in-the-loop architecture
   AI is used to propose structured strategies, while all scientific decisions, validation, and implementation remain under investigator control. This preserves methodological rigor and aligns with emerging standards for responsible AI use in research.

## Overall Objective

The objective of this project is to develop, implement, and validate a reproducible framework that translates existing scientific knowledge into actionable, data-driven research strategies.

## Aim 1 — Develop the Manuscript-to-Model Framework (MMF)

We will design a modular workflow that:

- extracts conceptual structure from prior manuscripts
- maps these concepts to available dataset schemas
- identifies 2–3 explicit, testable knowledge gaps[^impl]
- generates structured research strategies, including:
  - research questions
  - variable definitions
  - interaction structures
  - recommended model classes

Outcome: A clearly defined, reproducible framework for hypothesis-to-design translation.

## Aim 2 — Implement MMF as a Local, Executable Software Tool

We will develop a Python-based application that:

- accepts:
  - manuscript text
  - dataset documentation
- produces:
  - knowledge gaps
  - structured research strategies
  - feasibility mappings

The system will support local execution using open-source language models to ensure:

- data privacy
- reproducibility
- transparency

Outcome: A deployable tool enabling researchers to apply MMF across domains.

## Aim 3 — Validate MMF Using a SUID Proof-of-Concept Study

We will apply MMF to an existing research program on sudden unexpected infant death (SUID), integrating:

- prior manuscripts on developmental timing and exposure risk
- CDC linked birth–infant death data
- NCFRP case data

MMF will generate candidate strategies, one of which will be implemented using standard epidemiologic methods (e.g., case-control design, time-stratified modeling). We will evaluate whether MMF produces strategies that are:

- feasible
- interpretable
- aligned with prior findings

Outcome: Demonstration that MMF generates actionable, scientifically valid study designs.

## Expected Impact

This project establishes a reproducible, scalable approach for integrating AI into scientific workflows without compromising rigor. By formalizing the translation from knowledge to study design, MMF has the potential to:

- accelerate hypothesis generation
- improve alignment between theory and data
- enhance reproducibility in research planning

# Key Takeaway

MMF transforms an implicit cognitive process into a structured, reproducible component of scientific investigation, enabling more efficient and rigorous development of data-driven research strategies.

[^impl]: Implementation note (2026-11-19): the implemented Component C shortlists 10 candidate gaps and the investigator picks 5. PRAMS Phases 7–8 serve as the population reference source alongside the CDC and NCFRP data.
