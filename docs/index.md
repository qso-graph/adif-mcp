# ADIF MCP

**ADIF-MCP** gives AI agents safe, typed access to Amateur Radio logging data using the ADIF 3.1.6 specification.

[![ADIF 3.1.6](https://img.shields.io/badge/ADIF-3.1.6-blue?label=Spec)](https://adif-mcp.com/spec/spec/)
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/adif-mcp)](https://github.com/KI7MT/adif-mcp/releases)
[![PyPI](https://img.shields.io/pypi/v/adif-mcp)](https://pypi.org/project/adif-mcp/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://github.com/KI7MT/adif-mcp/blob/main/LICENSE)

## Install

```bash
pip install adif-mcp
```

## What It Does

ADIF-MCP is a [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes 7 tools for working with ADIF data. Connect it to Claude, ChatGPT, Copilot, Cursor, Gemini, or any MCP-compatible agent and ask questions in plain language:

- **Validate** ADIF records against the full 3.1.6 specification
- **Parse** large ADIF log files with streaming pagination
- **Search** the complete spec -- fields, enumerations, data types, subdivisions
- **Compute** Great Circle distance and beam headings between Maidenhead grids

## Key Features

- **Spec-compliant** -- full ADIF 3.1.6 bundled as structured JSON (30 modules)
- **Sovereign** -- runs entirely on your machine, no cloud dependencies
- **Extensible** -- plugin framework for LoTW, eQSL, and QRZ
- **Secure** -- credentials stored in your system keyring, never logged

## Project Ethos

ADIF-MCP is a community-driven effort. It does not replace or compete with existing ADIF libraries, logging applications, or services. Instead, it provides a common foundation that others can build upon:

- **Interoperability** -- schema-driven, spec-compliant core for tools and services to talk to each other
- **Extensibility** -- plugin and integration framework for LoTW, eQSL, QRZ, and future platforms
- **Collaboration** -- designed to complement, not fragment, the ADIF tools hams already use
- **Future-facing** -- safe, typed access to ADIF data for AI agents and modern workflows

## Quick Links

| | |
|---|---|
| [Quick Start](getting-started.md) | Install and configure in 5 minutes |
| [Tools Reference](mcp/tools.md) | All 7 tools with input/output examples |
| [MCP Architecture](mcp/overview.md) | How it works under the hood |
| [ADIF 3.1.6 Spec](spec/spec.md) | Specification coverage and details |
