"""Tests for enumeration listing, searching, and validation (v0.7.0)."""

import os
import re

from adif_mcp.mcp.server import (
    list_enumerations,
    search_enumerations,
    validate_adif_record,
)

_TEST_DATA = os.path.join(os.path.dirname(__file__), "data")

# --- list_enumerations ---


def test_list_enumerations_count() -> None:
    """Returns exactly 26 enumerations (25 spec + Country derived)."""
    result = list_enumerations()
    assert result["enumeration_count"] == 26
    assert len(result["enumerations"]) == 26


def test_list_enumerations_has_mode() -> None:
    """Mode enumeration present with correct record count.

    ADIF 3.1.7 adds OFDM (Orthogonal Frequency-Division Multiplexing),
    bringing the Mode count from 90 (3.1.6) to 91. OFDM is not
    Import-only, so the import_only_count stays at 42.
    """
    result = list_enumerations()
    mode = result["enumerations"]["Mode"]
    assert mode["record_count"] == 91
    assert mode["import_only_count"] == 42
    assert "Mode" in mode["searchable_fields"]


def test_list_enumerations_has_band() -> None:
    """Band enumeration present with 33 records."""
    result = list_enumerations()
    band = result["enumerations"]["Band"]
    assert band["record_count"] == 33
    assert band["import_only_count"] == 0


# --- search_enumerations ---


def test_search_mode_ft8() -> None:
    """Find FT8 in Mode enumeration."""
    result = search_enumerations("FT8", enumeration="Mode")
    assert "results" in result
    mode_results = result["results"]["Mode"]
    assert mode_results["match_count"] >= 1
    found_modes = [
        rec.get("Mode") for rec in mode_results["records"].values()
    ]
    assert "FT8" in found_modes


def test_search_band_20m() -> None:
    """Find 20m in Band enumeration."""
    result = search_enumerations("20m", enumeration="Band")
    assert "results" in result
    band_results = result["results"]["Band"]
    found_bands = [
        rec.get("Band") for rec in band_results["records"].values()
    ]
    assert "20m" in found_bands


def test_search_dxcc_entity() -> None:
    """Find United States in DXCC_Entity_Code."""
    result = search_enumerations(
        "United States", enumeration="DXCC_Entity_Code"
    )
    assert "results" in result
    assert "DXCC_Entity_Code" in result["results"]


def test_search_contest_cq_ww() -> None:
    """Find CQ-WW in Contest_ID."""
    result = search_enumerations("CQ-WW", enumeration="Contest_ID")
    assert "results" in result
    assert result["results"]["Contest_ID"]["match_count"] >= 1


def test_search_all_enums() -> None:
    """Search without filter hits multiple enumerations."""
    result = search_enumerations("CW")
    assert "results" in result
    # CW appears in Mode and possibly Submode
    assert result["enumerations_matched"] >= 1


def test_search_specific_enum() -> None:
    """Search with filter returns only that enumeration."""
    result = search_enumerations("CW", enumeration="Mode")
    assert "results" in result
    assert list(result["results"].keys()) == ["Mode"]


def test_search_case_insensitive() -> None:
    """Lowercase 'ft8' finds FT8."""
    result = search_enumerations("ft8", enumeration="Mode")
    assert "results" in result
    found_modes = [
        rec.get("Mode")
        for rec in result["results"]["Mode"]["records"].values()
    ]
    assert "FT8" in found_modes


def test_search_not_found() -> None:
    """Returns not-found message for nonexistent term."""
    result = search_enumerations("ZZZZNOTREAL")
    assert "message" in result
    assert "not found" in result["message"]


def test_search_invalid_enum() -> None:
    """Returns error for invalid enumeration name."""
    result = search_enumerations("CW", enumeration="FakeEnum")
    assert "error" in result
    assert "Unknown enumeration" in result["error"]


# --- validate_adif_record (enumeration validation) ---


def test_validate_valid_mode() -> None:
    """MODE=CW passes validation."""
    adif = "<MODE:2>CW<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_invalid_mode() -> None:
    """MODE=INVALID produces an error."""
    adif = "<MODE:7>INVALID<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("MODE" in e and "INVALID" in e for e in result["errors"])


