# Benchmark: MMF vs Biomni on SUID gap finding (2026-11-18)

**Status:** set up and smoke-tested on 2026-11-18. The scored runs start when the MMF run with the "years held are not a limitation" fix finishes (see [the C redesign plan](2026-11-12-c-redesign.md)). There is no more tuning of MMF before this benchmark.

## Question

Given the same inputs and the same local model, does MMF's staged pipeline produce better research questions than a general biomedical agent? Better means:
- more grounded in the documented data;
- more often valid by design;
- more novel;
- rated higher by blinded experts.

Biomni (Stanford SNAP, `biomni` 0.0.8, agent `A1`) is the comparison.

## Arms

| Arm | System | Model | Runs |
|---|---|---|---|
| MMF | `mmf ideate` (C0–C5), top 10 of the shortlist by score | qwen2.5:14b, local Ollama, num_ctx 32768 | 1 (≈ 6 h per run) |
| Biomni | `A1.go_stream(task)` | same model, server and num_ctx; temperature 0.7 (Biomni default); seed 0, 1, 2 | 3 |

The same model is used deliberately. The institute's rule is local models only, and holding the model fixed means the comparison is between methods. Biomni was built and evaluated with frontier cloud models, so this tests it outside its intended setting. The report must say so. A cloud arm (protocol condition O) is added only if institutional credentials ever exist.

## Inputs (identical information, no MMF LLM output)

`benchmarks/biomni/export_inputs.py` writes `RUN_DIR/inputs/`:
- **Manuscripts:** the plain text of the two manuscripts and the abstracts file, from MMF's deterministic loader.
- **Data dictionaries:** every variable of every source as CSV (name, label, type, levels, years, notes), from MMF's deterministic codebook parsing. This is the same variable list MMF uses.
- **Original documents:** the PDFs and spreadsheets.
- **`source_roles.md`:** the investigator's source roles, units, years held, linkage, weights and missing-data codes, the same text MMF's prompts receive.
- **`manifest.json`:** the sha256 of each input.

Biomni gets none of MMF's claims, schema map, inventory, ideas, designs or prompts.

The task (`benchmarks/biomni/task.md`) states the same goal and the same investigator rules MMF works under:
- outcomes come only from case series;
- no rates without a denominator source;
- survey weights for prevalences;
- years held are not a limitation.

It asks for the same output fields MMF produces, as `answer.json`.

## Biomni settings, and deviations from its defaults

- **Context and stop tags.** Biomni 0.0.8 builds `ChatOllama` without `num_ctx` or stop sequences. Ollama's default context would truncate Biomni's system prompt. The runner substitutes the same model with `num_ctx` 32768 and the stop tags (`</execute>`, `</solution>`) that Biomni passes to every other provider.
- **Data lake.** The 11 GB data lake (omics and molecular databases, nothing on infant death) is not downloaded (`expected_data_lake_files=[]`). The SUID inputs are registered with `add_data`. The tool retriever stays on, as by default.
- **Sandbox.** Biomni executes model-written Python and bash on the host. Each run therefore runs under macOS `sandbox-exec` (`benchmarks/biomni/sandbox.sb`):
  - network: only the local Ollama server;
  - file writes: only the run directory and temp directories.
  - Tested on 2026-11-18: Ollama reachable, internet blocked, repo writes blocked.
- **Cloud fallback removed.** The `BIOMNI_SOURCE`/`BIOMNI_LLM` environment variables point every Biomni default at Ollama, and cloud API keys are removed from the environment.
- **Budget:** 300 minutes of wall time per seed, or Biomni's own limit of 500 steps. If a run stops at the budget or crashes, that is recorded as its outcome, not rerun.
- **Install.** The Biomni venv lives outside the repo (`~/Projects/biomni-bench/.venv`, Python 3.12). It was installed through the institutional proxy with `uv --native-tls`.

## Measures

**1. Code checks** (`benchmarks/biomni/score.py`). These are the same checks MMF's C3 enforces, applied after the fact to the top 10 of every run in both arms. No gap is excluded for failing them.
- unknown variables: names not in that source's dictionary;
- variables from sources not listed under a role;
- role errors;
- missing survey weight;
- incidence or risk wording without a denominator source;
- invalid period;
- whether all checks pass.

Years to acquire are reported for information only.

**2. Computed scores,** the same functions as MMF's C4:
- novelty: 1 minus the highest mxbai cosine to any extracted manuscript claim;
- feasibility: the share of known variables that have documented levels or a known type.

**3. Pool measures:** the number of gaps returned, and the highest pairwise cosine between them (redundancy). Wall time is also recorded.

**4. Blinded expert rating** (protocol amendments A–C):
- **Coverage:** every gap from every run goes on one sheet in one template, in random order, under random codes (`rater_sheet.md` and `rater_sheet.csv`). Arm, run, rank, scores and the design label are hidden. MMF writes design labels as fixed codes (`case_only`), so they would reveal the arm; the design is still evident from the question and its sources. The writing style of the rationale may still hint at the arm, and the report should say so. `blinding_key.csv` stays closed until rating is done.
- **Raters:** the investigator and one colleague.
- **Dimensions,** each 1–5:

  | Dimension | 1 | 3 | 5 |
  |---|---|---|---|
  | Feasibility | outcome or key exposure not identifiable | needs a defensible proxy | implementable as written |
  | Coherence | contradicts established findings or is implausible | consistent, loosely argued | consistent and well argued |
  | Novelty | already answered | incremental | untested and informative |
  | Importance | trivial | useful | would change prevention or understanding |
  | Interpretability | unclear what result would support or refute it | clear with effort | fully explicit |

