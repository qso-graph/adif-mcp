# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-05-16

### Added

* **ADIF 3.1.7 specification support**. Full official 3.1.7 JSON resources from [adif.org.uk](https://adif.org.uk/317/) installed alongside the sealed 3.1.6 set. New enum entries (pure additive — no breaking changes):
  - New Mode: **OFDM** (Orthogonal Frequency-Division Multiplexing including COFDM)
  - New Submode: **FT2** (Mode MFSK)
  - New Submode: **FREEDATA** (Mode DYNAMIC)
  - New Submode: **RIBBIT_PIX** (Mode OFDM — Images transmitted using Ribbit)
  - New Submode: **RIBBIT_SMS** (Mode OFDM)
* `src/adif_mcp/resources/spec/317/` — full 30-file canonical 3.1.7 JSON set (29 official from upstream ZIP + project-internal `enumerations_country.json` carried forward).
* Test corpus `test/data/ADIF_317_test_QSOs_2026_03_22.adi` (6,197 records, +6 over 3.1.6) — official G3ZOD-generated file from upstream `ADIF_317_resources_2026_03_22.zip`.
* New tests covering the 5 new enum entries (`test_317_new_mode_ofdm`, `test_317_new_submode_ft2`, `test_317_new_submode_freedata`, `test_317_new_submode_ribbit_pix`, `test_317_new_submode_ribbit_sms`, `test_317_submode_count`).

### Changed

* Default spec set switched to **3.1.7** (`__adif_spec__`, `[tool.adif] spec_version`, `[tool.adif_mcp] spec`, `get_spec_text(version=...)` default).
* `test_list_enumerations_has_mode` — Mode record count expectation 90 → 91. Import-only count stays 42 (OFDM is not import-only).
* `test_official_adif_test_file_zero_errors` — switched to the 3.1.7 corpus, record count 6191 → 6197.
* `test_pkg_meta_exposed` — accepted `__adif_spec__` set now includes "3.1.7".
* Docstrings, README, and project URLs updated to reference 3.1.7.

### Preserved

* `src/adif_mcp/resources/spec/316/` — sealed and untouched. Callers explicitly pinning to 3.1.6 continue to work via `get_spec_text(filename, version="316")`.
* `test/data/ADIF_316_test_QSOs_2025_09_15.adi` — sealed for regression reference.

### Reference

* Upstream spec changes: https://adif.org.uk/317/ADIF_317_annotated.htm
* Tracks fleet rollout pattern from IONIS-AI/ionis-devel#49 (also bumps `get_version_info`'s reported `adif_spec_version` from `3.1.6` to `3.1.7`).

## [0.4.4] - 2025-12-28

### **Added**

* **Surgical ADIF Parser**: Implemented a length-aware internal parser (`parse_adif_internal`) that accurately extracts data based on ADIF tag length headers, improving reliability over standard regex splits.
* **ADIF 3.1.6 Authority**: Added tool-based access to authoritative 3.1.6 specification resources, including field definitions and enumerations.
* **Resource Bundling**: Updated build configuration to explicitly include ADIF specification JSON files within the package wheel.

### **Changed**

* **Async Migration**: Refactored core server tools to `async` to support high-performance I/O operations and compatibility with `aiofiles`.
* **Test Suite Modernization**: Migrated the test suite to `pytest-asyncio` with explicit loop scope configuration to ensure stability in CI/CD environments.
* **MCP Content Handling**: Updated tests to correctly index and verify `TextContent` objects returned by the FastMCP tool wrapper.

### **Fixed**

* **Linting & Type Safety**: Resolved 16 high-priority **Ruff** and **mypy** errors, including unused imports (`F401`), module-level import positioning (`E402`), and redundant type casts.
* **Undefined Name**: Replaced the undefined `is_numeric` helper with a robust regex-based number validator for field specification checks.
* **CI/CD Configuration**: Fixed a critical `INTERNALERROR` (Exit Code 3) in GitHub Actions caused by unset `asyncio_default_fixture_loop_scope`.
* **Path Resolution**: Fixed relative path logic in `get_spec_text` to ensure resources are findable regardless of the installation directory.

---

## [0.4.3] - 2025-12-26

### Added
- **Sovereign ADIF 3.1.6 Bridge**: Full local support for the 2025-09-15 specification without external dependencies.
- **Modular Resource Loading**: "Smart Router" logic to handle large specification files (540KB+) without hitting MCP 1MB limits.
- **Deep Relational Validation**: Verified logic for cross-referencing DXCC entities, Subdivisions, and Awards (e.g., blocking VUCC on HF bands).
- **Test Suite**: Added an 18-point functional verification suite covering edge cases like International Code Collisions and Legacy Submodes.

### Fixed
- **Parser Robustness**: Fixed `parse_adif` regex to correctly handle empty data fields and enforce uppercase keys for spec compliance.
- **Linting & Typing**: Resolved all Ruff, MyPy, and Interrogate errors; codebase is now strictly typed and fully documented.
- **API Surface**: Updated documentation to reflect the 11 active tools.

## [0.4.2] - 2025-12-25

### Added
- **Discovery Tools:** Added `get_version_info` tool to allow LLMs to identify the server version and ADIF spec level.
- **System Resources:** Added `adif://system/version` URI for environment verification.
- **Package Integration:** Wired server metadata to pull dynamically from `pyproject.toml` via the `adif_mcp` package.

### Fixed
- **Resource Mapping:** Restored helper logic and explicit routes for all ADIF 3.1.6 specification files.
- **CLI Entry Points:** Restored `run()` and `main()` functions to ensure compatibility with the `adif-mcp` command-line interface.

## [0.4.1] - 2025-12-25

### Fixed
- **Structural Integrity:** Decoupled radio mathematics from `server.py` into `adif_mcp.utils.geography`.
- **Typing & Linting:** Resolved Mypy export errors and Ruff import-sorting conflicts.
- **CLI Entry Point:** Restored `run()` function in `server.py` to fix CLI execution.

### Changed
- **Testing Strategy:** Unit tests now target logic modules directly rather than through the server interface.
- **Standardization:** Enforced strict PEP 8 import grouping and line-length compliance.

## [0.4.0] - 2025-12-25

### High-Level Pivot
Shifted project architecture to a **Schema-First** model based on the authoritative ADIF 3.1.6 Specification (Released 2025-09-15). This replaces experimental service stubs with a strictly-typed validation core.

### Added
- **Official Spec Resources:** Integrated `all.json`, `fields.json`, `enumerations.json`, and `datatypes.json` for ADIF v3.1.6.
- **Versioned Resource Paths:** Implemented `/resources/spec/316/` to support future specification iterations.
- **MCP Resource Contract:** Added URI handlers (`adif://spec/316/*`) allowing AI models to read official specifications directly.
- **Field Catalog:** Added `adif_catalog.json` to define primary fields for AI focus.

### Changed
- **Server Refactor:** Removed `eqsl`, `lotw`, and `qrz` tool stubs to prevent model hallucinations.
- **Type Safety:** Updated `server.py` to pass strict `mypy` type checking with `AnyUrl` and `importlib.resources`.
- **Metadata:** Updated `adif_meta.json` with official ADIF Developers Group attribution.

### Fixed
- Resolved `ruff`, `mypy`, and `interrogate` linting failures in `server.py`.
- Corrected CLI entry point mapping for the MCP server.

## [0.3.12] - 2025-12-25

### Documentation
- **Sovereign Overhaul**: Complete restructure of documentation to match implementation.
- **New Sections**: Added "Operations", "Maintenance", and "Internal API" to `mkdocs.yml`.
- **Testing Playbook**: Added `docs/dev/testing.md` covering "Unknown State" and "Sovereign Handshake" protocols.
- **Release Process**: Added `docs/dev/release-process.md` defining the "Gold Standard" gate.
- **Persona Guide**: Updated to enforce mandatory `--start` date and `creds set` usage.

## [0.3.11] - 2025-12-24

### Fixed
- **CLI Integrity**: Restored root-level `--version` flag support which was shadowed by subparsers.
- **Import Resolution**: Fixed `ImportError` by switching to absolute imports within the CLI dispatcher.
- **Linter Compliance**: Re-organized imports to satisfy Ruff `I001` sorting requirements.

### Added
- **Dynamic Versioning**: Implemented `importlib.metadata` to pull versioning directly from `pyproject.toml`, removing hardcoded version strings.
- **MCP Subcommand**: Finalized the `adif-mcp mcp` entry point for Stdio-based AI integration.

## [0.3.10] - 2025-12-24
- Bump the version tag to generate a new PyPi package.

## [0.3.9] - 2025-12-24

### Added
- **MCP Gateway Subcommand**: Added `adif-mcp mcp` to start the Model Context Protocol server via Stdio.
- **AI Tool Discovery**: Enabled automatic tool registration for LLMs (Gemini, Claude) using the FastMCP framework.

### Changed
- **Architectural Refactor**: Relocated `server.py` to `src/adif_mcp/mcp/` for a cleaner domain-driven structure.
- **Dispatcher Logic**: Updated `cli/root.py` to handle the `mcp` subcommand and provide lazy-loading of server dependencies.
- **Path Resolution**: Improved `adif_meta.json` lookup to support namespaced package deployments.

## [v0.3.7] — 2025-12-24
- Bump version for testing

## [v0.3.7] — 2025-12-24

### Added
- **Core Server**: Initialized `FastMCP` server in `src/adif_mcp/server.py`.
- **Tools**:
    - `get_service_metadata`: Returns service version and features.
    - `validate_qso`: Validates QSO objects against ADIF 3.1.5 Pydantic models.
    - `calculate_distance`: Computes great-circle distance between Maidenhead locators.
    - `calculate_heading`: Computes beam heading (azimuth) between locators.
    - `normalize_band`: Canonicalizes band names (e.g., "20m" -> "20M") and frequencies.
    - `parse_adif`: Parses raw ADIF text blocks into structured JSON.
    - `lookup_country`: Resolves callsigns to DXCC entities using a local prefix map.
- **Integrations (Stubs)**:
    - `eqsl_query`: Queries eQSL inbox/status.
    - `lotw_query`: Queries LoTW reports.
    - `qrz_query`: Fetches QRZ bio/station data.
- **Models**:
    - `QSO` (Pydantic V2) for strict ADIF validation.
    - `Entity` for DXCC country data.
- **Documentation**:
    - `ADIF_MCP_TOOLS.md` and `docs/tools.md` cataloging all available tools.
- **Testing**:
    - `scripts/smoke_test.py` for environment verification (Python 3.11+, Pydantic V2, FastMCP).
    - Comprehensive unit tests in `test/test_server.py`.

### Changed
- **Dependencies**: Upgraded `pydantic` to `>=2.12.0` and added `fastmcp`.
- **Refactoring**: Separated implementation logic from MCP tool decorators in `server.py` for better testability.
- **Type Safety**: Enforced `mypy --strict` compliance across all new modules, including explicit casting for `TypedDict` returns.

## [v0.3.6] — 2025-09-05

### Added
- New `adif-mcp validate-manifest` subcommand (now in `cli/validate.py`) to check `mcp/manifest.json` against bundled JSON schema.
- Credentials management CLI (`adif-mcp creds …`) with keychain/keyring storage; supports `username+password` and `api_key`.
- Persona date-ranged callsign support (e.g., legacy calls merged by providers, user-facing ranges for reporting).
- SSOT filesystem layout with configurable home (`ADIF_MCP_HOME`), standardized `config/`, `logs/`, `data/`, `state/`.
- Lean archive script and Make target for sharing minimal, fast-to-review packages.
- Added `cli.validate-manifest` key to usage.json mapping
- Keeps CLI usage mapping consistent with new validate subcommand

### Changed
- `convert-adi.py` moved to `src/adif_mcp/cli/convert_adi.py` and wired as library + CLI entry (`adif-mcp convert` / `convert-adi` alias).
- Provider metadata discovered from `src/adif_mcp/resources/providers/*.json` with explicit `auth` types.
- CLI reworked to argparse across modules (`root.py` dispatcher; subcommands in dedicated modules).
- Tests and smoke tests updated to import from the package paths.

### Fixed
- ADIF parsing robustness: header station call detection, eQSL `eqsl_qslrdate → eqsl_qsl_date` mapping, band normalization.
- Streaming NDJSON path: typed error records, memory-friendly iteration, correct stats accounting.
- Mypy/ruff/interrogate hygiene across CLI modules (complete type hints, docstrings, line length ≤ 90).

### Developer Experience
- `make gate` validates schema, runs lint/type/doc checks, and performs keychain smoke test on macOS.
- New script: `scripts/make-lean-archive.sh` to output `dist/*.tar.gz` and `dist/*.zip` with essential files.

---

## [0.3.5] - 2025-09-03
### Added
- CLI now exposes `validate-manifest` as a first-class command.
- `Makefile` updated to run `uv run adif-mcp validate-manifest` for consistency.

### Changed
- Refactored CLI entrypoint into `src/adif_mcp/cli/root.py` with modular subcommand registration (`persona`, `provider`, optional `eqsl_stub`).
- Tests updated to use the new CLI structure.
- Manifest validation tests improved with fallback shape checks (ensures `tools` array exists).

### Fixed
- Missing `__version__` and `__adif_spec__` exports in `adif_mcp.__init__.py`.
- MyPy typing issues in manifest tests and CLI tests.

---

## [0.3.4] - 2025-09-02
### Changed:
  - Recator manifest-validate to validate-manifest src/adif_mcp/cli.py
  - Renamed github workflow from manifest-validate.yml to validate-manifest.yml.
  - Updated test/test_cli.py for new validate-manifest target.

### Added
  - Added new target to Makefile: validate-manifest.

### Removed
  - Removed old bootstrap Makefile target for manifest.

### Optional CLI eQSL Stub ( demo / test functions )
```bash
      Commands for the (stub) eQSL integration.

      These commands exercise the manifest-defined tools without calling the real
      eQSL.cc service. Useful for wiring, demos, and end-to-end testing.

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      inbox    Return a deterministic stubbed 'inbox' for the given user.
      summary  Summarize QSO records by band or mode (stub data).
    - Verified Green for ruff, mypy, and interrogate
```
---

## [0.3.3] - 2025-09-02
### Changed
- Remove the eQSL stub (demo / test data ) from the adif-help --help
- Enable stub by running: `ADIF_MCP_DEV_STUBS=1 adif-mcp eqsl --help`
- Verified Green for ruff, mypy, and interrogate

---

## [0.3.3] - 2025-09-02
### Fixed
- Ensure manifest.json is included in dist aand wheel.

---

## [0.3.2] - 2025-09-02
### Fixed
- Ensured `manifest-validate` works reliably in both local and packaged installs by updating `cli.py` to prefer the packaged `src/adif_mcp/mcp/manifest.json` and gracefully fallback to repo manifests.
- Cleaned up CI configuration:
  - Updated `.github/workflows/ci.yml` to run manifest validation inline with other gates.
  - Corrected paths and logic in `manifest-validate.yml` workflow.

### Changed
- Removed redundant manifest validation logic; consolidated to `adif-mcp manifest-validate` for consistency across local, CI, and release builds.
- Minor cleanup of CLI docstrings and UX messages.

---

## [0.3.1] - 2025-09-03
### Fixed
- Restored and migrated `PersonaManager` into the new `adif_mcp.identity` namespace.
- Resolved missing import errors caused by the removal of `persona_manager.py`.
- Cleaned up packaging to ensure identity components ship correctly in wheel and sdist.

---

## [0.3.0] - 2025-09-03

### Added
- New `adif_mcp.identity` namespace with clear separation of:
  - `models` (Persona, ProviderRef types)
  - `store` (JSON persistence)
  - `secrets` (keyring integration)
  - `manager` (high-level PersonaManager with typed errors)
  - `errors` (granular exception classes for credential handling)

- `src/adif_mcp/resources/` module introduced:
  - `providers/*.json` for per-provider field definitions
  - `schemas/manifest.v1.json` for manifest validation
  - `spec/adif_catalog.json` and `spec/adif_meta.json` for ADIF catalog/spec metadata

### Changed
- Migrated old `personas.py` and `persona_manager.py` into `identity/` namespace.
- Moved provider manifests, schemas, and ADIF spec data into `resources/`.
- Updated all probes and adapters to import from `identity` instead of legacy modules.
- CI and pre-commit updated to enforce `ruff`, `mypy --strict`, and `interrogate` across the new layout.

### Removed
- Legacy `scripts/` helpers (`http_probe.py`, `provider_index_probe.py`, etc.) now fully replaced by `adif_mcp.probes.*`.
- Old `mcp/` provider/spec folders replaced by `resources/`.
- Deprecated direct imports from `adif_mcp.personas` / `persona_manager`.

### Notes
- This release introduces **breaking changes** for anyone importing directly from `adif_mcp.personas` or `persona_manager`.
- Downstream users should migrate to the `adif_mcp.identity` namespace.

---

## [0.2.1] - 2025-09-03

### Fixed
- Updated and refactored all test files under `test/` to match the new package layout.
- Restored full test coverage (17/17 passing).
- Fixed CLI `manifest-validate` command to use the in-package validator and packaged/repo manifests.
- Corrected workflow issues in CI:
  - Ensured `uv` is installed and available in pre-commit hooks.
  - Synced dev dependencies for `uv run` hooks in CI.
- Resolved pre-commit “uv not found” failures by updating GitHub Actions workflow.

### Changed
- CI/CD pipelines (lint, type-check, test, manifest validation, pre-commit) now green across all jobs.
- Pre-commit configuration aligned with `uv run` workflows.

### Notes
- This is primarily a **stability/maintenance release** to lock in a clean baseline after the v0.2.0 refactor.

---

## [0.2.0] - 2025-09-03

### Added
- Provider probe framework under `adif_mcp/probes/`:
  - `http_probe` (GET-only probe engine with redaction).
  - `inbox_probe` (persona+provider → safe GET execution).
  - `index_probe` (no-network credential presence check).
- New CLI commands:
  - `adif-mcp provider probe --provider … --persona …`
  - `adif-mcp provider index-check --provider … --persona …`
- Makefile targets `probe-index`, `probe-get`, `probe-all`.
- Centralized credential validation via `PersonaManager.require()` with typed errors.
- One-pager documentation: `docs/probes.md`.

### Changed
- Refactored all scripts into proper package modules (`adif_mcp/probes`, `adif_mcp/tools`, `adif_mcp/dev`).
- CLI now uses in-package probe logic (no more `scripts/` imports).
- Ruff line length standardized to 90 chars.

### Fixed
- Redaction for sensitive parameters (`password`, `token`, `api`, etc.) in probe output.
- Interrogate coverage: added missing docstrings to new modules and helpers.

---

## [0.1.21] - 2025-08-31
### Added
- Introduced **PersonaManager** as the single point of truth for personas, providers, and secrets.
- New script: `provider_index_probe.py` consolidates the old `eqsl_inbox_probe.py` and `provider_inbox_probe.py`.
- `make keychain-test` target now exercises persona add/set/remove flows against macOS Keychain safely.
- Extended pyproject.toml:
  - Defined `[project.optional-dependencies]` groups for dev tooling (ruff, mypy, pytest, interrogate, mkdocs, etc.).
  - Added provider URLs (LoTW, eQSL, QRZ) under `[project.urls]`.
  - Config section `[tool.adif]` now OS-agnostic (`config_dir_name`, `personas_index`).
- Makefile:
  - Added consistent `gate` and `smoke-all` targets with `uv run` for lint, type, test, interrogate.
  - Added `docs-check` and `docs-dev` helpers for MkDocs/Mermaid workflows.

### Changed
- All persona/provider/secret resolution now routed through **PersonaManager**.
- Refactored smoke and probe scripts to depend on PersonaManager (no direct PersonaStore lookups).
- Type safety improvements:
  - Removed redundant `cast()` calls, eliminated `Any` return paths.
  - Added full docstrings and typing to PersonaManager and helpers.
- Consolidated/de-duplicated Makefile `smoke-all` target (removed `scripts/smoke.sh`).
- UI (`persona_ui.py`) removed from repo and stashed for later revisit.

### Fixed
- `make gate` and `make smoke-all` now fully green (ruff, mypy strict, interrogate, pytest).
- MacOS keychain test: fixed handling of `security(1)` return codes when no items remain.
- Pre-commit and CI config aligned with strict typing and lint rules.

### Notes
- This version is **tagged only** (v0.1.21) and not intended for release packaging.
- Breaking change: the following scripts were removed in favor of consolidation:
  - `eqsl_inbox_probe.py`
  - `provider_inbox_probe.py`

---

## [0.1.20] - 2025-08-30
### Added
- Persona CLI enhancements:
  - `persona add`, `persona list`, `persona show`, `persona remove`, and `persona remove-all`.
  - Support for managing provider credentials via system keyring.
  - Validation: reject end date earlier than start date.
  - Automatic normalization of callsigns to uppercase.
  - Improved `persona list` output with optional `--verbose` mode (masks usernames).
  - Keyring backend is echoed when saving credentials.
- New `make keychain-test` target to manually validate persona/credential round-trips (safe for local testing).

### Fixed
- Consistent error handling in CLI commands (`remove`, `remove-all`, etc.).
- Mypy and Ruff compliance across `adif-mcp/{src,scripts,test} `.
- Gate and smoke tests now pass cleanly with real macOS Keychain integration.

### Notes
- This release marks the first complete integration of **Personas** with secure credential storage.
- CI tests avoid touching the real keychain; use `make keychain-test` locally if you want to validate secrets end-to-end.

---

## [0.1.19] - 2025-08-30

### Added
- Persona management (CLI): `persona add|list|show|remove|set-credential`.
- Date-bounded personas to model vanity/contest/event calls (start/end).
- Secure secret storage via system keyring; non-secrets stored in JSON index.
- `PersonaStore` for CRUD over `~/.config/adif-mcp/personas.json` (overrideable via `pyproject.toml`).
- Docs: brief guidance on personas & keyring (operator-facing).

### Changed
- CLI polish and consistent output for persona flows.
- `_personas_index_path()` resolves path from `tool.adif.personas_index` if provided.

### Fixed
- Type-check issues across `personas.py` and CLI; strict mypy now clean.
- Ruff E501 and assorted nitpicks; interrogate coverage at 100%.

### Internal
- `make gate` and `smoke-all` are green (ruff, mypy, interrogate, pytest, manifest).

---

## [0.1.18] - 2025-08-29

### Added
- New script: `scripts/provider_coverage.py`
  - Computes per-provider ADIF field coverage against the canonical catalog.
  - Pretty-printed report with coverage %, missing fields, and status column.
  - Consistent header/title conventions (`DEFAULT_TITLE`, `DEFAULT_DESCRIPTION`).
- Added `TODO.md` for developer notes and future improvements.
- Added `utils.clear()` helper idea for terminal readability (tracked in TODO).

### Changed
- Updated `CONTRIBUTING.md` to require smoke tests before PRs:
  - `ruff`, `mypy`, `interrogate`, `pytest`, and manifest validation.
- Centralized JSON spec & provider files under `mcp/` directory for clarity.
- Improved test coverage to 100% across `src/`, `scripts/`, and `test/`.

### Fixed
- Build hook script (`scripts/build_hooks.py`) cleaned up for Python ≥3.11 only.
- Normalization in ADIF parser (`record_as_qso`) now uppercases callsigns.
- eQSL stub `filter_summary` properly raises `ValueError` for invalid selectors.
- RST validation rejects invalid values (`rst_sent`, `rst_rcvd`).

---

## [0.1.17] - 2025-08-28
### Added
- First pass at `eqsl_stub.py` demo tool.
- ADIF parser and models with validation.
- CLI entrypoints (`adif-mcp version`, `manifest-validate`, `eqsl`).
- Docs: Concepts overview with working Mermaid diagram.
- CI pipeline integration for linting, typing, and manifest validation.

---

[0.1.18]: https://github.com/KI7MT/adif-mcp/releases/tag/v0.1.18
[0.1.17]: https://github.com/KI7MT/adif-mcp/releases/tag/v0.1.17

## [0.1.16] - 2025-08-28

### Added
- MkDocs configuration and CI/CD workflow for documentation publishing
- Mermaid2 diagrams support in docs (flowcharts render correctly)
- Redirects for subdomains (`eqsl.adif-mcp.com`, `lotw.adif-mcp.com`)
- Developer convenience Makefile targets (`docs-serve`, `check-version`, `init`)

### Fixed
- Smoke test isolation issues with `.smoke-venv`
- Pre-commit hook installation steps in `setup-dev`
- Release workflow tag/version mismatch edge cases
- Removed broken sitemap plugin reference

### Changed
- Documentation structure: clearer navigation (`Integrations` vs `Plugins`)
- MkDocs index/overview pages reorganized for clarity
- Adopted consistent `.yml` extension for workflows and mkdocs config

---

## [0.1.15] - 2025-08-27
### Added
  - Added target for publishing to github-release

## [0.1.14] - 2025-08-27

### Added
- Initial documentation publishing to [adif-mcp.com](https://adif-mcp.com)
- Placeholder test suite (`test/test_placeholder.py`) to satisfy CI pytest checks
- Pre-commit hooks and `commitizen` validation for consistent workflow
- Manifest validation script with JSON Schema checks
- Full docstring coverage across all source files

### Fixed
- Type annotation and `mypy` strictness issues with Click decorators
- Ruff/formatting issues in `scripts/validate_manifest.py`

### Changed
- CI/CD pipelines: renamed workflows to `.yml` for consistency
- Adopted `uv` toolchain for dependency management

## Removed
- All previous development tags

## v0.1.18 (2025-08-29)

## [v0.1.1] to [0.1.13] - 2025-08-27
- No formal package release was made during pipline development.