def test_validate_valid_band() -> None:
    """BAND=20m passes validation."""
    adif = "<BAND:3>20m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_invalid_band() -> None:
    """BAND=25m produces an error."""
    adif = "<BAND:3>25m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("BAND" in e and "25m" in e for e in result["errors"])


def test_validate_import_only_warns() -> None:
    """Import-only MODE value produces warning, not error."""
    # AMTORFEC is import-only in the Mode enumeration
    adif = "<MODE:8>AMTORFEC<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert any("import-only" in w for w in result["warnings"])
    assert not result["errors"]


def test_validate_compound_credit() -> None:
    """CREDIT_SUBMITTED with valid Credit:Medium value passes."""
    # DXCC:CARD is a valid Credit:QSL_Medium pair
    adif = "<CREDIT_SUBMITTED:9>DXCC:CARD<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_compound_credit_plain() -> None:
    """CREDIT_SUBMITTED with plain credit name (no medium) passes."""
    adif = "<CREDIT_SUBMITTED:4>DXCC<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_compound_bad() -> None:
    """CREDIT_SUBMITTED with invalid credit name errors."""
    adif = "<CREDIT_SUBMITTED:9>FAKE:CARD<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("CREDIT_SUBMITTED" in e for e in result["errors"])


def test_validate_submode_match() -> None:
    """SUBMODE=USB with MODE=SSB passes without warning."""
    adif = "<MODE:3>SSB<SUBMODE:3>USB<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
    # No submode mismatch warning
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns


def test_validate_submode_mismatch() -> None:
    """SUBMODE=USB with MODE=CW produces warning."""
    adif = "<MODE:2>CW<SUBMODE:3>USB<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"  # warning, not error
    assert any("submode" in w.lower() and "USB" in w for w in result["warnings"])


def test_validate_dxcc_valid() -> None:
    """DXCC=291 (United States) passes."""
    adif = "<DXCC:3>291<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_continent() -> None:
    """CONT=NA passes."""
    adif = "<CONT:2>NA<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_case_insensitive() -> None:
    """MODE=cw (lowercase) passes validation."""
    adif = "<MODE:2>cw<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_validate_number_unchanged() -> None:
    """Existing Number validation still works."""
    adif = "<AGE:3>abc<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("AGE" in e and "Number" in e for e in result["errors"])


def test_validate_empty_mode_errors() -> None:
    """Empty MODE value produces an error (Patton finding #2)."""
    adif = "<MODE:0><EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("MODE" in e and "empty" in e for e in result["errors"])


def test_validate_whitespace_band_errors() -> None:
    """Whitespace-only BAND value produces an error (Patton finding #2)."""
    adif = "<BAND:1> <EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("BAND" in e and "empty" in e for e in result["errors"])


# --- Official ADIF 3.1.7 Test File (G3ZOD / adif.org.uk) ---


def test_official_adif_test_file_zero_errors() -> None:
    """ADIF-TCR-001: Zero false errors on official 3.1.7 test corpus.

    Source: https://adif.org.uk/317/resources
    Generator: CreateADIFTestFiles (G3ZOD)
    Records: 6,197 QSOs exercising every enumeration value (3.1.7 adds
    +6 over 3.1.6: covers OFDM mode + FT2, FREEDATA, RIBBIT_PIX,
    RIBBIT_SMS submodes).
    Gate: If our validator rejects an official record, our validator is wrong.
    """
    test_file = os.path.join(
        _TEST_DATA, "ADIF_317_test_QSOs_2026_03_22.adi"
    )
    if not os.path.exists(test_file):
        return  # Skip if test file not present (CI without data)

    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r"<EOH>", content, flags=re.IGNORECASE)
    body = parts[1]
    records = re.findall(r"(.*?<EOR>)", body, re.IGNORECASE | re.DOTALL)

    assert len(records) == 6197, f"Expected 6197 records, got {len(records)}"

    all_errors = []
    for i, rec_text in enumerate(records):
        result = validate_adif_record(rec_text.strip())
        for err in result.get("errors", []):
            all_errors.append(f"Record {i + 1}: {err}")

    assert len(all_errors) == 0, (
        f"{len(all_errors)} false errors on official test file:\n"
        + "\n".join(all_errors[:20])
    )


