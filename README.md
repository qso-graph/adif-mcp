<!-- mcp-name: io.github.qso-graph/adif-mcp -->
# adif-mcp

Core [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for **Amateur Radio Logging**, built on the [ADIF 3.1.6 specification](https://adif.org.uk/316/ADIF_316.htm).

## Overview

adif-mcp gives AI agents safe, typed access to Amateur Radio logging data. It validates and parses ADIF records, searches the full ADIF 3.1.6 specification (fields, enumerations, data types), and provides geospatial utilities for Maidenhead locators.

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![ADIF 3.1.6](https://img.shields.io/badge/ADIF-3.1.6-blue)](https://adif.org.uk/316/ADIF_316.htm)
[![PyPI](https://img.shields.io/pypi/v/adif-mcp)](https://pypi.org/project/adif-mcp/)
[![CI](https://github.com/qso-graph/adif-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/qso-graph/adif-mcp/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-qso--graph.io-blue)](https://qso-graph.io/)

## Quick Start

```bash
pip install adif-mcp
```

## Configure Your MCP Client

adif-mcp works with any MCP-compatible client. Add the server config and restart -- tools appear automatically.

### Claude Desktop

Add to `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### ChatGPT Desktop

Configure via Settings > Apps & Connectors, or in your agent definition:

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### VS Code / GitHub Copilot

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "adif": {
      "command": "adif-mcp"
    }
  }
}
```

## Tools

adif-mcp exposes **8 tools** via the Model Context Protocol:

| Category | Tool | Description |
|----------|------|-------------|
| **Validation** | `validate_adif_record` | Validate a raw ADIF string against the 3.1.6 spec |
| **Validation** | `parse_adif` | Streaming parser for large ADIF files with pagination |
| **Spec** | `read_specification_resource` | Retrieve raw JSON for any spec module (band, mode, fields) |
| **Spec** | `list_enumerations` | List all ADIF enumerations with entry counts |
| **Spec** | `search_enumerations` | Search enumeration records by keyword |
| **Geospatial** | `calculate_distance` | Great Circle distance (km) between two Maidenhead locators |
| **Geospatial** | `calculate_heading` | Initial beam heading (azimuth) between two locators |
| **System** | `get_version_info` | Active service version and ADIF spec version |

## Architecture

adif-mcp is the **ADIF specification package** -- validation, parsing, and geospatial tools. Credential management is handled by [qso-graph-auth](https://pypi.org/project/qso-graph-auth/). Service integrations are separate MCP servers:

| Package | PyPI | What It Does |
|---------|------|-------------|
| [`qso-graph-auth`](https://pypi.org/project/qso-graph-auth/) | v0.1.1 | OS keyring credential management, persona CRUD |
| [`adif-mcp`](https://pypi.org/project/adif-mcp/) | v1.0.5 | ADIF 3.1.6 spec tools, validation, parsing, geospatial |
| [`eqsl-mcp`](https://pypi.org/project/eqsl-mcp/) | v0.3.1 | eQSL inbox, verification, AG status, last upload |
| [`qrz-mcp`](https://pypi.org/project/qrz-mcp/) | v0.3.1 | Callsign lookup, DXCC, logbook status/fetch |
| [`lotw-mcp`](https://pypi.org/project/lotw-mcp/) | v0.3.1 | LoTW confirmations, QSOs, DXCC credits, user activity |
| [`hamqth-mcp`](https://pypi.org/project/hamqth-mcp/) | v0.4.0 | Callsign lookup, DXCC, bio, activity, DX spots, RBN, QSO verify |
| [`pota-mcp`](https://pypi.org/project/pota-mcp/) | v0.2.1 | Parks on the Air spots, park info, stats, schedules |
| [`sota-mcp`](https://pypi.org/project/sota-mcp/) | v0.1.5 | Summits on the Air spots, alerts, summit info, stats |
| [`solar-mcp`](https://pypi.org/project/solar-mcp/) | v0.2.0 | Space weather conditions, forecasts, band outlook |
| [`wspr-mcp`](https://pypi.org/project/wspr-mcp/) | v0.3.1 | WSPR beacon spots, propagation, band activity |
| [`iota-mcp`](https://pypi.org/project/iota-mcp/) | v0.1.1 | Islands on the Air lookup, search, nearby groups |
| [`n1mm-mcp`](https://pypi.org/project/n1mm-mcp/) | v0.1.3 | N1MM Logger+ contest state via UDP |
| [`ionis-mcp`](https://pypi.org/project/ionis-mcp/) | v1.2.8 | HF propagation analytics (175M+ signatures) |
| [`qsp-mcp`](https://pypi.org/project/qsp-mcp/) | v0.2.1 | Local LLM ↔ MCP tool relay |

Authenticated servers use [qso-graph-auth](https://pypi.org/project/qso-graph-auth/) for persona lookup and keyring-backed credentials. Operators install only the servers they need. Each server is independently versioned with no unnecessary dependencies.

## Compliance & Provenance

adif-mcp follows the [ADIF Specification](https://adif.org.uk) (currently 3.1.6) and uses **registered Program IDs** to identify all exports:

- `ADIF-MCP` -- Core engine
- `ADIF-MCP-LOTW` -- LoTW server
- `ADIF-MCP-EQSL` -- eQSL server
- `ADIF-MCP-QRZ` -- QRZ server

The project uses **APP_ fields** for provenance when augmenting records:

- `APP_ADIF-MCP_OP` -- operation performed (`normalize`, `validate`, `merge`)
- `APP_ADIF-MCP-LOTW_ACTION` -- LoTW server operation
- `APP_ADIF-MCP-EQSL_TIME` -- timestamp of eQSL merge

## License

GPL-3.0-or-later. See [LICENSE](LICENSE) for details.
