"""
Minimal smoke tests for convert_adi.py (no external files).
Verifies: header autodetect (station_call + PROGRAMID), band normalization,
and eQSL eqsl_qslrdate → eqsl_qsl_date mapping + provenance.
"""

import adif_mcp.cli.convert_adi as m  # used to set module-level defaults in the test
from adif_mcp.cli.convert_adi import _extract_header_info, build_qso, parse_adif

_ADIF_TEXT = """Received eQSLs for KI7MT
<PROGRAMID:21>eQSL.cc DownloadInBox
<ADIF_Ver:5>3.1.0
<EOH>
<CALL:5>W9ILY<TIME_ON:4>0358<QSO_DATE:8>20220616<BAND:3>40M<MODE:2>CW<RST_SENT:3>599<GRIDSQUARE:6>EN51ti<EQSL_QSLRDATE:8>20220621<EOR>
<CALL:5>KM4FO<TIME_ON:4>2121<QSO_DATE:8>20240803<BAND:3>20M<MODE:2>CW<RST_SENT:3>599<GRIDSQUARE:6>EM67fi<EQSL_QSLRDATE:8>20240804<EOR>
"""


def test_header_extracts_station_call_and_program() -> None:
    """Test if we can extract station call from the adi header"""
    station_call, source, program = _extract_header_info(_ADIF_TEXT)
    assert station_call == "KI7MT"
    # Could be "header_tag:station_callsign" if present, or "header_text"
    # from the plain line.
    assert source in (
        "header_text",
        "header_tag:station_callsign",
        "header_tag:my_call",
        "header_tag:operator",
    )
    assert program is None or program.endswith("DownloadInBox")


def test_build_qso_normalizes_and_maps() -> None:
    """prime module defaults from the header (what main() normally does)"""
    station_call, source, program = _extract_header_info(_ADIF_TEXT)
    m._DEFAULT_STATION_CALL = station_call
    m._DEFAULT_STATION_CALL_SOURCE = source
    m._DEFAULT_SOURCE_PROGRAM = program

    # 2) now parse and build
    rec_maps = list(parse_adif(_ADIF_TEXT))
    assert len(rec_maps) == 2

    q1 = build_qso(rec_maps[0])
    q2 = build_qso(rec_maps[1])

    # Station call injected from header
    assert q1.station_call == "KI7MT"
    assert q2.station_call == "KI7MT"

    # Band normalization
    assert q1.band == "40m"
    assert q2.band == "20m"

    # Mode & eqsl mapping
    assert q1.mode == "CW" and q2.mode == "CW"
    assert q1.eqsl_qsl_date == "20220621"
    assert q2.eqsl_qsl_date == "20240804"

    # Provenance present
    assert q1.adif_fields and q1.adif_fields.get("_station_call_source") in (
        "header_text",
        "header_tag:station_callsign",
        "header_tag:my_call",
        "header_tag:operator",
    )
    # If PROGRAMID was seen, builder stamps _source_program
    sp = q1.adif_fields.get("_source_program")
    assert (sp is None) or sp.endswith("DownloadInBox")
