# ADIF-MCP Test Case Register

**Version**: v0.7.0
**Spec**: ADIF 3.1.7 (2026-03-22)
**Official Test Corpus**: G3ZOD `CreateADIFTestFiles` (https://adif.org.uk/316/resources)
**Reference Validators**: K1MU Validator (web), adif-multitool (CLI, G3ZOD/flwyd)

## Test Matrix Summary

| Category | Tests | Status |
|----------|-------|--------|
| Enumeration Listing (ADIF-ENL) | 3 | 3/3 PASS |
| Enumeration Search (ADIF-ENS) | 6 | 6/6 PASS |
| Enum Validation — Simple (ADIF-EVS) | 6 | 6/6 PASS |
| Enum Validation — Compound (ADIF-EVC) | 3 | 3/3 PASS |
| Enum Validation — Conditional (ADIF-EVX) | 2 | 2/2 PASS |
| Enum Validation — Regression (ADIF-EVR) | 1 | 1/1 PASS |
| Official ADIF 3.1.7 Test Corpus (ADIF-TCR) | 2 | 2/2 PASS |
| Enum JSON Parity vs Official Export | 1 | 1/1 PASS (manual) |
| KI7MT Forensic Hard Tests (KI7MT-FRN) | 12 | 12/12 PASS |
| **Total** | **40** | **40/40 PASS** |

## Run Command

```bash
cd adif-mcp
.venv/bin/python -m pytest test/test_enumerations.py test/test_ki7mt_forensic.py -v
```

---

## ADIF-ENL: Enumeration Listing

### ADIF-ENL-001: Enumeration Count

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENL-001 |
| **Name** | Enumeration count matches ADIF 3.1.7 spec |
| **Tool** | `list_enumerations` |
| **Purpose** | Verify all 25 ADIF 3.1.7 enumerations are loaded and exposed |
| **Input** | None |
| **Expected** | `enumeration_count` = 25, `enumerations` dict has 25 keys |
| **Pass Criteria** | Both assertions hold |
| **Result** | PASS |

### ADIF-ENL-002: Mode Enumeration Detail

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENL-002 |
| **Name** | Mode enum has correct record and import-only counts |
| **Tool** | `list_enumerations` |
| **Purpose** | Mode has 90 values (48 active + 42 import-only). Verify counts. |
| **Input** | None |
| **Expected** | `record_count` = 90, `import_only_count` = 42, "Mode" in searchable fields |
| **Pass Criteria** | All three assertions hold |
| **Result** | PASS |

### ADIF-ENL-003: Band Enumeration Detail

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENL-003 |
| **Name** | Band enum has 33 records, zero import-only |
| **Tool** | `list_enumerations` |
| **Purpose** | All 33 ADIF bands are active (none deprecated) |
| **Input** | None |
| **Expected** | `record_count` = 33, `import_only_count` = 0 |
| **Pass Criteria** | Both assertions hold |
| **Result** | PASS |

---

## ADIF-ENS: Enumeration Search

### ADIF-ENS-001: Search FT8 in Mode

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENS-001 |
| **Name** | Find FT8 in Mode enumeration |
| **Tool** | `search_enumerations("FT8", enumeration="Mode")` |
| **Purpose** | Basic targeted search — FT8 is the most-used digital mode |
| **Input** | search_term="FT8", enumeration="Mode" |
| **Expected** | Results contain Mode enum with FT8 in records |
| **Pass Criteria** | "FT8" in found mode values |
| **Result** | PASS |

### ADIF-ENS-002: Search 20m in Band

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENS-002 |
| **Name** | Find 20m in Band enumeration |
| **Tool** | `search_enumerations("20m", enumeration="Band")` |
| **Purpose** | Verify band search works with standard band notation |
| **Input** | search_term="20m", enumeration="Band" |
| **Expected** | Results contain Band enum with "20m" |
| **Pass Criteria** | "20m" in found band values |
| **Result** | PASS |

### ADIF-ENS-003: Search DXCC Entity

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENS-003 |
| **Name** | Find "United States" in DXCC Entity Code |
| **Tool** | `search_enumerations("United States", enumeration="DXCC_Entity_Code")` |
| **Purpose** | Verify multi-word search against entity names |
| **Input** | search_term="United States", enumeration="DXCC_Entity_Code" |
| **Expected** | DXCC_Entity_Code in results |
| **Pass Criteria** | Results dict contains DXCC_Entity_Code key |
| **Result** | PASS |

### ADIF-ENS-004: Search CQ-WW Contest ID

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENS-004 |
| **Name** | Find CQ-WW in Contest_ID |
| **Tool** | `search_enumerations("CQ-WW", enumeration="Contest_ID")` |
| **Purpose** | Verify hyphenated search terms work correctly |
| **Input** | search_term="CQ-WW", enumeration="Contest_ID" |
| **Expected** | Match count >= 1 in Contest_ID results |
| **Pass Criteria** | At least one match |
| **Result** | PASS |

### ADIF-ENS-005: Case-Insensitive Search

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENS-005 |
| **Name** | Lowercase "ft8" finds uppercase "FT8" |
| **Tool** | `search_enumerations("ft8", enumeration="Mode")` |
| **Purpose** | Verify case normalization in search |
| **Input** | search_term="ft8", enumeration="Mode" |
| **Expected** | FT8 found despite lowercase input |
| **Pass Criteria** | "FT8" in found mode values |
| **Result** | PASS |

### ADIF-ENS-006: Cross-Enum Search (No Filter)

| Field | Value |
|-------|-------|
| **ID** | ADIF-ENS-006 |
| **Name** | Unfiltered search hits multiple enumerations |
| **Tool** | `search_enumerations("CW")` |
| **Purpose** | Verify all-enum search works (CW appears in Mode + possibly Submode) |
| **Input** | search_term="CW", no enumeration filter |
| **Expected** | `enumerations_matched` >= 1 |
| **Pass Criteria** | At least one enumeration matched |
| **Result** | PASS |

---

## ADIF-EVS: Enum Validation — Simple

### ADIF-EVS-001: Valid Mode

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVS-001 |
| **Name** | MODE=CW passes validation |
| **Tool** | `validate_adif_record` |
| **Purpose** | CW is a valid, active Mode value |
| **Input** | `<MODE:2>CW<EOR>` |
| **Expected** | status="success", zero errors |
| **Pass Criteria** | No errors in report |
| **Result** | PASS |

### ADIF-EVS-002: Invalid Mode

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVS-002 |
| **Name** | MODE=INVALID produces error |
| **Tool** | `validate_adif_record` |
| **Purpose** | "INVALID" is not a valid Mode — must be caught |
| **Input** | `<MODE:7>INVALID<EOR>` |
| **Expected** | status="invalid", error mentions MODE and INVALID |
| **Pass Criteria** | Error list contains MODE+INVALID |
| **Result** | PASS |

### ADIF-EVS-003: Valid Band

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVS-003 |
| **Name** | BAND=20m passes validation |
| **Tool** | `validate_adif_record` |
| **Purpose** | 20m is a valid Band value |
| **Input** | `<BAND:3>20m<EOR>` |
| **Expected** | status="success", zero errors |
| **Pass Criteria** | No errors |
| **Result** | PASS |

### ADIF-EVS-004: Invalid Band

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVS-004 |
| **Name** | BAND=25m produces error |
| **Tool** | `validate_adif_record` |
| **Purpose** | 25m is not a valid ADIF band |
| **Input** | `<BAND:3>25m<EOR>` |
| **Expected** | status="invalid", error mentions BAND and 25m |
| **Pass Criteria** | Error list contains BAND+25m |
| **Result** | PASS |

### ADIF-EVS-005: Import-Only Warning

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVS-005 |
| **Name** | Import-only MODE value warns, does not error |
| **Tool** | `validate_adif_record` |
| **Purpose** | AMTORFEC is import-only — acceptable on import but not for new QSOs |
| **Input** | `<MODE:8>AMTORFEC<EOR>` |
| **Expected** | status="success", warning contains "import-only", zero errors |
| **Pass Criteria** | Warning present, no errors |
| **Physics** | Import-only modes are valid historical data; rejecting them loses QSOs |
| **Result** | PASS |

### ADIF-EVS-006: Case-Insensitive Validation

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVS-006 |
| **Name** | MODE=cw (lowercase) passes validation |
| **Tool** | `validate_adif_record` |
| **Purpose** | ADIF field values are case-insensitive per spec |
| **Input** | `<MODE:2>cw<EOR>` |
| **Expected** | status="success", zero errors |
| **Pass Criteria** | No errors |
| **Result** | PASS |

---

## ADIF-EVC: Enum Validation — Compound

### ADIF-EVC-001: Credit:Medium Format

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVC-001 |
| **Name** | CREDIT_SUBMITTED with Credit:QSL_Medium passes |
| **Tool** | `validate_adif_record` |
| **Purpose** | CreditList format is `CreditName:QSL_Medium`. DXCC:CARD = valid credit + valid medium. |
| **Input** | `<CREDIT_SUBMITTED:9>DXCC:CARD<EOR>` |
| **Expected** | status="success", zero errors |
| **Pass Criteria** | No errors |
| **Result** | PASS |

### ADIF-EVC-002: Plain Credit (No Medium)

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVC-002 |
| **Name** | CREDIT_SUBMITTED with plain credit name passes |
| **Tool** | `validate_adif_record` |
| **Purpose** | QSL medium is optional in CreditList format |
| **Input** | `<CREDIT_SUBMITTED:4>DXCC<EOR>` |
| **Expected** | status="success", zero errors |
| **Pass Criteria** | No errors |
| **Result** | PASS |

### ADIF-EVC-003: Invalid Credit Name

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVC-003 |
| **Name** | CREDIT_SUBMITTED with bad credit name errors |
| **Tool** | `validate_adif_record` |
| **Purpose** | "FAKE" is not a valid Credit For value |
| **Input** | `<CREDIT_SUBMITTED:9>FAKE:CARD<EOR>` |
| **Expected** | status="invalid", error mentions CREDIT_SUBMITTED |
| **Pass Criteria** | Error present |
| **Result** | PASS |

---

## ADIF-EVX: Enum Validation — Conditional

### ADIF-EVX-001: Submode-Mode Match

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVX-001 |
| **Name** | SUBMODE=USB with MODE=SSB passes cleanly |
| **Tool** | `validate_adif_record` |
| **Purpose** | USB is a valid Submode of SSB — no warning expected |
| **Input** | `<MODE:3>SSB<SUBMODE:3>USB<EOR>` |
| **Expected** | status="success", zero errors, zero submode warnings |
| **Pass Criteria** | No errors, no submode-related warnings |
| **Result** | PASS |

### ADIF-EVX-002: Submode-Mode Mismatch

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVX-002 |
| **Name** | SUBMODE=USB with MODE=CW produces warning |
| **Tool** | `validate_adif_record` |
| **Purpose** | USB belongs to SSB, not CW — warn on parent mode mismatch |
| **Input** | `<MODE:2>CW<SUBMODE:3>USB<EOR>` |
| **Expected** | status="success" (warning, not error), warning mentions submode + USB |
| **Pass Criteria** | Warning present, not an error |
| **Physics** | Parent mode mismatch may indicate data entry error |
| **Result** | PASS |

---

## ADIF-EVR: Enum Validation — Regression

### ADIF-EVR-001: Number Validation Unchanged

| Field | Value |
|-------|-------|
| **ID** | ADIF-EVR-001 |
| **Name** | Existing Number type validation still works |
| **Tool** | `validate_adif_record` |
| **Purpose** | v0.7.0 enum changes must not break pre-existing Number validation |
| **Input** | `<AGE:3>abc<EOR>` |
| **Expected** | status="invalid", error mentions AGE + Number |
| **Pass Criteria** | Error present with correct field and type |
| **Result** | PASS |

---

## ADIF-TCR: Official ADIF 3.1.7 Test Corpus

### ADIF-TCR-001: Zero False Errors

| Field | Value |
|-------|-------|
| **ID** | ADIF-TCR-001 |
| **Name** | Zero false errors on official ADIF 3.1.7 test QSOs |
| **Tool** | `validate_adif_record` (iterated over 6,197 records) |
| **Purpose** | The official test file from adif.org.uk exercises every enumeration value in the spec. If our validator rejects any official record, **our validator is wrong**. |
| **Source** | `https://adif.org.uk/317/` — `ADIF_317_test_QSOs_2026_03_22.adi` |
| **Generator** | G3ZOD `CreateADIFTestFiles` (3.1.7 corpus) |
| **Records** | 6,197 QSOs covering all 25 enumerations, all field types, user-defined fields, app-defined fields |
| **Expected** | Zero errors across all 6,197 records |
| **Pass Criteria** | `len(all_errors) == 0` |
| **Result** | **PASS — 0 errors on 6,197 records** |

### ADIF-TCR-002: Warning Categories Are Legitimate

| Field | Value |
|-------|-------|
| **ID** | ADIF-TCR-002 |
| **Name** | All warnings on official test file are correct behavior |
| **Tool** | `validate_adif_record` (iterated over 6,197 records) |
| **Purpose** | Verify warnings are real (not misclassified errors). The test file deliberately uses user-defined fields and import-only values. |
| **Expected** | ~39 warnings total, all in categories: "not in spec" (user/app-defined fields), "import-only" (deprecated enum values), or "submode" (parent mode mismatch) |
| **Pass Criteria** | 30-50 warnings, every warning matches a known category |
| **Observed** | 39 warnings: 23 user/app-defined fields + 16 import-only values |
| **Result** | **PASS** |

### Enum JSON Parity (Manual Verification)

| Field | Value |
|-------|-------|
| **ID** | ADIF-TCR-003 |
| **Name** | Our 25 enum JSON files match official ADIF 3.1.7 exports exactly |
| **Purpose** | Verify we ship the authoritative data, not a stale or modified copy |
| **Method** | Compare record counts and keys between `src/adif_mcp/resources/spec/316/enumerations_*.json` and official `316/exports/json/enumerations_*.json` from the ZIP archive |
| **Expected** | Identical record counts and identical record keys for all 25 enumerations |
| **Result** | **PASS — all 25 files match exactly** |

---

## KI7MT-FRN: Forensic Hard Tests (Operator-Grounded)

**Source**: 110,761 real QSO records from KI7MT's production logs.
**Method**: Forensic analysis of validation results across three logger dialects (eQSL, QRZ, LoTW).
**Standard**: Every test has a documented real-world source. No arbitrary tests.

### KI7MT-FRN-001: Bread-and-Butter FT8 QSO

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-001 |
| **Name** | Typical FT8 QSO with 9 enum fields passes cleanly |
| **Tool** | `validate_adif_record` |
| **Source** | QRZ export — ~15,000+ FT8 QSOs in 49,233-record log |
| **Purpose** | FT8 is 88.7% of all PSK Reporter spots. If this fails, everything fails. |
| **Input** | `<CALL:5>JA1ABC<BAND:3>20m<MODE:3>FT8<DXCC:3>339<CONT:2>AS<QSL_SENT:1>Y<QSL_RCVD:1>N<LOTW_QSL_SENT:1>Y<EQSL_QSL_SENT:1>Y<EOR>` |
| **Expected** | status="success", zero errors, zero warnings |
| **Result** | PASS |

### KI7MT-FRN-002: FT4 as MODE (True Data Error)

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-002 |
| **Name** | MODE=FT4 correctly errors per ADIF 3.1.7 spec |
| **Tool** | `validate_adif_record` |
| **Source** | QRZ export — 2 of 49,233 records have MODE=FT4 |
| **Purpose** | FT4 must be `MODE=MFSK + SUBMODE=FT4` per ADIF 3.1.7 policy. Unlike FT8 (grandfathered as a MODE before the policy), FT4 was added after MODE/SUBMODE standardization. WSJT-X exports FT4 correctly; the 2 errors came from a non-compliant logger. |
| **Input** | `<MODE:3>FT4<BAND:3>20m<EOR>` |
| **Expected** | status="invalid", error mentions MODE + FT4 |
| **Rationale** | Ref: https://wsjtx.groups.io/g/main/topic/85236332 — FT8 was rushed through before ADIF 3 policy; FT4 follows the rules. This is a TRUE data error, not a false positive. |
| **Result** | PASS |

### KI7MT-FRN-003: Multi-Field Contest QSO

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-003 |
| **Name** | CW contest QSO with 8+ enum fields passes cleanly |
| **Tool** | `validate_adif_record` |
| **Source** | QRZ export — CQ WW DX CW contest records |
| **Purpose** | Contest logs have the highest enum field density. Tests MODE + BAND + CONTEST_ID + ARRL_SECT + DXCC + CONT + QSL_RCVD + QSL_SENT + PROP_MODE all in one record with zero cross-interference. |
| **Input** | `<CALL:5>DL1ABC<MODE:2>CW<BAND:3>20m<CONTEST_ID:8>CQ-WW-CW<ARRL_SECT:2>ID<DXCC:3>230<CONT:2>EU<QSL_RCVD:1>Y<QSL_SENT:1>Y<PROP_MODE:2>F2<EOR>` |
| **Expected** | status="success", zero errors |
| **Result** | PASS |

### KI7MT-FRN-004: LoTW Dialect (Uppercase Band)

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-004 |
| **Name** | LoTW uppercase band value (15M) passes validation |
| **Tool** | `validate_adif_record` |
| **Source** | lotwreport-full.adi — 37,651 records, all with uppercase BAND |
| **Purpose** | LoTW exports BAND=15M, QRZ exports BAND=15m. Both must pass. ADIF spec requires case-insensitive matching. If this fails, every LoTW import is broken. |
| **Input** | `<CALL:5>KT4KB<BAND:3>15M<MODE:4>JT65<QSL_RCVD:1>Y<DXCC:3>291<MY_DXCC:3>291<STATE:2>AR<MY_STATE:2>MT<EOR>` |
| **Expected** | status="success", zero errors |
| **Result** | PASS |

### KI7MT-FRN-005: QSL_VIA=M Import-Only

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-005 |
| **Name** | QSL_SENT_VIA=M warns as import-only, not error |
| **Tool** | `validate_adif_record` |
| **Source** | QRZ export — pre-internet QSOs used QSL managers extensively |
| **Purpose** | QSL_Via "M" (manager) is import-only in 3.1.7. Common in logs predating eQSL/LoTW. Must preserve these QSOs on import, not reject. |
| **Input** | `<QSL_SENT_VIA:1>M<QSL_SENT:1>Y<EOR>` |
| **Expected** | status="success", warning contains "import-only", zero errors |
| **Result** | PASS |

### KI7MT-FRN-006: Six QSL Status Fields (Logger Pollution)

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-006 |
| **Name** | Six QSL status fields in one record, zero errors |
| **Tool** | `validate_adif_record` |
| **Source** | QRZ export — modern logs track QSL status across 3+ services |
| **Purpose** | Tests QSL_RCVD + QSL_SENT + EQSL_QSL_RCVD + EQSL_QSL_SENT + LOTW_QSL_RCVD + LOTW_QSL_SENT — six enum-typed fields referencing the same enums (QSL_Rcvd/QSL_Sent). Must not interfere with each other. |
| **Input** | `<CALL:4>NK4T<BAND:3>40m<MODE:3>SSB<QSL_RCVD:1>N<QSL_SENT:1>N<EQSL_QSL_RCVD:1>Y<EQSL_QSL_SENT:1>Y<LOTW_QSL_RCVD:1>Y<LOTW_QSL_SENT:1>Y<EOR>` |
| **Expected** | status="success", zero errors, zero warnings |
| **Result** | PASS |

### KI7MT-FRN-007: Deleted DXCC Entity

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-007 |
| **Name** | Deleted DXCC entity passes validation |
| **Tool** | `validate_adif_record` |
| **Source** | DXCC enum has 62 deleted entities (political/geographic mergers) |
| **Purpose** | Deleted entities are valid entity codes in historical QSO logs. Unlike import-only Mode values, DXCC deletions are not protocol deprecation — they are geopolitical events. Entity 8 = Aldabra (absorbed into Seychelles). |
| **Input** | `<DXCC:1>8<EOR>` |
| **Expected** | status="success", zero errors |
| **Result** | PASS |

### KI7MT-FRN-008: Satellite QSO (PROP_MODE=SAT)

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-008 |
| **Name** | PROP_MODE=SAT passes for satellite QSOs |
| **Tool** | `validate_adif_record` |
| **Source** | QRZ export — satellite QSOs (FM birds, ISS, etc.) |
| **Purpose** | Propagation_Mode enum (19 values) is rarely tested but critical for satellite and EME operators. Tests a non-HF enum that most validators overlook. |
| **Input** | `<CALL:6>NA1ISS<BAND:4>70cm<MODE:2>FM<PROP_MODE:3>SAT<EOR>` |
| **Expected** | status="success", zero errors |
| **Result** | PASS |

### KI7MT-FRN-009: Credit with & Multi-Medium Separator

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-009 |
| **Name** | CREDIT_SUBMITTED with & separator between mediums |
| **Tool** | `validate_adif_record` |
| **Source** | LoTW DXCC credit reports — CREDIT:MEDIUM1&MEDIUM2 format |
| **Purpose** | Tests the & separator for multiple QSL mediums per credit (e.g., confirmed via both paper card AND LoTW). This is a critical parsing edge in CreditList format that the G3ZOD corpus exercises but could easily regress. |
| **Input** | `<CREDIT_SUBMITTED:14>DXCC:CARD&LOTW<EOR>` |
| **Expected** | status="success", zero errors |
| **Result** | PASS |

### KI7MT-FRN-010: Freeform CONTEST_ID (Real Data Error)

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-010 |
| **Name** | Freeform CONTEST_ID text correctly errors |
| **Tool** | `validate_adif_record` |
| **Source** | eQSL inbox — 470 of 23,877 records have invalid CONTEST_ID |
| **Purpose** | Operators type freeform text ("CQWW 2021", "DX", "wpx") instead of spec-defined values like "CQ-WW-CW". The Contest_ID enum has 431 specific values. These are TRUE data errors that the validator must catch. |
| **Input** | `<CONTEST_ID:9>CQWW 2021<EOR>` |
| **Expected** | status="invalid", error mentions CONTEST_ID |
| **Result** | PASS |

### KI7MT-FRN-011: SUBMODE Without MODE Field

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-011 |
| **Name** | SUBMODE without MODE validates gracefully |
| **Tool** | `validate_adif_record` |
| **Source** | eQSL inbox — some records have SUBMODE but omit MODE |
| **Purpose** | Submode validation is conditional on MODE (parent mode check). When MODE is absent, submode membership should still be checked, but parent mismatch warning must be skipped. Tests graceful handling of incomplete records. |
| **Input** | `<SUBMODE:3>USB<BAND:3>20m<EOR>` |
| **Expected** | status="success", zero errors, zero submode warnings |
| **Result** | PASS |

### KI7MT-FRN-012: eQSL Authenticity Guaranteed Status

| Field | Value |
|-------|-------|
| **ID** | KI7MT-FRN-012 |
| **Name** | EQSL_AG=Y passes validation |
| **Tool** | `validate_adif_record` |
| **Source** | eQSL inbox — AG status determines DXCC credit eligibility via eQSL |
| **Purpose** | EQSL_AG has only 3 valid values (Y/N/U). This is a less-tested enum that's critical for DXCC credit — AG status determines whether an eQSL confirmation is accepted by ARRL. |
| **Input** | `<EQSL_AG:1>Y<MODE:3>SSB<BAND:3>20m<EOR>` |
| **Expected** | status="success", zero errors |
| **Result** | PASS |

---

## Known Limitations (v0.7.0)

| Limitation | Reason | Planned |
|------------|--------|---------|
| CNTY/MY_CNTY skipped | SAS enum ships only 58 Alaska records; full US county list (~3,200) not included | v0.8.0 |
| Country enum not validated | No `enumerations_country.json` ships with ADIF spec | v0.8.0 |
| Sponsored_Award enum not validated | No `enumerations_sponsored_award.json` ships | v0.8.0 |
| Deleted DXCC entities not warned | 62 deleted entities pass silently (correct per spec, but user may want advisory) | v0.8.0 |
| DXCC cross-validation (STATE must match DXCC entity) | Parameterized enum — complex | Deferred |
| Date/time format validation | Not enum-related | Deferred |
| Numeric min/max bounds | Not enum-related | Deferred |

---

## Mode/Submode Notes (Watson Research, 2026-03-05)

FT8 was rushed into the ADIF spec as its own MODE before the MODE/SUBMODE policy was standardized. FT4 was added later per the correct policy: `MODE=MFSK + SUBMODE=FT4`.

| Service | FT8 Handling | FT4 Handling | SUBMODE Stored? |
|---------|-------------|-------------|-----------------|
| LoTW | MODE=FT8 → DATA group | MODE=MFSK + SUBMODE=FT4 | Yes |
| eQSL | MODE=FT8 accepted | MODE=MFSK + SUBMODE=FT4 | Yes |
| QRZ | ADIF standard, lossless | ADIF standard, lossless | Yes |
| WSJT-X | Exports MODE=FT8 | Exports MODE=MFSK + SUBMODE=FT4 | Yes |

**Key anomalies**:
- DXKeeper flattens SUBMODE into Mode, loses original MODE
- Some loggers export "DIGI" or "DATA" as MODE — not valid ADIF, correctly rejected
- LoTW collapses all digital modes to DATA for award matching (Mode Groups)

**Ref**: https://wsjtx.groups.io/g/main/topic/85236332

---

## References

| Resource | URL |
|----------|-----|
| ADIF 3.1.7 Specification | https://adif.org/316/ADIF_316.htm |
| ADIF 3.1.7 Resources (ZIP) | https://adif.org.uk/316/resources |
| ADIF Resources Page | https://adif.org/316/ADIF_316_Resources.htm |
| CreateADIFTestFiles (G3ZOD) | https://github.com/g3zod/CreateADIFTestFiles |
| CreateADIFExportFiles (G3ZOD) | https://github.com/g3zod/CreateADIFExportFiles |
| K1MU ADIF Validator | https://www.rickmurphy.net/adifvalidator.html |
| adif-multitool (flwyd) | https://github.com/flwyd/adif-multitool |
| ADIF Program ID Register | https://adif.org.uk/programids.html |
| FT8/FT4 Mode vs Submode Discussion | https://wsjtx.groups.io/g/main/topic/85236332 |
| eQSL ADIF Content Specs | https://www.eqsl.cc/qslcard/ADIFContentSpecs.cfm |
