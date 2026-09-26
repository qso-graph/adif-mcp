#!/usr/bin/env python3
"""Generate enumerations_country.json from DXCC Entity Code enumeration.

ADIF's MY_COUNTRY and MY_COUNTRY_INTL fields name an enumeration called
"Country", but the ADIF exports publish no Country table: the country names
are the Entity Name column of DXCC_Entity_Code. This script derives the
Country enumeration from that column. Deleted DXCC entities are marked
Import-only.

The data is ADIF's: every name and code comes from ADIF's published
DXCC_Entity_Code enumeration. Only the file is ours, re-keyed by name so
MY_COUNTRY can be validated. It carries a "Derived" block saying so, and it
must never be merged into the upstream combined files (all.json,
enumerations.json), which stay byte-identical to what ADIF publishes.

Usage: python scripts/generate_country_enum.py 317   (spec directory name)
Output is committed as a static resource.
"""

import json
import os
import sys


def main() -> None:
    """Generate Country enumeration JSON from DXCC entities."""
    if len(sys.argv) != 2:
        sys.exit("usage: generate_country_enum.py <spec-version-dir, e.g. 317>")
    version = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    spec_dir = os.path.join(script_dir, "..", "src", "adif_mcp", "resources", "spec", version)

    dxcc_path = os.path.join(spec_dir, "enumerations_dxcc_entity_code.json")
    with open(dxcc_path, "r", encoding="utf-8") as f:
        dxcc_data = json.load(f)

    dxcc_records = dxcc_data["Adif"]["Enumerations"]["DXCC_Entity_Code"]["Records"]

    country_records: dict[str, dict[str, str]] = {}
    for _key, rec in dxcc_records.items():
        entity_name = rec.get("Entity Name", "")
        entity_code = rec.get("Entity Code", "")

        # Skip entity code 0 ("None")
        if entity_code == "0":
            continue

        country_rec: dict[str, str] = {
            "Enumeration Name": "Country",
            "Country Name": entity_name,
            "DXCC Entity Code": entity_code,
        }

        # Deleted DXCC entities → Import-only (warn, not error)
        if rec.get("Deleted") == "true":
            country_rec["Import-only"] = "true"

        country_records[entity_name] = country_rec

    output = {
        "Adif": {
            "Derived": {
                "By": "adif-mcp",
                "Generator": "scripts/generate_country_enum.py",
                "From": "enumerations_dxcc_entity_code.json, Entity Name",
                "Note": "A view of ADIF's DXCC_Entity_Code Entity Name, re-keyed "
                "by name. The data is ADIF's; ADIF publishes no separate Country "
                "table.",
            },
            "Enumerations": {
                "Country": {
                    "Header": [
                        "Enumeration Name",
                        "Country Name",
                        "DXCC Entity Code",
                        "Import-only",
                    ],
                    "Records": country_records,
                }
            },
        }
    }

    out_path = os.path.join(spec_dir, "enumerations_country.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total = len(country_records)
    deleted = sum(1 for r in country_records.values() if r.get("Import-only") == "true")
    print(f"Generated {out_path}")
    active = total - deleted
    print(f"  Total: {total} countries ({active} active, {deleted} import-only)")


if __name__ == "__main__":
    main()
