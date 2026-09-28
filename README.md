<!-- mcp-name: io.github.qso-graph/adif-mcp -->
# adif-mcp

[![PyPI](https://img.shields.io/pypi/v/adif-mcp?label=PyPI&color=blue)](https://pypi.org/project/adif-mcp/)
[![MCP Registry](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fregistry.modelcontextprotocol.io%2Fv0%2Fservers%3Fsearch%3Dadif-mcp&query=%24.servers%5B0%5D.server.version&label=MCP%20Registry&color=blue)](https://registry.modelcontextprotocol.io/v0/servers?search=adif-mcp)

MCP server for the [ADIF 3.1.7 specification](https://adif.org.uk/317/ADIF_317.htm): validate and parse ADIF records, search the spec's fields, enumerations and data types, and compute distance and heading between Maidenhead locators, through any MCP-compatible AI assistant.

Part of the [qso-graph](https://qso-graph.io/) project. **No authentication required** — the ADIF specification is bundled, so it works offline.

## Install

```bash
pip install adif-mcp
```

## Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `validate_adif_record` | Validate a raw ADIF record against the 3.1.7 spec | adif_string |
| `parse_adif` | Streaming parser for large ADIF files, with pagination | file_path, start_at, limit |
| `read_specification_resource` | Raw JSON for any spec module (band, mode, fields, ...) | resource_name |
| `list_enumerations` | All ADIF enumerations with entry counts | — |
| `search_enumerations` | Search enumeration records by keyword | search_term, enumeration |
| `calculate_distance` | Great-circle distance (km) between two Maidenhead locators | start, end |
| `calculate_heading` | Initial beam heading (azimuth) between two locators | start, end |
| `get_version_info` | Service version + upstream spec version (fleet identity attestation) | — |

## What is ADIF?

ADIF (Amateur Data Interchange Format) is the standard file format amateur radio logging programs use to exchange QSO records. adif-mcp is the specification package of qso-graph: it validates, parses and searches ADIF so an assistant can work with logs safely and accurately. Credentials are handled separately by [qso-graph-auth](https://pypi.org/project/qso-graph-auth/), and each logging service has its own MCP server (see [qso-graph.io](https://qso-graph.io/)).

## Quick Start

No credentials needed — just install and configure your MCP client.

### Configure your MCP client

adif-mcp works with any MCP-compatible client. Add the server config and restart. The tools appear automatically.

#### Claude Desktop

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

#### Claude Code

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

#### ChatGPT Desktop

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

#### Cursor

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

#### VS Code / GitHub Copilot

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

#### Gemini CLI

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

### Ask questions

> "Is this ADIF record valid? <CALL:5>KI7MT<QSO_DATE:8>20260928<BAND:3>20m<MODE:3>SSB<EOR>"

> "What values does the ADIF MODE enumeration allow for digital modes?"

> "Parse my log file and show me the first 50 QSOs."

> "How far is it from DN13 to JN48, and what heading should I point the beam?"

## Compliance & Provenance

adif-mcp follows the [ADIF Specification](https://adif.org.uk) (currently 3.1.7) and uses **registered Program IDs** to identify all exports:

- `ADIF-MCP` -- Core engine
- `ADIF-MCP-LOTW` -- LoTW server
- `ADIF-MCP-EQSL` -- eQSL server
- `ADIF-MCP-QRZ` -- QRZ server

The project uses **APP_ fields** for provenance when augmenting records:

- `APP_ADIF-MCP_OP` -- operation performed (`normalize`, `validate`, `merge`)
- `APP_ADIF-MCP-LOTW_ACTION` -- LoTW server operation
- `APP_ADIF-MCP-EQSL_TIME` -- timestamp of eQSL merge

## Development

```bash
git clone https://github.com/qso-graph/adif-mcp.git
cd adif-mcp
pip install -e ".[test]"
pytest
```

## License

GPL-3.0-or-later. See [LICENSE](LICENSE) for details.
