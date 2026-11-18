#!/bin/bash
# Run one Biomni seed inside the macOS sandbox (network: local Ollama only; writes: the run directory only).
# Usage: benchmarks/biomni/run.sh RUN_DIR SEED [extra run_biomni.py args]
set -euo pipefail
RUN_DIR=$(cd "$1" && pwd); SEED=$2; shift 2
BIOMNI_PY=${BIOMNI_PY:-$HOME/Projects/biomni-bench/.venv/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$RUN_DIR/home/.mpl"
curl -sf localhost:11434/api/tags >/dev/null || { echo "Ollama is not running: start it with 'ollama serve'"; exit 1; }
exec sandbox-exec -D RUN_DIR="$RUN_DIR" -f "$HERE/sandbox.sb" \
  env HOME="$RUN_DIR/home" MPLCONFIGDIR="$RUN_DIR/home/.mpl" \
  "$BIOMNI_PY" "$HERE/run_biomni.py" --run-dir "$RUN_DIR" --seed "$SEED" "$@"
