# MMF internal validation protocol (DRAFT — to be frozen before any scored run)

Status: **draft v0.1, not yet frozen.** Prerequisites still to build before freezing (validators-off switch for L-, single-manuscript configs for metric 3) are tracked in [HANDOFF.md](HANDOFF.md) §4. The blinded rater-sheet export now exists in `benchmarks/biomni/score.py`; it is written for the Biomni benchmark and can be reused for the protocol conditions. When frozen, record the commit hash here and log every later deviation in the "Deviations" section at the bottom. Scored runs made before freezing do not count.

## Approved amendments (2026-11-12)
Approved by the investigator on 2026-11-12. Reason: the draft rewards gaps that extend the input manuscripts. SUID run v2 produced only "known risk factor × PCA windows" gaps, and the goal is questions the field has not asked.
- **A.** Split the rubric's *Alignment* dimension. It becomes *Coherence* ("consistent with established findings and biologically plausible"), dropping "uses the manuscripts' own constructs". *Novelty* stays a separate dimension.
- **B.** Add an *Importance* dimension (1–5): if answered, would it change prevention or understanding?
- **C.** Give raters a fixed novelty procedure: a time-boxed PubMed search per strategy with logged queries, done by the raters and not by MMF.
- **D.** Demote metric 3 (retrospective recovery) to a secondary sanity check that is reported but not optimized for. Add a leakage check: ask the bare model what it knows about each manuscript.
- **E.** Add baseline condition **B0**: same model, one plain prompt with the manuscripts and data dictionaries, no pipeline. Rate it blind alongside L.
- **F.** Redefine reproducibility for generate-then-narrow gap finding. Report exact repeat with fixed seeds and logged samples, plus shortlist stability across k runs at the theme level, not exact-statement match.
- **G.** Add candidate-pool metrics: number of candidates, how much they differ, novelty-score distribution, and the fraction passing the feasibility checks.
- **H.** Pre-specify a deterministic selection rule (top 3 by a fixed score) so that evaluation runs stay auto-approved and comparable.
- **I.** Update *Inputs* to match `configs/suid.yaml`.

A–E and I are written into the sections below. F, G and H are **approved, not yet specified**; they are written in once the C redesign (gap generation then narrowing) is settled.

## Purpose
Quantify whether MMF produces research questions and strategies that are grounded, reproducible, feasible, coherent, novel and important, and whether the validators (not the prompts) are what provide the guarantees.

## Inputs (fixed; amendment I)
Taken from `configs/suid.yaml`.
- **Manuscripts:** the SUID developmental-timing manuscript (PCA framework, `SUID_manuscript_v9_clean.docx`), the bed-sharing/exposures manuscript (`bedsharing_ms_v7.docx`), and the PubMed abstracts file (`literature/suid_literature_abstracts.md`).
- **Documentation:**
  - NFR-CRS codebook v5.1 (`ncfrp_v51`; case series, deaths 2004–2019);
  - CDC linked birth/infant death public-use file guide, 2015 (`cdc_linkco15`; cases and denominator);
  - CDC natality public-use file guide, 2015 (`cdc_natl15`; denominator);
  - PRAMS Phase 7 ARF codebook (`prams_p7_arf`; reference, 2012–2015);
  - PRAMS Phase 8 ARF codebook (`prams_p8_arf`; reference, 2016–2021);
  - PRAMS Phase 8 Standard Section II codebook (`prams_p8_std2`; reference, 2016–2021);
  - CDC birth/death file variable names and labels (`cdc_codenames`; a lookup list, no role).
- **Source roles:** the role, unit, years held, geography, linkage, weight and missing-data text for each source, as in `configs/suid.yaml`. Every condition that sees the documentation sees this text.
- sha256 of every input recorded in `data/manifest.json` and in each run manifest.

## Conditions
| Condition | Backend | Model | Pipeline | Validators |
|---|---|---|---|---|
| L   | ollama | qwen2.5:14b (digest recorded) | full | on |
| L-  | ollama | qwen2.5:14b | full | **off** (ablation: outputs accepted on first parse) |
| B0  | ollama | qwen2.5:14b | **none** (baseline: one plain prompt) | none |
| O   | openai_compatible (institutional endpoint, TBD) | model TBD when institutional access exists (fingerprint recorded) | full | on |

**B0 (amendment E):** the same model gets one plain prompt with the manuscripts, the data dictionaries and the same source-role descriptions, and is asked for research questions. No pipeline stages, no validators, no retries. The prompt text and its hash are fixed at freezing. Its outputs are rated blind alongside L.

Condition O runs only with institutional credentials and `allow_cloud: true`; if no institutional access exists when the protocol is frozen, O is dropped and noted here.

