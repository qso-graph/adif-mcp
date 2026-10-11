"""KI7MT Forensic Hard Tests — grounded in 110,761 real operator QSOs.

Sources:
    ki7mt-eqsl-inbox.adi:  23,877 records (eQSL DownloadInBox export)
    ki7mt-qrz.adi:         49,233 records (QRZLogbook export)
    lotwreport-full.adi:   37,651 records (LoTW report export)

Every test case is derived from a real validation finding in KI7MT's logs.
No arbitrary tests — each has a documented real-world source and rationale.
"""

from adif_mcp.mcp.server import validate_adif_record

# --- KI7MT-FRN-001: Bread-and-butter FT8 QSO ---


def test_frn001_realistic_ft8_qso() -> None:
    """KI7MT-FRN-001: Typical FT8 QSO passes with zero errors.

    Source: QRZ export — ~15,000+ FT8 QSOs in KI7MT's 49,233-record log.
    FT8 is 88.7% of all PSK Reporter spots. If this fails, everything fails.
    """
    adif = (
        "<CALL:5>JA1ABC"
        "<BAND:3>20m"
        "<MODE:3>FT8"
        "<DXCC:3>339"
        "<CONT:2>AS"
        "<QSL_SENT:1>Y"
        "<QSL_RCVD:1>N"
        "<LOTW_QSL_SENT:1>Y"
        "<EQSL_QSL_SENT:1>Y"
        "<EOR>"
    )
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
    assert not result["warnings"]


# --- KI7MT-FRN-002: FT4 as MODE (WSJT-X false positive) ---


def test_frn002_ft4_as_mode_errors() -> None:
    """KI7MT-FRN-002: MODE=FT4 correctly errors per ADIF spec.

    Source: QRZ export — 2 of 49,233 records have MODE=FT4.
    FT4 must be MODE=MFSK + SUBMODE=FT4 per ADIF 3.1.6 policy.
    Unlike FT8 (which was grandfathered as a MODE before the policy),
    FT4 was added after the MODE/SUBMODE pattern was standardized.
    WSJT-X exports FT4 correctly; the 2 errors came from a non-compliant
    logger. This is a TRUE data error, not a false positive.
    Ref: https://wsjtx.groups.io/g/main/topic/85236332
    """
    adif = "<MODE:3>FT4<BAND:3>20m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("MODE" in e and "FT4" in e for e in result["errors"])


# --- KI7MT-FRN-003: Multi-field contest QSO ---


def test_frn003_contest_qso_multi_enum() -> None:
    """KI7MT-FRN-003: CW contest QSO with 8+ enum fields passes cleanly.

    Source: QRZ export — CQ WW DX CW contest records.
    Contest logs have the highest enum field density. Tests that
    MODE + BAND + CONTEST_ID + ARRL_SECT + DXCC + CONT + QSL + PROP_MODE
    all validate correctly in a single record with zero cross-interference.
    """
    adif = (
        "<CALL:5>DL1ABC"
        "<MODE:2>CW"
        "<BAND:3>20m"
        "<CONTEST_ID:8>CQ-WW-CW"
        "<ARRL_SECT:2>ID"
        "<DXCC:3>230"
        "<CONT:2>EU"
        "<QSL_RCVD:1>Y"
        "<QSL_SENT:1>Y"
        "<PROP_MODE:2>F2"
        "<EOR>"
    )
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


# --- KI7MT-FRN-004: LoTW dialect (uppercase band) ---


def test_frn004_lotw_uppercase_band() -> None:
    """KI7MT-FRN-004: LoTW uppercase band value (15M) passes validation.

    Source: lotwreport-full.adi — 37,651 records, all with uppercase BAND.
    LoTW exports BAND=15M, QRZ exports BAND=15m. Both must pass.
    ADIF spec requires case-insensitive matching on enumeration values.
    If this fails, every LoTW import is broken.
    """
    adif = (
        "<CALL:5>KT4KB"
        "<BAND:3>15M"
        "<MODE:4>JT65"
        "<QSL_RCVD:1>Y"
        "<DXCC:3>291"
        "<MY_DXCC:3>291"
        "<STATE:2>AR"
        "<MY_STATE:2>MT"
        "<EOR>"
    )
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


# --- KI7MT-FRN-005: QSL_VIA=M import-only ---


def test_frn005_qsl_via_manager_import_only() -> None:
    """KI7MT-FRN-005: QSL_SENT_VIA=M warns as import-only, not error.

    Source: QRZ export — pre-internet QSOs used QSL managers extensively.
    QSL_Via "M" (manager) is import-only in ADIF 3.1.6. Common in logs
    predating eQSL/LoTW. Must preserve these QSOs on import, not reject.
    """
    adif = "<QSL_SENT_VIA:1>M<QSL_SENT:1>Y<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert any("import-only" in w for w in result["warnings"])
    assert not result["errors"]


# --- KI7MT-FRN-006: Multiple QSL status fields (logger pollution) ---


