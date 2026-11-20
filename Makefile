.PHONY: check test lint type smoke ideate
PY_PATHS := src tests benchmarks evaluation scripts
CONFIG ?= configs/suid.yaml
check: lint type test
lint:
	uv run ruff check $(PY_PATHS) && uv run ruff format --check $(PY_PATHS)
type:
	uv run mypy src benchmarks evaluation scripts
test:
	uv run pytest -q
smoke:  ## end-to-end on fixtures against the local model (auto-approves checkpoints)
	./scripts/smoke.sh
ideate:  ## C0-C5 on an existing run with B approved: make ideate RUN_DIR=runs/... [CONFIG=...]
	@test -n "$(RUN_DIR)" || { echo "usage: make ideate RUN_DIR=runs/... [CONFIG=$(CONFIG)]"; exit 2; }
	uv run mmf ideate $(CONFIG) --run-dir $(RUN_DIR)