def test_official_adif_test_file_warning_categories() -> None:
    """ADIF-TCR-002: Warnings on official test file are all legitimate.

    Expected warning categories:
    - user/app-defined fields (USERDEF, APP_ prefixed) — not in fields spec
    - import-only values — valid but obsolete enum values
    Both are correct validator behavior, not false positives.
    """
    test_file = os.path.join(
        _TEST_DATA, "ADIF_316_test_QSOs_2025_08_27.adi"
    )
    if not os.path.exists(test_file):
        return

    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r"<EOH>", content, flags=re.IGNORECASE)
    body = parts[1]
    records = re.findall(r"(.*?<EOR>)", body, re.IGNORECASE | re.DOTALL)

    total_warnings = 0
    for rec_text in records:
        result = validate_adif_record(rec_text.strip())
        for w in result.get("warnings", []):
            total_warnings += 1
            # Every warning must be one of these legitimate categories
            assert (
                "not in spec" in w
                or "import-only" in w
                or "submode" in w.lower()
            ), f"Unexpected warning type: {w}"

    # Expect ~39 warnings (23 user-defined + 16 import-only)
    assert 30 <= total_warnings <= 50, (
        f"Expected ~39 warnings, got {total_warnings}"
    )


# --- Country validation (v0.9.0) ---


def test_country_enum_exists() -> None:
    """Country enum loaded with 400 records (340 active, 60 deleted)."""
    result = list_enumerations()
    country = result["enumerations"]["Country"]
    assert country["record_count"] == 400
    assert country["import_only_count"] == 60


def test_country_valid() -> None:
    """MY_COUNTRY=CANADA passes validation."""
    adif = "<MY_COUNTRY:6>CANADA<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_country_invalid() -> None:
    """MY_COUNTRY=FAKELAND errors."""
    adif = "<MY_COUNTRY:8>FAKELAND<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("FAKELAND" in e for e in result["errors"])


# --- ADIF 3.1.7 new enum entries ---


def test_317_new_mode_ofdm() -> None:
    """ADIF 3.1.7: OFDM is a new Mode (Orthogonal Frequency-Division Multiplexing)."""
    adif = "<MODE:4>OFDM<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success", result
    assert not result["errors"], result["errors"]


def test_317_new_submode_ft2() -> None:
    """ADIF 3.1.7: FT2 is a new Submode under Mode MFSK."""
    adif = "<MODE:4>MFSK<SUBMODE:3>FT2<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success", result
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns, submode_warns


def test_317_new_submode_freedata() -> None:
    """ADIF 3.1.7: FREEDATA is a new Submode under Mode DYNAMIC."""
    adif = "<MODE:7>DYNAMIC<SUBMODE:8>FREEDATA<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success", result
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns, submode_warns


def test_317_new_submode_ribbit_pix() -> None:
    """ADIF 3.1.7: RIBBIT_PIX is a new Submode under Mode OFDM."""
    adif = "<MODE:4>OFDM<SUBMODE:10>RIBBIT_PIX<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success", result
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns, submode_warns


def test_317_new_submode_ribbit_sms() -> None:
    """ADIF 3.1.7: RIBBIT_SMS is a new Submode under Mode OFDM."""
    adif = "<MODE:4>OFDM<SUBMODE:10>RIBBIT_SMS<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success", result
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns, submode_warns


def test_317_submode_count() -> None:
    """ADIF 3.1.7: Submode count is 187 (3.1.6 had 183, +4 new in 3.1.7)."""
    result = list_enumerations()
    sub = result["enumerations"]["Submode"]
    assert sub["record_count"] == 187


def test_country_case_insensitive() -> None:
    """MY_COUNTRY=canada passes (case-insensitive)."""
    adif = "<MY_COUNTRY:6>canada<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_country_deleted_warns() -> None:
    """MY_COUNTRY with deleted DXCC entity → import-only warning."""
    adif = "<MY_COUNTRY:11>ABU AIL IS.<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert any("import-only" in w for w in result["warnings"])
    assert not result["errors"]


# --- Sponsored_Award prefix validation (v0.9.0) ---


def test_sponsored_award_valid_prefix() -> None:
    """AWARD_SUBMITTED=ARRL_DXCC passes (known sponsor)."""
    adif = "<AWARD_SUBMITTED:9>ARRL_DXCC<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["warnings"]


