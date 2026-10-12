"""ADIF-DT: the structured data types, checked as ADIF 3.1.7 defines them (#47).

Errors for what the specification states; warnings, never errors, for what its
grammar allows but cannot be right. Case never fails a type ADIF calls
case-insensitive.
"""

from __future__ import annotations

import pytest
from fastmcp.exceptions import ToolError

from adif_mcp.mcp import server


def _record(field: str, value: str) -> str:
    return f"<CALL:4>W1AW<{field}:{len(value)}>{value}<EOR>"


def _check(field: str, value: str) -> dict:
    return server.validate_adif_record(_record(field, value))


class TestTheIssueValues:
    """ADIF-DT01: every value #47 reported as passing now gets its answer."""

    @pytest.mark.parametrize(
        "field,value",
        [
            ("MY_GRIDSQUARE", "ZZ"),  # field letters run A-R
            ("MY_LAT", "43.5"),  # decimal degrees, not XDDD MM.MMM
            ("MY_LON", "garbage"),
            ("MY_LON", "W117 70.000"),  # minutes above 59.999
        ],
    )
    def test_a_value_the_grammar_forbids_is_an_error(self, field: str, value: str) -> None:
        answer = _check(field, value)
        assert answer["status"] == "invalid", answer
        assert any(field in error for error in answer["errors"])

    def test_an_unreachable_latitude_is_a_warning_not_an_error(self) -> None:
        """N100 00.000 satisfies the type's 0-180, which serves latitude and
        longitude alike; so it is reported, never rejected."""
        answer = _check("MY_LAT", "N100 00.000")
        assert answer["status"] == "success"
        assert any("not on the Earth" in warning for warning in answer["warnings"])


class TestGridSquare:
    """ADIF-DT02: GridSquare, GridSquareExt and GridSquareList."""

    @pytest.mark.parametrize(
        "value", ["DN", "DN13", "DN13LA", "DN13la", "dn13la", "Dn13La", "DN13LA45"]
    )
    def test_valid_locators_pass_in_any_case(self, value: str) -> None:
        answer = _check("GRIDSQUARE", value)
        assert answer["status"] == "success", answer
        assert not answer["errors"]

    @pytest.mark.parametrize("value", ["D", "DN1", "SS13", "DN13YA", "DN13LA4", "DN13LA45AB"])
    def test_invalid_locators_fail(self, value: str) -> None:
        assert _check("GRIDSQUARE", value)["status"] == "invalid"

    @pytest.mark.parametrize("value", ["AB", "ab", "AB12"])
    def test_extension_valid(self, value: str) -> None:
        assert _check("GRIDSQUARE_EXT", value)["status"] == "success"

    @pytest.mark.parametrize("value", ["A", "ZZ", "AB1", "12"])
    def test_extension_invalid(self, value: str) -> None:
        assert _check("GRIDSQUARE_EXT", value)["status"] == "invalid"

    def test_vucc_grids_two_or_four_of_four_or_six(self) -> None:
        assert _check("VUCC_GRIDS", "EM98,FM08,EM97,FM07")["status"] == "success"
        assert _check("VUCC_GRIDS", "EM98,FM08")["status"] == "success"
        assert _check("VUCC_GRIDS", "EM98,FM08,EM97")["status"] == "invalid"
        assert _check("VUCC_GRIDS", "EM,FM")["status"] == "invalid"
        assert _check("VUCC_GRIDS", "EM98,ZZ08")["status"] == "invalid"


