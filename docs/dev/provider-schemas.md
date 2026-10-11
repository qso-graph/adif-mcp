# Provider Schemas & Usage (how the JSON fits together)

This project keeps provider capabilities as data so code stays small and safe. Three pieces matter:

- Provider schemas — the minimal field sets we rely on per service
src/adif_mcp/resources/providers/*.json
- Usage map — which tools/features consume which fields
src/adif_mcp/resources/mapping/usage.json
- Loader helpers — a tiny API to read those files at runtime
adif_mcp.resources module

## Why Schemas as JSON?
- Keep network code narrow: only fetch what we need.
- Make it easy to add/adjust providers without touching Python.
- Enable docs/tests to reason about support (e.g., “QSO lacks RST fields”).

Example: resources/providers/eqsl.json
```json
{
  "name": "eQSL",
  "fields": [
    "station_call",
    "call",
    "qso_date",
    "time_on",
    "band",
    "mode",
    "rst_sent",
    "rst_rcvd",
    "gridsquare",
    "my_gridsquare",
    "freq"
  ]
}
```

## Conventions
- name: display label used in docs/UI.
- fields: the normalized ADIF-ish keys our parser/normalizer expects.

Other providers are similar (LoTW, QRZ). QRZ currently omits RST fields intentionally.

## Usage map (what consumes what)

resources/mapping/usage.json binds features/tools to fields so both docs and code can ask, “Do we have enough data to answer this?” For example (simplified):
```json
{
  "tools": {
    "eqsl.fetch_inbox": ["call", "qso_date", "time_on", "band", "mode", "freq", "eqsl_qsl_rcvd", "eqsl_qslrdate"],
    "eqsl.filter_summary": ["band", "mode", "qso_date"]
  }
}
```

This lets CI or a future “capabilities” command flag gaps early.

## Examples

List what we ship:

```bash
uv run python -c "from adif_mcp.resources import list_providers; print(list_providers())"
```

Check fields for a provider:
```
uv run python - <<'PY'
from adif_mcp.resources import load_provider
print(load_provider("eqsl")["fields"])
PY
```

Confirm a tool’s needs are covered by a provider:
```bash
uv run python - <<'PY'
from adif_mcp.resources import load_provider, get_usage_map
prov = load_provider("qrz")
need = set(get_usage_map()["tools"]["eqsl.filter_summary"])
have = set(prov["fields"])
missing = need - have
print("Missing:", sorted(missing))
PY
```

## Adding a new provider (checklist)

1. Create src/adif_mcp/resources/providers/<name>.json with name + fields.
2. If any tools rely on it, update resources/mapping/usage.json.
3. Add a probe adapter (read-only GET) under src/adif_mcp/providers/adapters.py.
4. Ensure redaction/masking rules apply to any auth materials.
5. Tests:
- Unit: load_provider("<name>") returns fields.
- Optional: “wire” probe behind a local env flag (no CI network).

## CI & Packaging notes
- Resources are included via tool.hatch.build.targets.wheel.packages & tool.hatch.build.include.
- validate-manifest (CLI) uses the packaged manifest by default; keep it under src/adif_mcp/mcp/manifest.json.
- A simple resource smoke test exists in tests/test_resources.py.

## Future extensions (nice to have)
- adif_mcp.resources.capabilities(provider) → synthesize what queries are answerable.
- Versioned provider files (e.g., providers/eqsl@2025-09.json + alias) when APIs change.
- A CLI command adif-mcp providers show <name> to dump fields & sample coverage
