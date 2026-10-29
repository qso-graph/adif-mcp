"""adif-mcp reads ADIF with qso_graph_lib.adif; what its own scanning got wrong."""

from __future__ import annotations

import asyncio
from pathlib import Path

from adif_mcp.mcp import server


def spec(name: str, value: str) -> str:
    """A Data-Specifier with its length counted, not typed by hand."""
    return f"<{name}:{len(value)}>{value}"


def test_a_tag_inside_a_value_does_not_replace_the_field_being_validated():
    report = server.validate_adif_record(
        spec("CALL", "W1AW") + spec("COMMENT", "see <CALL:2>X1") + "<EOR>")
    assert report["record"]["CALL"] == "W1AW"
    assert report["record"]["COMMENT"] == "see <CALL:2>X1"


def test_a_literal_eor_in_a_value_is_not_a_second_record(tmp_path: Path):
    record = spec("CALL", "W1AW") + spec("COMMENT", "a<eor>b") + "<EOR>"
    log = tmp_path / "log.adi"
    log.write_text("Header\n" + spec("ADIF_VER", "3.1.7") + "<EOH>\n" + record + "\n")
    out = asyncio.run(server.parse_adif(str(log)))[0].text
    assert "TOTAL RECORDS: 1" in out
    assert "--- RECORD 1 ---\n" + record + "\n" in out  # and no Header in it


def test_a_crlf_multiline_field_keeps_its_length(tmp_path: Path):
    log = tmp_path / "log.adi"
    text = (spec("CALL", "W1AW") + spec("NOTES", "one\r\ntwo") + spec("BAND", "20M")
            + "<EOR>\r\n")
    log.write_bytes(text.encode())
    out = asyncio.run(server.parse_adif(str(log)))[0].text
    assert "TOTAL RECORDS: 1" in out and "ADIF PROBLEMS" not in out