**Settings:** seed 0, `max_retries` 3, identical prompts (hashes recorded). Temperatures are set per stage in the config (`src/mmf/config.py`, `configs/suid.yaml`): `temperature` (0.0) for JSON answers, `c_ideation_temperature` (0.9) for C1 idea generation, and `c_reason_temperature` (0.7) for the C3 reasoning turn. The values used are recorded in each run manifest. k = 5 repeats per condition for reproducibility. Review checkpoints are auto-approved in evaluation runs (no human edits) so that runs are comparable; the human-in-the-loop effect is assessed separately in Phase 5.

**Selection rule (amendment H, provisional):** until H is specified, the C4 shortlist rule in `src/mmf/components/c_narrow.py` (`SELECTION_RULE`) stands in. Gaps rated below `c_min_importance` (or unrated) are dropped, the rest are ranked by novelty × feasibility, a gap too similar to one already picked (`c_shortlist_max_similarity`) is skipped, and selection stops at `c_shortlist`. The rule text is written into `C_shortlist.json`.

## Metrics (pre-specified)
1. **Grounding rate.** Per stage: fraction of generate() calls accepted on attempt 1; fraction accepted within retries; count of hallucinated variable names, unknown claim ids, and non-verbatim quotes on attempt 1. Source: `manifest.calls` and `llm_log/`.
   Expectation: with validators on, 100% of final outputs are grounded; the attempt-1 rate shows how much the validators do.
2. **Reproducibility.** Across k repeats within a condition: exact-match rate of `(design, model_class)` per strategy; Jaccard overlap of variable-ref sets per strategy (matched by gap order); Jaccard overlap of gap statements after normalization. Reported as mean and range; no threshold is promised in advance. Amendment F (exact repeat plus theme-level shortlist stability) is approved, not yet specified.
3. **Retrospective recovery (secondary; amendment D).** A sanity check, reported but not optimized for. Run with only manuscript 1 (PCA) as input and ask: does any gap/strategy correspond to what manuscript 2 (bed-sharing) actually tested? Judged by two blinded raters on a 0/1/2 scale (none / partial / substantive overlap). Repeat with the manuscripts swapped.
   **Leakage check:** before these runs, ask the bare model (no inputs) what it knows about each manuscript, given its title. Record the answers. If the model already knows a manuscript's findings, its recovery result is reported as possibly leaked.
4. **Expert rubric.** For every rated question or strategy from conditions L, B0 and O (blinded to condition), two raters score 1–5 on feasibility, coherence, novelty, importance and interpretability, using the `evaluation/rubric.md` anchors (amendments A and B):

   | Dimension | 1 | 3 | 5 |
   |---|---|---|---|
   | Feasibility | outcome or key exposure not identifiable | needs a defensible proxy | implementable as written |
   | Coherence | contradicts established findings or is implausible | consistent, loosely argued | consistent and well argued |
   | Novelty | already answered | incremental | untested and informative |
   | Importance | trivial | useful | would change prevention or understanding |
   | Interpretability | unclear what result would support or refute it | clear with effort | fully explicit |

   **Novelty search (amendment C):** before scoring novelty, each rater runs a PubMed search of at most 10 minutes per question and logs the queries in the sheet's `pubmed_queries` column. The raters do this, not MMF.
   Report per-dimension means by condition and quadratic-weighted kappa between raters.
5. **Ablation.** L vs L-: hallucinated-variable rate and rubric feasibility score.
6. **Candidate-pool metrics.** Amendment G: approved, not yet specified.

## Analysis
`evaluation/analyze_eval.py` reads run manifests and rater sheets, outputs the tables above as CSV and Markdown. Descriptive statistics only; no hypothesis tests are planned because n is small and the goal is characterization.

## Blinding
Questions and strategies are exported to rater sheets with condition and run id replaced by a random code; the key is written to `blinding_key.csv`; the repository is public, so raters must not open the key, `scores.csv` or the run folders until scoring is complete. `benchmarks/biomni/score.py` writes such a sheet (`rater_sheet.md`, `rater_sheet.csv`) and its key.

## Reporting
All metrics are reported regardless of outcome, including low reproducibility or low novelty.

## External comparison: Biomni (2026-11-18)
A benchmark of MMF against Biomni (agent `A1`) on the same inputs and the same local model, planned in [docs/plans/2026-11-18-biomni-benchmark.md](plans/2026-11-18-biomni-benchmark.md). It sits outside the protocol conditions above and does not count as a scored protocol run. Results are reported separately in [docs/reports/2026-11-19-mmf-first-runs-and-biomni-benchmark.md](reports/2026-11-19-mmf-first-runs-and-biomni-benchmark.md). A rerun with a large cloud model is pinned until funded through the institute.

## Deviations
(none yet)