- **Novelty searches:** done by the raters, as a time-boxed PubMed search (10 minutes) per question, with the queries logged in the sheet.

## Analysis

Descriptive only (n is small):
- for each arm, the means and ranges of the code-check rates and computed scores;
- rubric means by arm and dimension, with quadratic-weighted kappa between the two raters;
- the fraction of questions per arm that pass all checks *and* score ≥ 4 on novelty and importance from both raters.

All results are reported regardless of direction.

## How to run

```bash
# 1. inputs (MMF venv)
.venv/bin/python benchmarks/biomni/export_inputs.py configs/suid.yaml runs/biomni_20261118
# 2. Biomni, one seed at a time, with Ollama free of other jobs
benchmarks/biomni/run.sh runs/biomni_20261118 0 --budget-min 300   # then 1, 2
# 3. scoring and the blinded sheet (MMF venv; needs Ollama for the embeddings)
.venv/bin/python benchmarks/biomni/score.py configs/suid.yaml runs/biomni_20261118 runs/suid_poc_20261103_ideas
```

## Run log

- **Wed 14:27–14:41 PST, smoke tests** (`runs/biomni_smoke`):
  - The import, sandbox, Ollama connection and task rendering all work.
  - Biomni's first step (the tool retriever) took 11 minutes, because it queued behind the MMF run on the same Ollama server. Scored runs therefore wait until MMF is done.
  - Scorer tested on the 2026-11-17 MMF shortlist plus a hand-made Biomni answer with planted errors (an unknown variable, a missing weight, risk without a denominator, a wrong role, a future year). Every error was caught.
  - Fixed: answer recovery had matched the JSON template in the task (step 1 of the stream is the task itself). It now reads only a `<solution>` block from a later step.
- **Biomni seeds** (Wed 22:10 – Thu 03:36 PST; MMF was idle throughout):

  | Seed | Status | Steps | Minutes | Gaps |
  |---|---|---|---|---|
  | 0 | stopped at the 300-minute budget; `answer.json` was written mid-run | 130 | 302 | 5 |
  | 1 | finished | 37 | 14 | 9 |
  | 2 | finished | 26 | 10 | 3 |

  - The step logs show no sandbox blocks. Biomni loaded every dictionary CSV. Its "file not found" errors come from paths the model mistyped.
- **MMF:** the C3 rerun with the bookkeeping fixes ran Thu 03:36–04:52 PST. The first scoring, made before that fix, is kept as `*.pre-c3fix.*`.
- **Scores, Thu 04:52 PST** (`runs/biomni_20261118/report.md`, top 10 per run):

  | Arm | Gaps | Pass all checks | Unknown variables | Weight missing | Novelty (mean) | Feasibility (mean) | Max pairwise cosine |
  |---|---|---|---|---|---|---|---|
  | MMF | 10 | 10 | 0/66 | 0 | 0.33 | 0.63 | 0.85 |
  | Biomni seed 0 | 5 | 0 | 8/8 | 5 | 0.20 | 0.00 | 0.83 |
  | Biomni seed 1 | 9 | 1 | 9/10 | 0 | 0.26 | 0.11 | 0.87 |
  | Biomni seed 2 | 3 | 0 | 10/10 | 2 | 0.18 | 0.00 | 0.84 |

- **Reading the Biomni gaps:**
  - Variable names are invented (`SOCIOECONOMIC_STATUS`, `BED_SHARING`, `MOMEDU`).
  - The questions are textbook risk factors (smoking, prematurity, SES, maternal age, education), mostly phrased as incidence.
  - Seed 2 pairs 2015 natality with 2016–2021 cases. Seed 1 asks about geographic variation, which the public-use files do not contain.
- **Reading the MMF gaps:** the variables are real and every check passes. But 4 of the 10 are PRAMS-vs-PRAMS measurement comparisons with no SUID cases, because novelty-as-distance rewards questions off the topic (see the C redesign log). The code checks cannot see topic relevance; the blinded rating can.
- **Not yet done:** the blinded rating of 27 questions (`rater_sheet.md` and `rater_sheet.csv`; the key is in `blinding_key.csv`, tracked like everything else since the repo went public; raters must not open it before finishing).
- **Blinding caveat:** the summary report, `review_C_shortlist.md` and `scores.csv` show which system wrote each question. The second rater must not read them (or the repo's run folders) before finishing the sheet. Give them `rater_sheet.md` and `rater_sheet.csv` only.
- **Summary report:** [docs/reports/2026-11-19-mmf-first-runs-and-biomni-benchmark.md](../reports/2026-11-19-mmf-first-runs-and-biomni-benchmark.md).

## Pinned follow-up: cloud-model arm, if funded

Pinned by the investigator on 2026-11-19. It is not to be run until funding provides an institutional cloud-model endpoint; personal accounts or keys are never used.
- **Why:** this benchmark ran Biomni on a 14B local model, outside its intended setting. A cloud arm tests whether MMF's advantage holds when the agent has a capable model, and how much a better model improves MMF itself (protocol condition O).
- **Design:** the same inputs, task (`benchmarks/biomni/task.md`) and scorer (`score.py`). Biomni runs on the model class it was built for, MMF on the same cloud model, with 3 seeds each. The blinded rater sheet is regenerated over every arm.
- **Changes needed:** `run_biomni.py` switches its model source to the institutional endpoint, and the sandbox profile allows that host. MMF needs `allow_cloud` and the institutional credentials. Nothing else changes.
