# Useful Command Reference (Dev & Power Users)

A compact, copy-pasteable guide to the most common commands you’ll use while developing or validating adif-mcp.

## 1. Quick Start

```bash
# Install deps (project venv managed by uv)
uv sync

# See CLI help
uv run adif-mcp --help
uv run adif-mcp version
```

## 2. Environments

```bash
# Show which Python uv is using and where the venv lives
uv run python -c "import sys,site;print(sys.executable);print(site.getsitepackages())"

# Recreate venv from lock
uv sync --frozen
```

## 3. Code Quality (local parity with CI)
```bash
# Lint (Ruff)
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .

# Type check (mypy)
uv run mypy src

# Docstring coverage (interrogate)
uv run interrogate -c pyproject.toml
uv run interrogate -vv -c pyproject.toml --fail-under=100 src test
```

## 4. One-shot gates (Make)
```bash
# Local smoke (quick) and full gate (CI parity)
make smoke-all
make gate
```

## 5. Tests
```bash
# All tests
uv run pytest -q

# Specific file or test
uv run pytest -q tests/test_resources.py
uv run pytest -q -k "manifest"
```

## 6. Provider Probes (GET sanity checks)
```bash
# Index (no network): checks persona + provider wiring
uv run adif-mcp provider index-check --provider lotw   --persona MyLOTW
uv run adif-mcp provider index-check --provider eqsl   --persona MyEQSL
uv run adif-mcp provider index-check --provider qrz    --persona MyQRZ

# Network GET (safe probe)
uv run adif-mcp provider probe --provider lotw   --persona MyLOTW    --timeout 30
uv run adif-mcp provider probe --provider eqsl   --persona MyEQSL    --timeout 30
uv run adif-mcp provider probe --provider qrz    --persona MyQRZ     --timeout 30

# Make helpers
make probe-index
make probe-get
make probe-all
```

## 7. Personas & Credentials
```bash
# List / show
uv run adif-mcp persona list
uv run adif-mcp persona show Primary
uv run adif-mcp persona show --by callsign KI7MT

# Add / update (Note: --start is mandatory)
uv run adif-mcp persona add --name Primary --callsign KI7MT --start 2020-01-01
uv run adif-mcp persona add --name ContestW7A --callsign W7A --start 2025-03-01 --end 2025-03-31

# Set credential ( stores ref in index; secret in OS keyring )
uv run adif-mcp creds set --persona Primary --provider lotw --username ki7mt

# Remove one / all
uv run adif-mcp persona remove Primary
uv run adif-mcp persona remove-all --yes
```

## 8. Manifest Validation
## 9. Building & Installing Locally
```bash
# Build sdist+wheel
uv build

# Install the just-built wheel in a throwaway venv to smoke test packaging
python -m venv /tmp/adif-smoke && source /tmp/adif-smoke/bin/activate
pip install ./dist/adif_mcp-*.whl
adif-mcp --help
deactivate
```

## 10. Common Troubleshooting
```bash
# Clear pre-commit envs if hooks act weird
pre-commit clean

# Confirm keyring backend
uv run python -c "import keyring; k=keyring.get_keyring(); print(k.__class__.__module__+'.'+k.__class__.__name__)"
```

## 11. Handy One-liners
```bash
# Show masked usernames for all personas
uv run adif-mcp persona list --verbose
```

## 12. Narrow PyTest
- Run then open last failing traceback interactively
```bash
uv run pytest -k probe -q -x
```

## 13. Suggested Aliases (optional)
```bash
alias amcp='uv run adif-mcp'
alias ruffc='uv run ruff check .'
alias mypyc='uv run mypy src'
alias itg='uv run interrogate -c pyproject.toml'
```

## 14. Makefile Targets

The Makefile provides shortcuts for iterative testing, linting, and packaging.
Run `make help` to see the full list (excerpt below):

> NOTE: **Note:** All commands use `uv` consistently, respect strict lint/type/docstring/test gates, and follow the OS-agnostic/secret-safe practices defined in this project.

```bash
Developer Commands
--------------------------------------------------------------------------------------------------------
add-dev                Add a dev dep (usage: make add-dev DEP=pytest)
add                    Add a runtime dep (usage: make add DEP=requests)
bootstrap              Ensure dev tools (ruff/mypy/pytest/interrogate) are installed
check-all              Ruff + mypy + verbose docstrings + manifest validation
check-version          Ensure VERSION and/or SPEC match pyproject.toml (use VERSION=... SPEC=...)
clean-all              Deep clean (incl. smoke venv)
clean-pyc              Remove Python bytecode (__pycache__, *.pyc)
clean                  Remove build artifacts (dist/build/egg-info)
docs-build             Build docs to ./site
docs-check             Verify Mermaid rendered (div.mermaid present; no code.language-mermaid left)
docs-dev               Generate docs/dev.md from make help
docs-serve             Serve MkDocs locally on http://127.0.0.1:8000/
docstrings             Show per-object docstring coverage with file/function lines
format                 Ruff format (in-place)
gate                   CI parity gate: lint + type + tests + manifest + docstrings, keychain test
help                   Show this help
init                   One-time bootstrap: sync deps, install hooks, run smoke-all
lint                   Ruff lint
pre-commit-install     Install pre-commit hooks (pre-commit & commit-msg)
pre-commit-run         Run hooks on all files
print-versions         Show versions from pyproject.toml
probe-all              Run both index and GET probes
probe-get              Run GET (network) probes for all providers
probe-index            Run index (no network) probes for all providers
release                Tag & push release [usage: make release VERSION=x.y.z SPEC=3.1.5]
setup-dev              Create venv, sync deps (incl. dev), install pre-commit hooks
smoke-all              Run smoke checks in a fresh, reproducible env
smoke                  quick local gate (lint+type+manifest)
sync                   uv sync dependencies
test                   pytest
type                   mypy (src only)
```
