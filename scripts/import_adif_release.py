#!/usr/bin/env python3
"""Install one ADIF version's published files into the package (#28).

Usage:
    python scripts/import_adif_release.py VERSION ZIP_URL ZIP_SHA256

    e.g. python scripts/import_adif_release.py 317 \
        https://adif.org.uk/317/ADIF_317_resources_2026_03_22.zip <sha256>

adif-mcp ships ADIF **as published**: every file in ADIF's resource zip except the test
material (`tests/`), unmodified. The zip is downloaded, checked against ZIP_SHA256, and
its `exports/` are written to `src/adif_mcp/resources/spec/VERSION/`:

- `exports/json/*.json` at the top of that folder (where the tools read them);
- every other format in a subfolder named as ADIF names it: `xml/` (with `all.xml` and
  `adifexport.xsd`), `csv/`, `tsv/`, `xlsx/`, `ods/`.

It writes `MANIFEST.json` beside them (the zip's URL and SHA-256, and every file's
SHA-256) and the same pins to `test/data/adif_upstream_sha256.json`, which the tests
check the packaged files against.

**Two versions are shipped: the previous and the current** (KI7MT, 2026-10-06), so the
package doesn't grow with every ADIF release. Importing a new version means removing the
oldest one's folder and pin in the same change.

The derived `enumerations_country.json` is adif-mcp's own and is left alone.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "src" / "adif_mcp" / "resources" / "spec"
PINS = ROOT / "test" / "data" / "adif_upstream_sha256.json"
OURS = {"enumerations_country.json"}  # derived by adif-mcp, never from the zip


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def target(member: str, version: str) -> str | None:
    """Where a zip member goes, relative to spec/VERSION/; None to skip it."""
    prefix = f"{version}/exports/"
    if not member.startswith(prefix) or member.endswith("/"):
        return None  # tests/ and anything outside exports/ are not shipped
    fmt, _, name = member[len(prefix):].partition("/")
    if not name or "/" in name:
        return None
    return name if fmt == "json" else f"{fmt}/{name}"


def main(version: str, url: str, zip_sha: str) -> None:
    with urllib.request.urlopen(url, timeout=120) as r:  # https, adif.org.uk
        blob = r.read()
    got = sha256(blob)
    if got != zip_sha:
        sys.exit(f"zip SHA-256 mismatch: expected {zip_sha}, got {got}")

    out = SPEC / version
    out.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            rel = target(info.filename, version)
            if rel is None:
                continue
            data = z.read(info)
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            files[rel] = sha256(data)

    manifest = {
        "_about": "ADIF's published files for this version, unmodified, with their SHA-256. "
                  "From the resource zip below; tests/ is not shipped. "
                  "enumerations_country.json is adif-mcp's own (derived) and not listed.",
        "adif_version": f"{version[0]}.{version[1]}.{version[2:]}",
        "source": url,
        "zip_sha256": zip_sha,
        "files": dict(sorted(files.items())),
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    pins = json.loads(PINS.read_text(encoding="utf-8"))
    pins["versions"][version] = {
        "source": url, "zip_sha256": zip_sha, "files": manifest["files"],
    }
    pins["versions"] = dict(sorted(pins["versions"].items()))
    PINS.write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
    print(f"{version}: {len(files)} files, zip {zip_sha[:12]}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
