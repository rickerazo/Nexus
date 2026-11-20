# Biomni benchmark

Compares MMF's redesigned Component C (`mmf ideate`, C0–C5) with Biomni (Stanford SNAP, `biomni` 0.0.8, agent `A1`), a general biomedical agent, on the same SUID gap-finding task. Both get the same inputs and the same local model (`qwen2.5:14b` on Ollama, `num_ctx` 32768), so the comparison is between methods, not models. Biomni was built for frontier cloud models; this tests it outside that setting.

Design, measures and run log: [docs/plans/2026-11-18-biomni-benchmark.md](../../docs/plans/2026-11-18-biomni-benchmark.md). Results: `runs/biomni_20261118/report.md` and [the 2026-11-19 summary report](../../docs/reports/2026-11-19-mmf-first-runs-and-biomni-benchmark.md). A cloud-model arm is pinned until funded.

## Files

| File | Runs in | What it does |
|---|---|---|
| `export_inputs.py` | MMF venv | Writes `RUN_DIR/inputs/`: manuscript texts, every documented variable as CSV, the original documents, `source_roles.md` and a sha256 `manifest.json`. Uses MMF's deterministic ingestion only, no LLM output. |
| `task.md` | | The task prompt: goal, investigator rules, `answer.json` format. |
| `run_biomni.py` | Biomni venv | Runs `A1` for one seed. Sets `num_ctx` and stop tags on Biomni's `ChatOllama`, points every Biomni default at Ollama, removes cloud API keys from the environment, skips the 11 GB data lake. |
| `run.sh` | host | Runs `run_biomni.py` for one seed inside the sandbox. |
| `sandbox.sb` | host | The macOS `sandbox-exec` profile. |
| `score.py` | MMF venv | Applies MMF's C3 code checks and C4 scores to both arms and writes the blinded rater sheet. |

## Install Biomni

Biomni lives in its own venv outside the repo, with Python 3.12. Behind a TLS-intercepting proxy, pass `--native-tls` so uv trusts the system certificates.

```bash
mkdir -p ~/Projects/biomni-bench && cd ~/Projects/biomni-bench
uv --native-tls venv --python 3.12 .venv
uv --native-tls pip install --python .venv/bin/python biomni==0.0.8 langchain_ollama langchain_openai tqdm
```

`run.sh` uses `~/Projects/biomni-bench/.venv/bin/python` by default. Set `BIOMNI_PY` to use another interpreter:

```bash
export BIOMNI_PY=/path/to/biomni/venv/bin/python
```

You also need Ollama running (`ollama serve`) with `qwen2.5:14b` and `mxbai-embed-large` pulled.

## Run

From the repo root:

```bash
# 1. inputs (MMF venv)
.venv/bin/python benchmarks/biomni/export_inputs.py configs/suid.yaml runs/biomni_20261118 [SOURCES_DIR]

# 2. Biomni, one seed at a time, with nothing else using Ollama
benchmarks/biomni/run.sh runs/biomni_20261118 0 --budget-min 300
benchmarks/biomni/run.sh runs/biomni_20261118 1 --budget-min 300
benchmarks/biomni/run.sh runs/biomni_20261118 2 --budget-min 300

# 3. scores and the blinded sheet (MMF venv; needs Ollama for embeddings)
.venv/bin/python benchmarks/biomni/score.py configs/suid.yaml runs/biomni_20261118 runs/suid_poc_20261103_ideas
```

- `SOURCES_DIR` is where the parsed `DataSource` JSON files are read from. Default: `runs/suid_poc_20261103_ideas/sources`. Point it at the `sources/` folder of the MMF run you compare against.
- `run.sh` passes extra arguments to `run_biomni.py`: `--model` (default `qwen2.5:14b`), `--num-ctx` (32768), `--budget-min` (240; the benchmark used 300), `--task`.
- `score.py`'s third argument is the MMF run directory; it reads `C_shortlist.json` and `C_grounding.json` from it.

## Sandbox

Biomni executes model-written Python and bash on the host. `run.sh` wraps each seed in `sandbox-exec -f sandbox.sb`:
- network: only the local Ollama server (`localhost:11434`);
- file writes: only the run directory, `/private/tmp` and `/private/var/folders`;
- `HOME` is set to `RUN_DIR/home`, so Biomni's caches stay in the run directory.

`run.sh` checks that Ollama answers before starting.

## Outputs

In `RUN_DIR`:
- `inputs/`: what both arms received.
- `biomni_seed<N>/`: `task.txt` (the rendered task), `steps.jsonl` (every agent step, with minutes elapsed), `answer.json` (the ranked gaps), `summary.json` (status, steps, minutes), `biomni_home/`.
- `scores.csv` (one row per gap, with the arm), `report.md` (per-run summary).
- `rater_sheet.md`, `rater_sheet.csv` (blinded) and `blinding_key.csv` (code to arm and run).
- `home/`: the sandbox home. Not tracked in git.

A run that stops at the budget or crashes is recorded as its outcome, not rerun.

## Blinding

Give raters `rater_sheet.md` and `rater_sheet.csv` only. Every gap from every run is on one sheet, in random order, under random codes, with arm, run, rank, scores and design label hidden. `blinding_key.csv`, `scores.csv`, `report.md`, `review_C_shortlist.md` and the summary report all reveal which system wrote each question, and they are tracked in this public repo. A rater must not read them, or browse the repo's run folders, before finishing the sheet.
