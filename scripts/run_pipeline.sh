#!/usr/bin/env bash
# Run the pipeline for a config. With --auto-approve, review checkpoints B and C are approved
# without human inspection (for unattended/evaluation runs); the review files remain in the run
# directory and the report must be read as UNREVIEWED. Without it, the run stops at each checkpoint.
#   scripts/run_pipeline.sh configs/suid.yaml [run_dir] [--auto-approve]
set -euo pipefail
cd "$(dirname "$0")/.."
CFG=$1; RD=${2:-runs/$(basename "$CFG" .yaml)_$(date -u +%Y%m%dT%H%M%S)}; AUTO=${3:-}
for stage in B C final; do
  # caffeinate keeps the Mac from idle-sleeping mid-call (a closed lid still sleeps unless on power with a display).
  set +e; caffeinate -is uv run mmf run "$CFG" --run-dir "$RD" > "$RD.log" 2>&1; rc=$?; set -e
  grep -v "^INFO httpx" "$RD.log" | tail -40
  if [ "$stage" != final ]; then
    if [ "$rc" -eq 2 ] && [ "$AUTO" = "--auto-approve" ]; then
      uv run mmf approve "$RD" "$stage"; echo "[auto-approved $stage at $(date -u +%H:%M:%S)]"
    elif [ "$rc" -eq 2 ]; then
      echo "Stopped at review $stage: $RD"; exit 2
    else
      echo "run failed before review $stage (rc=$rc); see $RD.log"; exit 1
    fi
  else
    [ "$rc" -eq 0 ] || { echo "final stage failed rc=$rc"; exit 1; }
  fi
done
echo "DONE $(date -u +%H:%M:%S): $RD/report.md"