def test_frn006_six_qsl_status_fields() -> None:
    """KI7MT-FRN-006: Six QSL status fields in one record, zero errors.

    Source: QRZ export — modern logs track QSL status across 3+ services.
    A single QSO may have QSL_RCVD, QSL_SENT, EQSL_QSL_RCVD,
    EQSL_QSL_SENT, LOTW_QSL_RCVD, LOTW_QSL_SENT — all enum-typed.
    Tests that multiple fields referencing the same enum (QSL_Rcvd/QSL_Sent)
    don't interfere with each other during validation.
    """
    adif = (
        "<CALL:4>NK4T"
        "<BAND:3>40m"
        "<MODE:3>SSB"
        "<QSL_RCVD:1>N"
        "<QSL_SENT:1>N"
        "<EQSL_QSL_RCVD:1>Y"
        "<EQSL_QSL_SENT:1>Y"
        "<LOTW_QSL_RCVD:1>Y"
        "<LOTW_QSL_SENT:1>Y"
        "<EOR>"
    )
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
    assert not result["warnings"]


# --- KI7MT-FRN-007: Deleted DXCC entity ---


def test_frn007_deleted_dxcc_entity() -> None:
    """KI7MT-FRN-007: Deleted DXCC entity passes validation.

    Source: DXCC enum has 62 deleted entities (e.g., Abu Ail Is., Aldabra).
    Deleted entities are NOT marked import-only — they are valid entity codes
    that appear in historical QSO logs. Validator must accept them.
    Unlike import-only Mode values, DXCC deletions are political/geographic
    (countries merged/dissolved), not protocol deprecation.
    Entity 8 = Aldabra (deleted, absorbed into entity 460 = Seychelles).
    """
    adif = "<DXCC:1>8<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


# --- KI7MT-FRN-008: Satellite QSO ---


def test_frn008_satellite_prop_mode() -> None:
    """KI7MT-FRN-008: PROP_MODE=SAT passes for satellite QSOs.

    Source: QRZ export — KI7MT satellite QSOs (FM birds, ISS, etc.).
    Propagation_Mode enum is rarely tested but critical for satellite
    and EME operators. 19 valid propagation modes in the spec.
    """
    adif = (
        "<CALL:6>NA1ISS"
        "<BAND:4>70cm"
        "<MODE:2>FM"
        "<PROP_MODE:3>SAT"
        "<EOR>"
    )
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


# --- KI7MT-FRN-009: Credit with & multi-medium separator ---


def test_frn009_credit_multi_medium_ampersand() -> None:
    """KI7MT-FRN-009: CREDIT_SUBMITTED with & separator between mediums.

    Source: LoTW DXCC credit reports use CREDIT:MEDIUM1&MEDIUM2 format.
    Example: DXCC confirmed via both paper QSL card AND LoTW electronic.
    Tests the & separator — a critical parsing edge in CreditList format.
    """
    adif = "<CREDIT_SUBMITTED:14>DXCC:CARD&LOTW<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]


# --- KI7MT-FRN-010: Freeform CONTEST_ID (real data error) ---


def test_frn010_freeform_contest_id_errors() -> None:
    """KI7MT-FRN-010: Freeform CONTEST_ID text correctly errors.

    Source: eQSL inbox — 470 of 23,877 records have invalid CONTEST_ID.
    Operators type freeform text ("CQWW 2021", "DX", "wpx", "CQ WW RTTY")
    instead of spec-defined Contest-IDs like "CQ-WW-CW" or "CQ-WW-RTTY".
    These are TRUE data errors — the Contest_ID enum has 431 specific values.
    """
    adif = "<CONTEST_ID:9>CQWW 2021<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "invalid"
    assert any("CONTEST_ID" in e for e in result["errors"])


# --- KI7MT-FRN-011: SUBMODE without MODE field ---


def test_frn011_submode_without_mode() -> None:
    """KI7MT-FRN-011: SUBMODE without MODE field validates gracefully.

    Source: eQSL inbox — some records have SUBMODE but omit MODE.
    Submode validation is conditional on MODE (parent mode check).
    When MODE is absent, submode membership should still be checked,
    but parent mode mismatch warning must be skipped (nothing to compare).
    """
    adif = "<SUBMODE:3>USB<BAND:3>20m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
    # No submode mismatch warning (MODE is absent — nothing to compare)
    submode_warns = [w for w in result["warnings"] if "submode" in w.lower()]
    assert not submode_warns


# --- KI7MT-FRN-012: eQSL Authenticity Guaranteed status ---


def test_frn012_eqsl_ag_status() -> None:
    """KI7MT-FRN-012: EQSL_AG=Y passes validation.

    Source: eQSL inbox — Authenticity Guaranteed is a key eQSL feature.
    EQSL_AG has only 3 valid values (Y/N/U). This is a less-tested enum
    that's critical for DXCC credit via eQSL — AG status determines
    whether an eQSL confirmation is accepted by ARRL for DXCC credit.
    """
    adif = "<EQSL_AG:1>Y<MODE:3>SSB<BAND:3>20m<EOR>"
    result = validate_adif_record(adif)
    assert result["status"] == "success"
    assert not result["errors"]
