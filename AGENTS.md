# Agent guide

<!-- qso-graph:shared:start -->
<!-- Maintained in qso-graph/.github; change this block there. -->
- Keep credentials and keys in the OS credential store at rest; never put them in code, config, logs, tool results, issues, or pull requests.
- Use HTTPS for every connection to an outside service, never disable TLS verification, and validate all input.
- Report security vulnerabilities through private vulnerability reporting, never in a public issue.
- Keep one open pull request per repository, targeting `main`; the next change waits for it or joins it.
- Use the pull request template headings: Issues, What changed, Verification, and Credentials.
- Add each change under `## [Unreleased]` in `CHANGELOG.md`.
- Bump versions only in a release pull request; merging publishes nothing, and release is a separate step.
- Install, run, and develop Python with uv (`uvx`, `uv tool install`, `uv add`, `uv run`); documentation never tells users to use pip.
- Make `README.md` the product page: what it is, who it is for, what it does, installation, and first use.
- Keep caveats and work in progress out of `README.md`.
- Put user guides and images in `docs/user/`; use the rest of `docs/` for developers.
- Expect qso-graph.io to show each product's README and `docs/user/` at its latest Release, so documentation goes live by releasing.
- Follow the [Google Developer Documentation Style Guide](https://developers.google.com/style) and use American English.
- Check user-facing documentation with `vale README.md docs/user` using the organization's Vale configuration.
- See [TEMPLATES.md](https://github.com/qso-graph/.github/blob/main/TEMPLATES.md) for what every public repository carries and the release process.
<!-- qso-graph:shared:end -->

## This repository

- ADIF MCP server: spec parsing, validation, and field enumeration tools.
- Install development dependencies with `uv sync --group dev --frozen`.
- Run locally with `uv run adif-mcp --help`.
- Run CI lint: `uv run ruff check .`.
- Run CI type checks: `uv run mypy src`.
- Run CI tests: `uv run pytest tests --ignore=tests/test_security.py -v`.
- Run CI security tests: `uv run pytest tests/test_security.py -v`.
- Audit locked dependencies: `uv run --with pip-audit pip-audit`.
- Declare all four MCP tool annotation hints; keep them consistent with tool behavior.
- Raise `ToolError` for the tool error cases covered by conformance tests.
