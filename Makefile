PY ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: help setup check lint test fmt doctor clean

help: ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

setup: ## create .venv and install jobhunt with dev tools
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -e '.[dev]'
	@echo "Done. Run: source $(BIN)/activate && jobhunt init"

check: lint test ## everything CI runs

lint: ## ruff lint + format check
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

test: ## run the test suite
	$(BIN)/pytest

fmt: ## auto-format and auto-fix
	$(BIN)/ruff format .
	$(BIN)/ruff check --fix .

doctor: ## check your local setup
	$(BIN)/jobhunt doctor

clean: ## remove caches and build output (keeps me/ and .venv)
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
