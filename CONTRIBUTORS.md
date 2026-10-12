# Contributors

This project exists thanks to its contributors.

## Contributors

- Gregory Beam (@KI7MT) — Project lead, architecture, packaging, documentation

## Contribution Checklist

When contributing new code, documentation, or other resources, please ensure:

1. **Coding Standards**
   - Add **docstrings** for all functions, classes, and modules.
   - Run `make test` and ensure all unit tests pass.
   - Run `pre-commit run --all-files` before committing.

2. **Documentation**
   - The README is the documentation; keep it in the layout the other qso-graph MCP servers use.
   - Record every change under `## Unreleased` in `CHANGELOG.md`.

3. **Releases**
   - A change never bumps the version. KI7MT decides when to release; the release pull request to
     `main` sets the version, and `publish.yml` publishes to PyPI and the MCP Registry and then tags.

4. **General**
   - Keep commits atomic and meaningful.
   - Prefer PRs from feature branches.
   - Be respectful and collaborative.

Thank you for helping improve **WSPR AI Lite** 🚀
