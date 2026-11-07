# MMF internal validation protocol (DRAFT — to be frozen before any scored run)

Status: **draft v0.1, not yet frozen.** Prerequisites still to build before freezing (validators-off switch for L-, blinded rater-sheet export, single-manuscript configs for metric 3) are tracked in [HANDOFF.md](HANDOFF.md) §4. When frozen, record the commit hash here and log every
later deviation in the "Deviations" section at the bottom. Scored runs made before freezing do not count.

## Purpose
Quantify whether MMF produces strategies that are grounded, reproducible, feasible, scientifically
aligned, and non-trivial, and whether the validators (not the prompts) are what provide the guarantees.

## Inputs (fixed)
- Manuscripts: the SUID developmental-timing manuscript (PCA framework) and the bed-sharing/exposures manuscript.
- Documentation: PRAMS Phase 7 ARF, PRAMS Phase 8 ARF, PRAMS Phase 8 Standard Section II, CDC linked birth/infant death guide; NCFRP data dictionary if obtainable.
- sha256 of every input recorded in `data/manifest.json` and in each run manifest.

## Conditions
| Condition | Backend | Model | Validators |
|---|---|---|---|
| L   | ollama | qwen2.5:14b (digest recorded) | on |
| L-  | ollama | qwen2.5:14b | **off** (ablation: outputs accepted on first parse) |
| O   | openai_compatible (institutional endpoint, TBD) | model TBD when institutional access exists (fingerprint recorded) | on |

Condition O runs only with institutional credentials and `allow_cloud: true`; if no institutional access exists when the protocol is frozen, O is dropped and noted here. Seed 0, temperature 0, `n_gaps` 3, `max_retries` 3, identical prompts (hashes recorded). k = 5 repeats per condition for reproducibility. Review checkpoints are auto-approved in evaluation runs (no human edits) so that runs are comparable; the human-in-the-loop effect is assessed separately in Phase 5.

## Metrics (pre-specified)
1. **Grounding rate.** Per stage: fraction of generate() calls accepted on attempt 1; fraction accepted within retries; count of hallucinated variable names, unknown claim ids, and non-verbatim quotes on attempt 1. Source: `manifest.calls` and `llm_log/`.
   Expectation: with validators on, 100% of final outputs are grounded; the attempt-1 rate shows how much the validators do.
2. **Reproducibility.** Across k repeats within a condition: exact-match rate of `(design, model_class)` per strategy; Jaccard overlap of variable-ref sets per strategy (matched by gap order); Jaccard overlap of gap statements after normalization. Reported as mean and range; no threshold is promised in advance.
3. **Retrospective recovery.** Run with only manuscript 1 (PCA) as input and ask: does any gap/strategy correspond to what manuscript 2 (bed-sharing) actually tested? Judged by two blinded raters on a 0/1/2 scale (none / partial / substantive overlap). Repeat with the manuscripts swapped.
4. **Expert rubric.** For every strategy from conditions L and O (blinded to condition), two raters score 1–5 on feasibility, alignment with prior findings, novelty vs triviality, interpretability using `evaluation/rubric.md` anchors. Report per-dimension means by condition and quadratic-weighted kappa between raters.
5. **Ablation.** L vs L-: hallucinated-variable rate and rubric feasibility score.

## Analysis
`evaluation/analyze_eval.py` reads run manifests and rater sheets, outputs the tables above as CSV and Markdown. Descriptive statistics only; no hypothesis tests are planned because n is small and the goal is characterization.

## Blinding
Strategies are exported to rater sheets with condition and run id replaced by a random code; the key is held in `evaluation/blinding_key.csv` (gitignored) until scoring is complete.

## Reporting
All metrics are reported regardless of outcome, including low reproducibility or low novelty.

## Deviations
(none yet)
