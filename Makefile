.PHONY: check test lint type smoke
check: lint type test
lint:
	uv run ruff check src tests && uv run ruff format --check src tests
type:
	uv run mypy src
test:
	uv run pytest -q
smoke:  ## end-to-end on fixtures against the local model (auto-approves checkpoints)
	./scripts/smoke.sh