class TestLocation:
    """ADIF-DT03: XDDD MM.MMM."""

    @pytest.mark.parametrize(
        "field,value", [("LAT", "N043 30.000"), ("LON", "W117 59.999"), ("LON", "e000 00.000")]
    )
    def test_valid(self, field: str, value: str) -> None:
        answer = _check(field, value)
        assert answer["status"] == "success", answer
        assert not answer["warnings"]

    @pytest.mark.parametrize(
        "value",
        [
            "N43 30.000",
            "N043 30.00",
            "N043 30.0000",
            "N04330.000",
            "X043 30.000",
            "N181 00.000",
        ],
    )
    def test_invalid(self, value: str) -> None:
        assert _check("LON", value)["status"] == "invalid"

    def test_a_hemisphere_letter_on_the_wrong_axis_is_a_warning(self) -> None:
        """A wrong-axis letter puts a station somewhere plausible and wrong, so it
        is reported; the type itself does not forbid it."""
        lat = _check("LAT", "E043 30.000")
        lon = _check("LON", "N117 00.000")
        assert lat["status"] == lon["status"] == "success"
        assert lat["warnings"] and lon["warnings"]


class TestBooleanAndReferences:
    """ADIF-DT04: Boolean, IOTARefNo, WWFFRef, POTARefList, SOTARef."""

    @pytest.mark.parametrize(
        "value,ok",
        [("Y", True), ("y", True), ("N", True), ("n", True), ("yes", False), ("1", False)],
    )
    def test_boolean(self, value: str, ok: bool) -> None:
        assert (_check("SWL", value)["status"] == "success") is ok

    @pytest.mark.parametrize(
        "value,ok",
        [
            ("NA-001", True),
            ("eu-005", True),
            ("XX-001", False),
            ("NA-000", False),
            ("NA-1", False),
        ],
    )
    def test_iota(self, value: str, ok: bool) -> None:
        assert (_check("IOTA", value)["status"] == "success") is ok

    @pytest.mark.parametrize(
        "value,ok",
        [
            ("KFF-4655", True),
            ("3DAFF-0002", True),
            ("kff-4655", True),
            ("KFF-46", False),
            ("K-4655", False),
        ],
    )
    def test_wwff(self, value: str, ok: bool) -> None:
        assert (_check("WWFF_REF", value)["status"] == "success") is ok

    @pytest.mark.parametrize(
        "value,ok",
        [
            ("K-0059", True),
            ("K-10000", True),
            ("K-0059,K-1234", True),
            ("K-0059@US-CA", True),
            ("K0059", False),
            ("K-59", False),
        ],
    )
    def test_pota(self, value: str, ok: bool) -> None:
        assert (_check("POTA_REF", value)["status"] == "success") is ok

    @pytest.mark.parametrize(
        "value,ok",
        [("W2/WE-003", True), ("G/LD-003", True), ("W2WE-003", False), ("/WE-003", False)],
    )
    def test_sota(self, value: str, ok: bool) -> None:
        assert (_check("SOTA_REF", value)["status"] == "success") is ok


class TestLocatorTools:
    """ADIF-DT05: the distance and heading tools refuse what is not a locator (#48).

    'ZZ99' used to decode to a point off the Earth and return a number."""

    @pytest.mark.parametrize("bad", ["ZZ99", "DN", "12AB", ""])
    def test_bad_locators_are_tool_errors(self, bad: str) -> None:
        with pytest.raises(ToolError):
            server.calculate_distance(bad, "JN48")
        with pytest.raises(ToolError):
            server.calculate_heading("DN13", bad)

    def test_lower_case_locators_work(self) -> None:
        assert server.calculate_distance("dn13", "jn48") == server.calculate_distance(
            "DN13", "JN48"
        )


class TestParseAdifErrors:
    """ADIF-DT06: a file that is not there is a tool error, not an answer (#48)."""

    def test_a_missing_file_raises(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        import asyncio

        with pytest.raises(ToolError):
            asyncio.run(server.parse_adif(str(tmp_path / "missing.adi")))

    def test_a_real_file_still_parses(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        import asyncio

        log = tmp_path / "log.adi"
        log.write_text("<EOH>\n<CALL:4>W1AW<EOR>\n<CALL:4>K1JT<EOR>\n")
        out = asyncio.run(server.parse_adif(str(log)))
        assert "TOTAL RECORDS: 2" in out[0].text
