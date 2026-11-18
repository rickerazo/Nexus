"""Run Biomni's A1 agent on the SUID gap-finding task, local Ollama only.

Run with the Biomni venv, inside the sandbox (see run.sh):
  python run_biomni.py --run-dir RUN_DIR --seed 0 [--model qwen2.5:14b] [--num-ctx 32768] [--budget-min 240]

Settings, and why:
- Same model, context window and Ollama server as MMF (qwen2.5:14b, num_ctx 32768), so the comparison is the
  method (agent vs pipeline), not the model.
- Biomni builds ChatOllama without num_ctx or stop sequences (biomni 0.0.8, llm.py). Ollama's default context
  would truncate Biomni's system prompt, so the runner replaces the model with the same one plus num_ctx and the
  stop sequences Biomni passes to every other provider. Temperature stays at Biomni's default (0.7).
- The 11 GB Biomni data lake (omics and molecular databases, nothing on infant death) is not downloaded
  (expected_data_lake_files=[]). Biomni's tool retriever stays on, as by default.
- The run stops after `budget_min` minutes of wall time or Biomni's own 500-step limit; the step log is kept.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--run-dir", required=True)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--model", default="qwen2.5:14b")
ap.add_argument("--num-ctx", type=int, default=32768)
ap.add_argument("--budget-min", type=float, default=240)
ap.add_argument("--task", default=str(Path(__file__).with_name("task.md")))
args = ap.parse_args()

run = Path(args.run_dir).resolve()
inputs, out = run / "inputs", run / f"biomni_seed{args.seed}"
out.mkdir(parents=True, exist_ok=True)
# Every Biomni default points at Ollama, so no helper call can reach a cloud model (the sandbox blocks it too).
os.environ.update(BIOMNI_SOURCE="Ollama", BIOMNI_LLM=args.model, BIOMNI_PATH=str(out / "biomni_home"))
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"):
    os.environ.pop(k, None)

from biomni.agent import A1  # noqa: E402
from langchain_ollama import ChatOllama  # noqa: E402

agent = A1(
    path=str(out / "biomni_home"),
    llm=args.model,
    source="Ollama",
    timeout_seconds=600,
    expected_data_lake_files=[],
)
agent.llm = ChatOllama(
    model=args.model,
    temperature=0.7,
    num_ctx=args.num_ctx,
    seed=args.seed,
    stop=["</execute>", "</solution>"],
)
files = {
    str(p): f"SUID benchmark input: {p.relative_to(inputs)}"
    for p in sorted(inputs.rglob("*"))
    if p.is_file() and p.name != "manifest.json"
}
agent.add_data(files)

task = Path(args.task).read_text().replace("INPUT_DIR", str(inputs)).replace("OUTPUT_DIR", str(out))
(out / "task.txt").write_text(task)
os.chdir(out)

t0, steps, status, solution = time.time(), 0, "finished", ""
with (out / "steps.jsonl").open("w") as log:
    try:
        for step in agent.go_stream(task):
            steps += 1
            text = step["output"]
            if steps > 1 and "<solution>" in text:  # step 1 is the task itself, which contains the template
                solution = text
            log.write(json.dumps({"step": steps, "t_min": round((time.time() - t0) / 60, 2), "output": text}) + "\n")
            log.flush()
            if time.time() - t0 > args.budget_min * 60:
                status = "budget exhausted"
                break
    except Exception as e:  # recorded, not hidden: a crash is a benchmark outcome
        status = f"error: {type(e).__name__}: {e}"

answer = out / "answer.json"
if not answer.exists() and solution:
    m = re.search(r"<solution>(.*?)(</solution>|$)", solution, re.DOTALL)
    j = re.search(r"\{.*\}", m.group(1), re.DOTALL) if m else None
    if j:
        try:
            answer.write_text(json.dumps(json.loads(j.group(0)), indent=1))
            status += "; answer recovered from the final message"
        except json.JSONDecodeError:
            pass
summary = {
    "seed": args.seed,
    "model": args.model,
    "num_ctx": args.num_ctx,
    "status": status,
    "steps": steps,
    "minutes": round((time.time() - t0) / 60, 1),
    "answer_file": answer.exists(),
}
(out / "summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary))
