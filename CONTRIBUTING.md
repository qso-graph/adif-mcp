# Contributing to ADIF-MCP

Thank you for your interest in contributing! This project is open to contributions from the ham radio and open source community.

## Contributing Philosophy

>"Pretty Code, Pretty Output, Iterative Docs"
>
>An wise old friend and mentor once told me: “We need pretty code and pretty output — and good documentation takes *lots* of iterations.”

It’s a simple rule of thumb:
- **Pretty code** keeps contributors sane.
- **Pretty output** gives users confidence.
- **Pretty docs** bridge the two, but take more work and refinement than once would think.

Following this mindset helps keep the project consistent, approachable, and operator-friendly.

>Contributing Tip: file ideas and concrete items as Issues.

## Prerequisites

To contribute to ADIF-MCP, you will need a working Python ≥3.11 environment with [UV by Astral](https://docs.astral.sh/uv/) installed.

## Development Setup

The following is a quick start in getting the required environment setup. Details workflows will be outlined in the [Dev Guide](./docs/devguide/).

### Clone the Repo and Install Development Dependencies

~~~bash
git clone git@github.com:KI7MT/adif-mcp.git
cd adif-mcp
~~~

This will create a local .venv with all tools needed for linting, typing, docs, and tests.

### Pre-Commit & PR Checklist
Before submitting a PR, you must ensure all validations and smoke tests pass locally, if not thebuild hook
automation will faill after merging the PR.

Minimal Validations
make gate
make smoke-all

~~~bash
# Start fresh
make clean ; make clean-all ; make clean-pyc

# Linting (PEP8, unused imports, formatting, etc.)
uv run ruff check src test

# Attempt to auto-fix any issues reported
uv run ruff check src test --fix

# Attempt to fix formating issues
uv run ruff format src test

# Type checking (strict mode)
uv run mypy src test

# Docstring coverage (must be 100%)
uv run interrogate -v -c pyproject.toml --fail-under=100 --verbose

# MCP manifest validation
make validate-manifest

# Run Unit tests
uv run pytest -q

# Auto run most all of the commands above
make gate

# Run the full smoke test
make smoke-all
~~~

### CLI Validation Testing
Ensure the CLI entry points work as expected.
~~~bash
uv run adif-mcp version
uv run adif-mcp --help
uv run adif-mcp persona --help
uv run adif-mcp provider --help
uv run adif-mcp validate-manifest
~~~

### Optional but Recommended

~~~bash
uv build
~~~

## Code Style & Checks

- Code is formatted with **ruff**.
- **Docstrings** are required (enforced with `interrogate`).
- Pre-commit hooks run automatically:
  - Trailing whitespace
  - EOF fixes
  - YAML/JSON/TOML validation
  - Docstring coverage
  - Artifact blocking (no `site/`, DuckDB, etc. in commits)

## Documentation Style Tips

When contributing to the docs (/docs):
	•	Always use ~~~ fences for code/diagram blocks

Example:

~~~mermaid
graph LR
  A --> B
~~~

This avoids issues where triple backticks (```) can be consumed by some editors, automated parsers, or the chat interfaces.

	•	Mermaid Diagrams
	•	Use ~~~mermaid fences.
	•	Remember: labels containing spaces or HTML (e.g., <br/>) must be wrapped in quotes:

~~~
flowchart LR
  A["Operator<br/>(Ask in plain English)"] --> B["Agent / LLM<br/>(Chat or Voice)"]
~~~

### Mermaid Diagrams — Gotcha

Mermaid diagrams will fail silently and render as plain text if labels use `<br/>`, `:`, `{}`, `[]` or other special characters without quotes.

✅ Always wrap labels in double quotes ` "what you want to say""`. The following will render correctly:

~~~bash
flowchart LR
  A["Operator<br/>(Ask in plain English)"] --> B["Agent / LLM<br/>(Chat or Voice)"]
~~~

❌ This Will not render:

~~~bash
flowchart LR
  A[Operator<br/>(Ask in plain English)] --> B[Agent / LLM (Chat or Voice)]
~~~

## 👥 Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of people who have helped shape this project.

## 📜 License

By contributing, you agree that your contributions will be licensed under the [LICENSE](LICENSE) of this repository.
