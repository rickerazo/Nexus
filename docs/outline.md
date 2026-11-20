## Ricardo Erazo, PhD
## Draft proposal
# Manuscript-to-Model Framework (MMF): A Structured, AI-Assisted Approach to Reproducible Study Design

## Abstract

The transition from completed research findings to new, data-driven study designs remains an informal and poorly standardized step in scientific workflows. Investigators must synthesize prior literature, identify knowledge gaps, map those gaps to available datasets, and define feasible analytical strategies. This process is cognitively demanding, time-intensive, and not reproducible across investigators or studies.

We present the Manuscript-to-Model Framework (MMF), a structured, human-in-the-loop workflow that integrates generative artificial intelligence to support this translation step. MMF does not perform statistical analysis or generate conclusions. Instead, it systematically transforms prior manuscripts and dataset documentation into testable research strategies, including explicitly defined knowledge gaps, variable mappings, study designs, and appropriate model classes.

The framework is implemented as a modular, Python-based application capable of running locally to ensure data privacy and reproducibility. As a proof of concept, MMF is applied to sudden unexpected infant death (SUID) research, where prior developmental findings and heterogeneous data sources present a complex hypothesis-generation challenge. The framework produces a small set of feasible, developmentally structured research strategies, one of which is implemented to demonstrate end-to-end applicability.

MMF formalizes a previously implicit component of scientific reasoning, providing a reproducible and extensible approach for integrating AI into study design while preserving full human oversight and methodological rigor.

# Specific Aims

## Aim 1 — Develop a Structured Manuscript-to-Model Framework

To formalize a reproducible workflow that translates:

- prior research findings (manuscripts)
- and dataset documentation

into:

- explicitly defined knowledge gaps
- data-aligned research strategies
- feasible analytical models

This framework will standardize a currently informal and investigator-dependent step in scientific reasoning.

## Aim 2 — Implement MMF as an Executable, Local Python Application

To develop a modular software tool that:

- accepts:
  - manuscript text
  - dataset documentation
- produces:
  - knowledge gaps
  - structured research strategies
  - variable mappings
  - recommended model classes

The application will support local execution using open-source language models to ensure:

- data privacy
- reproducibility
- independence from external APIs

## Aim 3 — Validate MMF Through a SUID Proof-of-Concept Study

To apply MMF to an ongoing SUID research program by:

- integrating prior manuscripts on developmental timing and exposure risk
- mapping these to CDC and NCFRP datasets

MMF will generate 2–3 candidate research strategies. One strategy will be selected and implemented using standard epidemiologic methods to evaluate:

- feasibility
- interpretability
- alignment with prior findings

This step demonstrates that MMF produces actionable, data-valid study designs.

# Background and Significance

Scientific progress depends on the ability to translate existing knowledge into new, testable questions. However, this translation step—linking prior findings to available data and appropriate analytical methods—is rarely formalized.

Instead, it relies on:
- individual expertise
- iterative reasoning
- ad hoc decision-making

This creates variability in:
- hypothesis quality
- study feasibility
- reproducibility

At the same time, generative AI tools have emerged as powerful systems for text synthesis and pattern recognition. However, their application in scientific research has been limited by:

- lack of domain constraints
- risk of generating non-feasible or trivial hypotheses
- absence of integration with real data structures

The Manuscript-to-Model Framework (MMF) addresses these limitations by:

- constraining AI outputs to:
  - existing datasets
  - valid variable structures
  - feasible model classes
- embedding AI within a human-supervised workflow
- producing outputs that are directly actionable by researchers

# Methods

## Overview

MMF is a modular pipeline consisting of five components:

## Component A — Manuscript Decomposition

Input:
- Prior research manuscripts

Process:
- Extract:
  - core variables
  - conceptual frameworks
  - modeling approaches
  - known limitations

Output:
- Structured representation of the research program

## Component B — Data Schema Mapping

Input:
- Dataset documentation (e.g., CDC, NCFRP)

Process:
- Identify:
  - variable availability
  - measurement definitions
  - overlaps and discrepancies

Output:
- Harmonized variable map
- dataset capability summary

## Component C — Knowledge Gap Identification

Process:
- Identify 2–3 gaps that are:[^impl]
  - consistent with prior findings
  - not previously tested
  - supported by available data

Output:
- Explicit, testable knowledge gaps

## Component D — Research Strategy Generation

For each gap, generate:

- research question
- outcome definition
- exposure variables
- interaction structure
- study design (e.g., case-control)
- recommended model class:
  - logistic regression
  - negative binomial
  - time-stratified models

## Component E — Feasibility Mapping

Assess:

- variable availability
- missingness
- dataset compatibility
- modeling constraints

## Human Oversight

All outputs are:

- reviewed
- validated
- selected

by the investigator prior to implementation.

MMF does not perform:
- statistical modeling
- inference
- interpretation

# Proof of Concept: SUID Application

MMF will be applied to:

- prior SUID manuscripts demonstrating developmental timing using postconceptional age (PCA)
- complementary analyses of sleep environment and exposure risk

The framework will generate candidate strategies exploring:

- developmental interactions (e.g., PCA × exposure)
- sex-specific timing effects
- exposure-dependent shifts in risk

One strategy will be implemented using:

- CDC linked birth–infant death data
- NCFRP case data

to demonstrate feasibility and scientific value.

# Expected Outcomes

- A reproducible framework for AI-assisted study design
- A software implementation enabling local execution
- A validated example demonstrating translation from concept to analysis

# Impact

MMF formalizes a critical but underdeveloped component of scientific research:

*The translation of knowledge into testable, data-aligned study design*

By making this process:

- structured
- reproducible
- scalable

MMF enables more efficient and rigorous scientific discovery while maintaining full human responsibility for all analytical and interpretive steps.

# Key Takeaway

The Manuscript-to-Model Framework does not automate science.

It provides a structured bridge between what we know and what we can test—turning an implicit cognitive process into a reproducible component of the scientific workflow.

[^impl]: Implementation note (2026-11-19): the implemented Component C shortlists 10 candidate gaps and the investigator picks 5. PRAMS Phases 7–8 serve as the population reference source alongside the CDC and NCFRP data.
