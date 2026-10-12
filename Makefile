# -------------------------------
# Project meta
# -------------------------------
PROJECT	?= "adif-mcp"
PYTHON	?= python3

# Persona Variables

# Pull versions from pyproject.toml (Python 3.11+ for tomllib)
PY_PROJ_VERSION := $(shell $(PYTHON) -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])" 2>/dev/null)
# The ADIF version the server serves, from the package itself.
ADIF_SPEC_VERSION := $(shell sed -n 's/^__adif_spec__: Final\[str\] = "\(.*\)"/\1/p' src/adif_mcp/__init__.py)

# Optional defaults printed in the help header (leave blank if N/A)
FROM    ?=
TO      ?=
DB      ?=
PORT    ?=

# -------------------------------
# Color Helpers
# -------------------------------
# Foreground colors
C_R='\033[01;31m'		# red
C_G='\033[01;32m'		# green
C_Y='\033[01;33m'		# yellow
C_C='\033[01;36m'		# cyan
C_NC='\033[0m'		  # no color

# -------------------------------
# Environment / deps
# -------------------------------
.PHONY: bootstrap setup-dev sync add add-dev init
bootstrap: ## Ensure dev tools (ruff/mypy/pytest/interrogate) are installed
	uv sync --group dev || uv sync

setup-dev: ## Create venv, sync deps (incl. dev), install pre-commit hooks
	uv sync --group dev || uv sync
	pre-commit install -t pre-commit -t commit-msg
	@echo "Dev environment ready."

sync: ## uv sync dependencies
	uv sync

add: ## Add a runtime dep (usage: make add DEP=requests)
	@test -n "$(DEP)" || (echo "Usage: make add DEP=<package>[==version]"; exit 1)
	uv add "$(DEP)"

add-dev: ## Add a dev dep (usage: make add-dev DEP=pytest)
	@test -n "$(DEP)" || (echo "Usage: make add-dev DEP=<package>[==version]"; exit 1)
	uv add --group dev "$(DEP)"

init: ## One-time bootstrap: sync deps, install hooks, run smoke-all
	$(MAKE) setup-dev
	$(MAKE) smoke-all
	@echo
	@echo $(C_G)"init complete"$(C_NC)
	@echo

# -------------------------------
# Quality gates
# -------------------------------
.PHONY: lint format type test smoke gate
lint: bootstrap ## Ruff lint
	uv run ruff check .

format: bootstrap ## Ruff format (in-place)
	uv run ruff format .

type: bootstrap ## mypy (src only)
	uv run mypy src

test: bootstrap ## pytest
	uv run pytest -q

smoke: lint type ## quick local gate (lint+type)
	@echo "[smoke] OK"

.PHONY: gate lint type test
gate: ## CI parity gate: lint + type + tests + docstrings
	@echo "[gate] lint (ruff)"
	$(MAKE) lint
	@echo ''
	@echo "[gate] type check (mypy)"
	$(MAKE) type
	@echo ''
	@echo "[gate] interrogate"
	uv run interrogate -c pyproject.toml
	@echo ''

# -------------------------------
# pre-commit
# -------------------------------
.PHONY: pre-commit-install pre-commit-run
pre-commit-install: ## Install pre-commit hooks (pre-commit & commit-msg)
	pre-commit install -t pre-commit -t commit-msg
	@echo "Hooks installed."

pre-commit-run: ## Run hooks on all files
	pre-commit run --all-files

# -------------------------------
# Full smoke (inline; single definition)
# -------------------------------
.PHONY: smoke-all
smoke-all: ## Run smoke checks in a fresh, reproducible env
	@echo "[smoke] lint (ruff)"
	uv run ruff check .
	@echo ''
	@echo "[smoke] format check (ruff)"
	uv run ruff format .
	@echo ''
	@echo "[smoke] type check (mypy)"
	uv run mypy src
	@echo ''
	@echo "[smoke] docstrings (interrogate)"
	uv run interrogate -c pyproject.toml
	@echo ''
	@echo "[smoke-all] OK"
	@echo ''

# -------------------------------
# Version checks
# -------------------------------
.PHONY: print-versions check-version
print-versions: ## Show versions from pyproject.toml
	@clear
	@echo $(C_C)"Project Information"$(C_NC)
	@echo "--------------------------------------------"
	@echo "  Project Name .......: $(PROJECT) "
	@echo "  Project Version ....: $(PY_PROJ_VERSION)"
	@echo "  ADIF Spec Version ..: $(ADIF_SPEC_VERSION)"
	@echo

# Usage:
#   make check-version
#   make check-version VERSION=0.1.23
#   make check-version SPEC=3.1.5
#   make check-version VERSION=0.1.23 SPEC=3.1.5
check-version: ## Ensure VERSION and/or SPEC match pyproject.toml (use VERSION=... SPEC=...)
	@clear
	@echo $(C_C)"Project Information"$(C_NC)
	@echo "--------------------------------------------"
	@echo "  Project Name .......: $(PROJECT) "
	@echo "  Project Version ....: $(PY_PROJ_VERSION)"
	@echo "  ADIF Spec Version ..: $(ADIF_SPEC_VERSION)"

	@if [ -n "$(VERSION)" ] && [ "$(PY_PROJ_VERSION)" != "$(VERSION)" ]; then \
	  echo ; echo $(C_Y)"ERROR: pyproject version ($(PY_PROJ_VERSION)) != VERSION ($(VERSION))"; echo $(C_NC) ;echo ; exit 1; \
	fi
	@if [ -n "$(VERSION)" ]; then echo "✔ version matches ($(VERSION))"; fi

	@if [ -n "$(SPEC)" ] && [ "$(ADIF_SPEC_VERSION)" != "$(SPEC)" ]; then \
	  echo ; echo $(C_Y)"ERROR: ADIF spec version ($(ADIF_SPEC_VERSION)) != SPEC ($(SPEC))";  echo $(C_NC) ;echo ; echo ; exit 1; \
	fi
	@if [ -n "$(SPEC)" ]; then echo $(C_G)"✔ ADIF spec matches ($(SPEC))"$(C_NC); fi
	@echo

# -------------------------------
# Docstring coverage (verbose)
# -------------------------------
.PHONY: docstrings
docstrings: ## Show per-object docstring coverage with file/function lines
	uv run interrogate -vv -c pyproject.toml --fail-under=100 src scripts tests

# -------------------------------
# Full local gate
# -------------------------------
.PHONY: check-all
check-all: ## Ruff + mypy + verbose docstrings
	uv run ruff check src scripts tests
	uv run mypy src scripts tests
	uv run interrogate -vv -c pyproject.toml --fail-under=100 src scripts tests

# -------------------------------
# Clean
# -------------------------------
.PHONY: clean clean-pyc clean-all
clean:  ## Remove build artifacts (dist/build/egg-info)
	rm -rf dist build *.egg-info
	rm -rf site/
	rm -rf .venv
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache

clean-pyc:  ## Remove Python bytecode (__pycache__, *.pyc)
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.py[co]' -delete 2>/dev/null || true
	@find . -name '*$$py.class' -delete 2>/dev/null || true

clean-all: clean clean-pyc  ## Deep clean (incl. smoke venv)
	rm -rf .smoke-venv

# -------------------------------
# Help
# -------------------------------
.PHONY: help
help: ## Show this help
	@clear
	@echo "Developer Commands"
	@echo "--------------------------------------------------------------------------------------------------------"
	@grep -E '^[a-zA-Z0-9_.-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@printf "\n"
