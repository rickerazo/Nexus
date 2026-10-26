#!/usr/bin/env bash
# End-to-end smoke run on test fixtures with the local model, auto-approving review checkpoints.
set -euo pipefail
cd "$(dirname "$0")/.."
RD=${1:-runs/smoke_$(date -u +%Y%m%dT%H%M%S)}
for stage in B C final; do
  set +e; uv run mmf run configs/smoke.yaml --run-dir "$RD"; rc=$?; set -e
  if [ "$stage" != final ]; then
    [ "$rc" -eq 2 ] || { echo "expected review stop at $stage, got rc=$rc"; exit 1; }
    uv run mmf approve "$RD" "$stage"
  else
    [ "$rc" -eq 0 ] || { echo "final run failed rc=$rc"; exit 1; }
  fi
done
echo "smoke OK: $RD/report.md"
