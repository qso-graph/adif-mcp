# ADIF specification files

`316/` and `317/` hold the ADIF specification exports, versions 3.1.6 and 3.1.7, produced by the
ADIF Developers Group and published at <https://adif.org.uk/>: every file in ADIF's resource zip
except its test material, unmodified. The JSON is at the top of each folder; the other formats are
in `xml/` (with `all.xml` and `adifexport.xsd`), `csv/`, `tsv/`, `xlsx/` and `ods/`, as ADIF names
them. Each folder's `MANIFEST.json` lists the zip and every file's SHA-256, and a test checks the
files stay byte-identical to ADIF's.

**Two versions are kept: the previous and the current.** When ADIF publishes a new version, it is
installed with `scripts/import_adif_release.py` and the oldest folder is removed in the same change.

They are ADIF's work, not ours: adif-mcp's GPL-3.0-or-later licence does not cover them. The
exceptions, which are ours, are each version's `enumerations_country.json` (derived by adif-mcp;
see its `Derived` block), each `MANIFEST.json`, and `adif_catalog.json` / `adif_meta.json` in this folder.

See `NOTICE` at the root of the adif-mcp repository.