def test_sponsored_award_bad_prefix() -> None:
    """AWARD_SUBMITTED=FAKE_THING warns (unknown sponsor)."""
    adif = "<AWARD_SUBMITTED:10>FAKE_THING<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"  # warning, not error
    assert any("sponsor" in w.lower() for w in result["warnings"])


def test_sponsored_award_comma_list() -> None:
    """AWARD_SUBMITTED=ARRL_DXCC,CQ_WAZ passes (comma list, both valid)."""
    adif = "<AWARD_SUBMITTED:16>ARRL_DXCC,CQ_WAZ<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["warnings"]


# --- DXCC cross-validation (v0.9.0) ---


def test_dxcc_state_match() -> None:
    """DXCC=291 + STATE=ID passes (Idaho is in US)."""
    adif = "<DXCC:3>291<STATE:2>ID<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    dxcc_warns = [w for w in result["warnings"] if "subdivision" in w.lower()]
    assert not dxcc_warns


def test_dxcc_state_mismatch() -> None:
    """DXCC=1 + STATE=ID warns (Idaho is not in Canada)."""
    adif = "<DXCC:1>1<STATE:2>ID<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"  # warning, not error
    assert any("subdivision" in w.lower() for w in result["warnings"])


def test_dxcc_state_no_dxcc() -> None:
    """STATE=ID without DXCC → no cross-validation warning."""
    adif = "<STATE:2>ID<EOR>"
    result = validate_adif_record(adif)
    dxcc_warns = [w for w in result["warnings"] if "subdivision" in w.lower()]
    assert not dxcc_warns


# --- Date/time format validation (v0.9.0) ---


def test_date_valid() -> None:
    """QSO_DATE=20260305 passes."""
    adif = "<QSO_DATE:8>20260305<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_date_invalid_format() -> None:
    """QSO_DATE=2026-03-05 errors (hyphens not allowed)."""
    adif = "<QSO_DATE:10>2026-03-05<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("QSO_DATE" in e for e in result["errors"])


def test_date_impossible() -> None:
    """QSO_DATE=20260230 errors (Feb 30 doesn't exist)."""
    adif = "<QSO_DATE:8>20260230<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("calendar" in e.lower() for e in result["errors"])


def test_date_short() -> None:
    """QSO_DATE=202603 errors (too short)."""
    adif = "<QSO_DATE:6>202603<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("8 digits" in e for e in result["errors"])


def test_time_valid_4digit() -> None:
    """TIME_ON=1430 passes."""
    adif = "<TIME_ON:4>1430<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_time_valid_6digit() -> None:
    """TIME_ON=143022 passes."""
    adif = "<TIME_ON:6>143022<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_time_invalid_hour() -> None:
    """TIME_ON=2500 errors (hour > 23)."""
    adif = "<TIME_ON:4>2500<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("TIME_ON" in e for e in result["errors"])


def test_time_invalid_format() -> None:
    """TIME_ON=14:30 errors (colon not allowed)."""
    adif = "<TIME_ON:5>14:30<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("TIME_ON" in e for e in result["errors"])


# --- Min/max numeric bounds (v0.9.0) ---


def test_bounds_age_valid() -> None:
    """AGE=45 passes (within 0-120)."""
    adif = "<AGE:2>45<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_bounds_age_over() -> None:
    """AGE=150 errors (above max 120)."""
    adif = "<AGE:3>150<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("above maximum" in e for e in result["errors"])


def test_bounds_cqz_under() -> None:
    """CQZ=0 errors (below min 1)."""
    adif = "<CQZ:1>0<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("below minimum" in e for e in result["errors"])


def test_bounds_sfi_valid() -> None:
    """SFI=150 passes (within 0-300)."""
    adif = "<SFI:3>150<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_bounds_ant_el_negative() -> None:
    """ANT_EL=-45 passes (min is -90)."""
    adif = "<ANT_EL:3>-45<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_bounds_age_exact_min() -> None:
    """AGE=0 passes (boundary: exact minimum)."""
    adif = "<AGE:1>0<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


def test_bounds_age_exact_max() -> None:
    """AGE=3>120 passes (boundary: exact maximum)."""
    adif = "<AGE:3>120<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
