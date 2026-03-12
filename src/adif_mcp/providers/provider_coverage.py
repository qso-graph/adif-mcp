# scripts/provider_coverage.py
"""
Compute per-provider coverage of ADIF fields.

Reads canonical ADIF fields (catalog) and compares against each provider’s
declared fields, producing a compact table with coverage % and missing fields.

Order of precedence for paths:
    1) CLI flags (--catalog, --providers)
    2) pyproject.toml [tool.adif] block
    3) Hard-coded repo defaults

Usage (from repo root):
    uv run python src/adif_mcp/providers/provider_coverage.py
    uv run python src/adif_mcp/providers/provider_coverage.py
        --catalog mcp/spec/adif_catalog.json
        --providers mcp/providers
"""

from __future__ import annotations

import argparse
import json
import os
import textwrap
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import Any

# ---- Repo defaults (used only if pyproject.toml doesn’t provide them) --------

DEFAULT_TITLE = "Provider Coverage Report"
DEFAULT_DESCRIPTION = "Compute per-provider ADIF field coverage."

DEFAULT_CATALOG = Path("mcp/spec/adif_catalog.json")
DEFAULT_PROVIDERS_DIR = Path("mcp/providers")


# ---- Utilities ---------------------------------------------------------------


def _read_json(p: Path) -> Any:
    """Read JSON file *p* and return the parsed object."""
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_adif_paths_from_pyproject(
    pyproject: Path = Path("pyproject.toml"),
) -> tuple[Path, Path]:
    """
    Try to read catalog/providers paths from pyproject.toml [tool.adif].

    Returns:
        (catalog_path, providers_dir)
    """
    if not pyproject.exists():
        return DEFAULT_CATALOG, DEFAULT_PROVIDERS_DIR

    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    tool = data.get("tool", {})
    adif = tool.get("adif", {}) or {}

    # spec.adif_catalog under [tool.adif]
    catalog_cfg = (adif.get("spec") or {}).get("adif_catalog")
    catalog = Path(catalog_cfg) if catalog_cfg else DEFAULT_CATALOG

    providers_cfg = adif.get("providers_dir")
    providers = Path(providers_cfg) if providers_cfg else DEFAULT_PROVIDERS_DIR

    return catalog, providers


# ---- Loaders -----------------------------------------------------------------


def load_catalog_fields(catalog_path: Path) -> set[str]:
    """
    Extract canonical ADIF field names from a catalog JSON.

    Accepted shapes:
      - {"fields": [{"name": "CALL"}, ...]}
      - {"fields": ["CALL", "QSO_DATE", ...]}
      - ["CALL", "QSO_DATE", ...]
    """
    data = _read_json(catalog_path)

    if isinstance(data, list):
        return {str(x).strip() for x in data}

    fields = data.get("fields", [])
    names: set[str] = set()
    for item in fields:
        if isinstance(item, dict) and "name" in item:
            names.add(str(item["name"]).strip())
        else:
            names.add(str(item).strip())
    return names


def load_provider_file(p: Path) -> tuple[str, set[str]]:
    """
    Extract provider name and implemented fields from a provider JSON.

    Accepted shapes:
      - {"provider": "LoTW", "fields": ["CALL", ...]}
      - {"name": "LoTW", "fields": ["CALL", ...]}
    """
    data = _read_json(p)
    name = str(data.get("provider") or data.get("name") or p.stem)
    raw_fields: Iterable[object] = data.get("fields", [])
    impl = {str(x).strip() for x in raw_fields}
    return name, impl


def scan_providers(providers_dir: Path) -> list[tuple[str, set[str]]]:
    """Load all provider JSON files in *providers_dir*, skipping usage.json."""
    out: list[tuple[str, set[str]]] = []
    for jf in sorted(providers_dir.glob("*.json")):
        if jf.name.lower() == "usage.json":
            continue
        out.append(load_provider_file(jf))
    return out


def pct(n: int, d: int) -> float:
    """Percentage helper."""
    return 0.0 if d == 0 else (100.0 * n / d)


# ---- Presentation ------------------------------------------------------------


def render_report(catalog_fields: list[str], rows: list[tuple[str, set[str]]]) -> None:
    """Pretty-print provider coverage with a Status column (missing fields inline)."""
    total = len(catalog_fields)

    printable: list[tuple[str, int, int, float, str]] = []
    for provider, fields in rows:
        covered = len(fields & set(catalog_fields))
        missing_set = sorted(set(catalog_fields) - fields)
        missing = len(missing_set)
        pct_val = 0.0 if total == 0 else round((covered / total) * 100, 1)
        status = f"missing: {', '.join(missing_set) if missing_set else '—'}"
        printable.append((provider, covered, missing, pct_val, status))

    name_w = max(8, max(len(p[0]) for p in printable)) if printable else 12
    cov_w = 8
    mis_w = 8
    pct_w = 6
    status_w = 72  # shorten long lists

    header = f"{'Provider':<{name_w}} {'Cov':>{cov_w}} {'Miss':>{mis_w}} {'%':>{pct_w}} Status"

    sep = "-" * (name_w + cov_w + mis_w + pct_w + 8 + status_w)
    print(header)
    print(sep)

    for provider, covered, missing, pct_val, status in printable:
        short = textwrap.shorten(status, width=status_w, placeholder="…")
        line = (
            f"{provider:<{name_w}}  "
            f"{covered:>{cov_w}}  "
            f"{missing:>{mis_w}}  "
            f"{pct_val:>{pct_w}}  "
            f"{short}"
        )
        print(line)


def clear() -> None:
    """Clear the terminal for readability."""
    os.system("cls" if os.name == "nt" else "clear")


# ---- CLI ---------------------------------------------------------------------


def main() -> int:
    """CLI entry point: resolve paths, gather data, and print the report."""
    ap = argparse.ArgumentParser(description="Compute per-provider ADIF coverage.")
    ap.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Path to ADIF catalog JSON (overrides pyproject/ default)",
    )
    ap.add_argument(
        "--providers",
        type=Path,
        default=None,
        help="Directory of provider JSON files (overrides pyproject/ default)",
    )
    args = ap.parse_args()

    # Resolve from pyproject first, then allow CLI overrides
    catalog_from_py, providers_from_py = _load_adif_paths_from_pyproject()
    catalog_path = args.catalog or catalog_from_py
    providers_dir = args.providers or providers_from_py

    catalog_fields_set = load_catalog_fields(catalog_path)
    providers = scan_providers(providers_dir)

    clear()
    print(f"{DEFAULT_TITLE} - {DEFAULT_DESCRIPTION}")
    print()
    print(f"Catalog Fields .......: {len(catalog_fields_set)}")
    print(f"Catalog Directory ....: {catalog_path}")
    print(f"Providers Directory ..: {providers_dir}")
    print()

    render_report(list(catalog_fields_set), providers)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
