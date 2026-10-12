# MCP Overview

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) is an open standard that lets AI agents discover and call tools exposed by external servers. Instead of hardcoding API integrations, agents connect to MCP servers that advertise typed tool contracts -- inputs, outputs, and descriptions -- so the agent can invoke them safely.

## How ADIF-MCP Uses MCP

ADIF-MCP is an MCP server built with [FastMCP](https://github.com/jlowin/fastmcp) that exposes Amateur Radio logging operations as tools. When an AI agent (Claude, ChatGPT, Copilot, Gemini, etc.) connects to ADIF-MCP, it automatically discovers 7 tools for:

- **Validating and parsing** ADIF records against the 3.1.6 specification
- **Searching** the full ADIF spec -- fields, enumerations, data types, subdivisions
- **Computing** Great Circle distance and beam headings between Maidenhead grids
- **Querying** service version and specification metadata

## Architecture

```
AI Agent  <-->  MCP Protocol (stdio)  <-->  adif-mcp server
                                              |
                                              +-- ADIF 3.1.6 spec (30 bundled JSON modules)
                                              +-- Plugin system (LoTW, eQSL, QRZ)
                                              +-- Persona & credential management
```

The server runs locally via `stdio` transport (default) or `streamable-http` for debugging. All ADIF specification data is bundled -- no network calls required for core operations.

## Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Validation | 2 | Parse and validate ADIF records |
| Spec Intelligence | 2 | Search fields, enumerations, subdivisions |
| Geospatial | 2 | Distance and heading between grids |
| System | 1 | Version and metadata |

Plus 1 MCP resource (`adif://system/version`) for agent-discoverable version info.

See the [Tools Reference](tools.md) for the complete tool catalog with input/output examples.

## Transport Modes

ADIF-MCP supports two transport modes:

**stdio (default)** -- The standard transport for MCP clients. The agent launches `adif-mcp` as a subprocess and communicates over stdin/stdout. This is what Claude Desktop, Claude Code, Cursor, and VS Code use.

```bash
adif-mcp           # starts in stdio mode
```

**streamable-http** -- For debugging with [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) or other HTTP-based clients. Starts an HTTP server that accepts MCP requests.

```bash
adif-mcp --transport streamable-http
```

## How a client discovers the tools

A client reads the tool list from the protocol itself, with `tools/list`. Each tool carries its
name, description, `inputSchema`, `outputSchema` and annotations, generated from the Python
signatures and docstrings, so there is nothing to keep in sync by hand.

`server.json` at the repository root is the other half: it is the
[MCP Registry](https://registry.modelcontextprotocol.io) manifest, declaring the package name and
version for discovery. The release pipeline checks it against `pyproject.toml` and refuses to
publish if they disagree.

There used to be a third, hand-maintained `mcp/manifest.json` describing the tools separately. It
was removed in the 2026-10-11 cleanup: the server never read it, and it had drifted to declaring
four tools that no longer existed while the server registered eight. Two declarations of the same
thing is one too many, and the protocol's own is authoritative.

## How FastMCP Works

ADIF-MCP uses [FastMCP](https://github.com/jlowin/fastmcp) as its MCP runtime. FastMCP handles:

- **Tool registration** via `@mcp.tool()` decorators -- each Python function becomes an MCP tool
- **Resource registration** via `@mcp.resource()` -- read-only endpoints agents can discover
- **Schema generation** -- Python type hints are automatically converted to JSON Schema for tool inputs
- **Transport management** -- stdio and HTTP transports are handled transparently

This means adding a new tool is as simple as writing a decorated Python function with type annotations. FastMCP generates the MCP-compliant schema automatically.
