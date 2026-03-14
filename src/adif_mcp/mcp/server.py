"""
ADIF-MCP Server: Authoritative 3.1.6 Specification Server.

Provides tools for parsing, streaming, and validating ADIF data.
"""

import datetime
import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import aiofiles
import mcp.types as types
from fastmcp import FastMCP

import adif_mcp
from adif_mcp.utils.geography import calculate_distance_impl, calculate_heading_impl

# Initialize the FastMCP server
mcp = FastMCP("ADIF-MCP")


# --- Enumeration Infrastructure ---

# Searchable fields per enumeration (hardcoded per Patton requirement)
ENUMERATION_FIELDS: Dict[str, List[str]] = {
    "Ant_Path": ["Abbreviation", "Meaning"],
    "ARRL_Section": ["Abbreviation", "Section Name"],
    "Award": ["Award"],
    "Award_Sponsor": ["Sponsor", "Sponsoring Organization"],
    "Band": ["Band"],
    "Contest_ID": ["Contest-ID", "Description"],
    "Continent": ["Abbreviation", "Continent"],
    "Country": ["Country Name", "DXCC Entity Code"],
    "Credit": ["Credit For", "Sponsor", "Award"],
    "DXCC_Entity_Code": ["Entity Code", "Entity Name"],
    "EQSL_AG": ["Status", "Description"],
    "Mode": ["Mode"],
    "Morse_Key_Type": ["Abbreviation", "Meaning"],
    "Primary_Administrative_Subdivision": ["Code", "Primary Administrative Subdivision"],
    "Propagation_Mode": ["Enumeration", "Description"],
    "QSL_Medium": ["Medium", "Description"],
    "QSL_Rcvd": ["Status", "Meaning"],
    "QSL_Sent": ["Status", "Meaning"],
    "QSL_Via": ["Via", "Description"],
    "QSO_Complete": ["Abbreviation", "Meaning"],
    "QSO_Download_Status": ["Status", "Description"],
    "QSO_Upload_Status": ["Status", "Description"],
    "Region": ["Region Entity Code", "Region"],
    "Secondary_Administrative_Subdivision": [
        "Code", "Secondary Administrative Subdivision",
    ],
    "Secondary_Administrative_Subdivision_Alt": ["Code", "Region", "District"],
    "Submode": ["Submode", "Mode"],
}

# Primary key field for membership validation per enumeration
ENUM_VALIDATION_KEY: Dict[str, str] = {
    "Ant_Path": "Abbreviation",
    "ARRL_Section": "Abbreviation",
    "Award": "Award",
    "Award_Sponsor": "Sponsor",
    "Band": "Band",
    "Contest_ID": "Contest-ID",
    "Continent": "Abbreviation",
    "Country": "Country Name",
    "Credit": "Credit For",
    "DXCC_Entity_Code": "Entity Code",
    "EQSL_AG": "Status",
    "Mode": "Mode",
    "Morse_Key_Type": "Abbreviation",
    "Primary_Administrative_Subdivision": "Code",
    "Propagation_Mode": "Enumeration",
    "QSL_Medium": "Medium",
    "QSL_Rcvd": "Status",
    "QSL_Sent": "Status",
    "QSL_Via": "Via",
    "QSO_Complete": "Abbreviation",
    "QSO_Download_Status": "Status",
    "QSO_Upload_Status": "Status",
    "Region": "Region Entity Code",
    "Secondary_Administrative_Subdivision": "Code",
    "Secondary_Administrative_Subdivision_Alt": "Code",
    "Submode": "Submode",
}

# ADIF field name -> enumeration spec string (from fields.json)
# Covers all 43 enum-typed fields. Parameterized enums use [PARAM] suffix.
FIELD_ENUM_MAP: Dict[str, str] = {
    "ANT_PATH": "Ant_Path",
    "ARRL_SECT": "ARRL_Section",
    "AWARD_GRANTED": "Sponsored_Award",
    "AWARD_SUBMITTED": "Sponsored_Award",
    "BAND": "Band",
    "BAND_RX": "Band",
    "CLUBLOG_QSO_UPLOAD_STATUS": "QSO_Upload_Status",
    "CNTY": "Secondary_Administrative_Subdivision",
    "CONT": "Continent",
    "CONTEST_ID": "Contest_ID",
    "CREDIT_GRANTED": "Credit,Award",
    "CREDIT_SUBMITTED": "Credit,Award",
    "DCL_QSL_RCVD": "QSL_Rcvd",
    "DCL_QSL_SENT": "QSL_Sent",
    "DXCC": "DXCC_Entity_Code",
    "EQSL_AG": "EQSL_AG",
    "EQSL_QSL_RCVD": "QSL_Rcvd",
    "EQSL_QSL_SENT": "QSL_Sent",
    "HAMLOGEU_QSO_UPLOAD_STATUS": "QSO_Upload_Status",
    "HAMQTH_QSO_UPLOAD_STATUS": "QSO_Upload_Status",
    "HRDLOG_QSO_UPLOAD_STATUS": "QSO_Upload_Status",
    "LOTW_QSL_RCVD": "QSL_Rcvd",
    "LOTW_QSL_SENT": "QSL_Sent",
    "MODE": "Mode",
    "MORSE_KEY_TYPE": "Morse_Key_Type",
    "MY_ARRL_SECT": "ARRL_Section",
    "MY_CNTY": "Secondary_Administrative_Subdivision",
    "MY_COUNTRY": "Country",
    "MY_COUNTRY_INTL": "Country",
    "MY_DXCC": "DXCC_Entity_Code",
    "MY_MORSE_KEY_TYPE": "Morse_Key_Type",
    "MY_STATE": "Primary_Administrative_Subdivision",
    "PROP_MODE": "Propagation_Mode",
    "QRZCOM_QSO_DOWNLOAD_STATUS": "QSO_Download_Status",
    "QRZCOM_QSO_UPLOAD_STATUS": "QSO_Upload_Status",
    "QSL_RCVD": "QSL_Rcvd",
    "QSL_RCVD_VIA": "QSL_Via",
    "QSL_SENT": "QSL_Sent",
    "QSL_SENT_VIA": "QSL_Via",
    "QSO_COMPLETE": "QSO_Complete",
    "REGION": "Region",
    "STATE": "Primary_Administrative_Subdivision",
    "SUBMODE": "Submode",
}

# Enumerations that have no shipped JSON file — skip gracefully
_MISSING_ENUM_FILES = {"Sponsored_Award"}

# Fields with incomplete enum data — skip validation (warn only in future)
# SAS ships only 58 Alaska records; full US county data is ~3,200 entries
_INCOMPLETE_ENUM_FIELDS = {"CNTY", "MY_CNTY"}

# In-memory cache for loaded enumeration records
_enum_cache: Dict[str, Dict[str, Any]] = {}


def _load_enum_records(enum_name: str) -> Dict[str, Any]:
    """Load enumeration records from JSON, with in-memory caching."""
    if enum_name in _enum_cache:
        return _enum_cache[enum_name]

    raw = get_spec_text(enum_name.lower())
    try:
        data = json.loads(raw)
        records = data["Adif"]["Enumerations"][enum_name]["Records"]
    except (json.JSONDecodeError, KeyError, TypeError):
        records = {}

    _enum_cache[enum_name] = records
    result: Dict[str, Any] = records
    return result


def _validate_enum_field(
    field_name: str,
    value: str,
    enum_spec: str,
    parsed: Dict[str, str],
) -> Tuple[List[str], List[str]]:
    """Validate a field value against its enumeration.

    Returns (errors, warnings).
    Handles: simple, compound (Credit,Award), conditional (Submode[MODE]),
    parameterized (PAS[DXCC]), import-only, and missing enum files.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Sponsored_Award: validate sponsor prefix only (no full enum file)
    if enum_spec == "Sponsored_Award":
        return _validate_sponsored_award(field_name, value)

    # Skip enumerations with no shipped JSON file
    if enum_spec in _MISSING_ENUM_FILES:
        return errors, warnings

    # Compound enumerations: "Credit,Award" — ADIF CreditList format.
    # Value is comma-separated elements. Each element may be:
    #   "CREDIT_NAME" (plain) or "CREDIT_NAME:QSL_MEDIUM" or
    #   "CREDIT_NAME:MEDIUM1&MEDIUM2" (multiple mediums with &)
    # The credit name must exist in Credit OR Award enum.
    # The medium (if present) must exist in QSL_Medium enum.
    if "," in enum_spec:
        enum_names = [e.strip() for e in enum_spec.split(",")]
        elements = [v.strip() for v in value.split(",") if v.strip()]
        for element in elements:
            # Split credit:medium if colon present
            if ":" in element:
                credit_part, medium_part = element.split(":", 1)
            else:
                credit_part = element
                medium_part = ""

            # Validate credit name against Credit/Award enums
            found = False
            for en in enum_names:
                if en in _MISSING_ENUM_FILES:
                    found = True
                    break
                records = _load_enum_records(en)
                key_field = ENUM_VALIDATION_KEY.get(en, "")
                upper_credit = credit_part.upper()
                for rec in records.values():
                    if str(rec.get(key_field, "")).upper() == upper_credit:
                        found = True
                        if rec.get("Import-only", "") == "true":
                            warnings.append(
                                f"Field '{field_name}': value '{credit_part}' "
                                f"is import-only in {en}."
                            )
                        break
                if found:
                    break
            if not found:
                errors.append(
                    f"Field '{field_name}': credit '{credit_part}' is not a "
                    f"valid member of {'/'.join(enum_names)}."
                )

            # Validate QSL medium(s) if present (& separates multiple)
            if medium_part:
                mediums = [m.strip() for m in medium_part.split("&")]
                medium_records = _load_enum_records("QSL_Medium")
                medium_key = ENUM_VALIDATION_KEY.get("QSL_Medium", "")
                for med in mediums:
                    med_found = False
                    for rec in medium_records.values():
                        if str(rec.get(medium_key, "")).upper() == med.upper():
                            med_found = True
                            break
                    if not med_found:
                        errors.append(
                            f"Field '{field_name}': QSL medium '{med}' is "
                            f"not a valid QSL_Medium."
                        )
        return errors, warnings

    # Conditional: Submode[MODE] — check submode exists, warn on parent mismatch
    if enum_spec == "Submode":
        records = _load_enum_records("Submode")
        key_field = ENUM_VALIDATION_KEY["Submode"]
        upper_val = value.upper()
        matched_rec = None
        for rec in records.values():
            if str(rec.get(key_field, "")).upper() == upper_val:
                matched_rec = rec
                break
        if matched_rec is None:
            errors.append(
                f"Field '{field_name}': value '{value}' is not a valid Submode."
            )
        else:
            # Check parent mode match
            record_mode = parsed.get("MODE", "")
            parent_mode = str(matched_rec.get("Mode", ""))
            if record_mode and parent_mode:
                if record_mode.upper() != parent_mode.upper():
                    warnings.append(
                        f"Field '{field_name}': submode '{value}' belongs to "
                        f"mode '{parent_mode}', but record MODE is "
                        f"'{record_mode}'."
                    )
        return errors, warnings

    # Simple enumeration lookup
    records = _load_enum_records(enum_spec)
    if not records:
        # File didn't load — skip silently
        return errors, warnings

    key_field = ENUM_VALIDATION_KEY.get(enum_spec, "")
    upper_val = value.upper()

    for rec in records.values():
        if str(rec.get(key_field, "")).upper() == upper_val:
            if rec.get("Import-only", "") == "true":
                warnings.append(
                    f"Field '{field_name}': value '{value}' is import-only "
                    f"in {enum_spec}."
                )
            return errors, warnings

    errors.append(
        f"Field '{field_name}': value '{value}' is not a valid member of "
        f"{enum_spec}."
    )
    return errors, warnings


def _validate_sponsored_award(
    field_name: str, value: str,
) -> Tuple[List[str], List[str]]:
    """Validate Sponsored_Award fields by checking sponsor prefix.

    Format: SPONSOR_AWARDNAME (e.g., ARRL_DXCC). Comma-separated list.
    Validates the sponsor prefix against Award_Sponsor enumeration.
    """
    errors: List[str] = []
    warnings: List[str] = []

    sponsor_records = _load_enum_records("Award_Sponsor")
    sponsor_key = ENUM_VALIDATION_KEY.get("Award_Sponsor", "Sponsor")
    valid_prefixes = {
        str(rec.get(sponsor_key, "")).upper()
        for rec in sponsor_records.values()
    }

    elements = [v.strip() for v in value.split(",") if v.strip()]
    for element in elements:
        # Find matching sponsor prefix (sponsors end with _)
        matched = False
        upper_elem = element.upper()
        for prefix in valid_prefixes:
            if upper_elem.startswith(prefix):
                matched = True
                break
        if not matched:
            warnings.append(
                f"Field '{field_name}': award '{element}' has an "
                f"unrecognized sponsor prefix."
            )

    return errors, warnings


# Cache for DXCC → PAS code reverse map
_dxcc_pas_map: Optional[Dict[str, Set[str]]] = None


def _build_dxcc_pas_map() -> Dict[str, Set[str]]:
    """Build reverse lookup: DXCC entity code → set of valid PAS codes."""
    global _dxcc_pas_map
    if _dxcc_pas_map is not None:
        return _dxcc_pas_map

    records = _load_enum_records("Primary_Administrative_Subdivision")
    result: Dict[str, Set[str]] = {}
    for rec in records.values():
        dxcc_code = str(rec.get("DXCC Entity Code", ""))
        pas_code = str(rec.get("Code", ""))
        if dxcc_code and pas_code:
            if dxcc_code not in result:
                result[dxcc_code] = set()
            result[dxcc_code].add(pas_code.upper())

    _dxcc_pas_map = result
    return result


def _validate_date(field_name: str, value: str) -> List[str]:
    """Validate ADIF Date field: YYYYMMDD, 8 digits, calendar-valid."""
    errors: List[str] = []
    if not re.match(r"^\d{8}$", value):
        errors.append(
            f"Field '{field_name}': date '{value}' must be exactly "
            f"8 digits (YYYYMMDD)."
        )
        return errors

    year = int(value[0:4])
    month = int(value[4:6])
    day = int(value[6:8])
    try:
        datetime.date(year, month, day)
    except ValueError:
        errors.append(
            f"Field '{field_name}': date '{value}' is not a valid "
            f"calendar date."
        )
    return errors


def _validate_time(field_name: str, value: str) -> List[str]:
    """Validate ADIF Time field: HHMM or HHMMSS."""
    errors: List[str] = []
    if not re.match(r"^\d{4}(\d{2})?$", value):
        errors.append(
            f"Field '{field_name}': time '{value}' must be 4 or 6 "
            f"digits (HHMM or HHMMSS)."
        )
        return errors

    hh = int(value[0:2])
    mm = int(value[2:4])
    if hh > 23 or mm > 59:
        errors.append(
            f"Field '{field_name}': time '{value}' has invalid "
            f"hour/minute (HH 00-23, MM 00-59)."
        )
        return errors

    if len(value) == 6:
        ss = int(value[4:6])
        if ss > 59:
            errors.append(
                f"Field '{field_name}': time '{value}' has invalid "
                f"seconds (SS 00-59)."
            )
    return errors


# --- Spec File Loader ---


def get_spec_text(filename: str, version: str = "316") -> str:
    """Retrieve raw text of a 3.1.6 specification JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_dir = os.path.abspath(
        os.path.join(current_dir, "..", "resources", "spec", version)
    )
    name = filename.lower().strip()

    targets = [
        os.path.join(json_dir, f"enumerations_{name}.json"),
        os.path.join(json_dir, f"{name}.json"),
        os.path.join(json_dir, "all.json"),
    ]

    for target_path in targets:
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                continue
    return json.dumps({"error": f"Resource {name} not found in {json_dir}"})


# --- MCP Resources ---


@mcp.resource("adif://system/version")
async def get_system_version() -> str:
    """Provides the current service and ADIF specification versions."""
    return json.dumps(
        {
            "service_version": adif_mcp.__version__,
            "adif_spec_version": adif_mcp.__adif_spec__,
            "status": "online",
        }
    )


# --- Internal Logic ---


def parse_adif_internal(text: str) -> Dict[str, str]:
    """Surgically extracts ADIF tags and their data by length."""
    tag_pattern = re.compile(
        r"<(?P<name>[^:>]+):(?P<len>\d+)(?::(?P<type>[^>]+))?>", re.IGNORECASE
    )
    results: Dict[str, str] = {}

    for match in tag_pattern.finditer(text):
        name = match.group("name").upper()
        length = int(match.group("len"))
        start_of_data = match.end()
        data = text[start_of_data : start_of_data + length]
        results[name] = data

    return results


# --- Core Tools ---


@mcp.tool()
def get_version_info() -> Dict[str, Any]:
    """Returns the version of the ADIF-MCP server and spec."""
    return {
        "service_version": adif_mcp.__version__,
        "adif_spec_version": adif_mcp.__adif_spec__,
    }


@mcp.tool()
def calculate_distance(start: str, end: str) -> float:
    """Calculates distance (km) between Maidenhead locators."""
    return calculate_distance_impl(start, end)


@mcp.tool()
def calculate_heading(start: str, end: str) -> float:
    """Calculates heading (azimuth) between Maidenhead locators."""
    return calculate_heading_impl(start, end)


@mcp.tool()
async def parse_adif(
    file_path: str, start_at: int | None = 1, limit: int | None = 20
) -> List[types.TextContent]:
    """Streaming parser for large ADIF files with record seeking.

    SECURITY NOTE: This tool reads files from the local filesystem using
    the provided path. Only pass paths to ADIF log files you own.
    """
    start_at = start_at if start_at is not None else 1
    limit = limit if limit is not None else 20
    record_pattern = re.compile(r"(.*?)<EOR>", re.IGNORECASE | re.DOTALL)

    try:
        if not os.path.exists(file_path):
            err_msg = f"ERROR: File not found at {file_path}"
            return [types.TextContent(type="text", text=err_msg)]

        async with aiofiles.open(file_path, mode="r") as f:
            content = await f.read()
            matches = list(record_pattern.finditer(content))
            total_count = len(matches)

            start_idx = max(0, start_at - 1)
            end_idx = start_idx + limit
            requested = matches[start_idx:end_idx]

            output_text = f"FILE: {file_path}\nTOTAL RECORDS: {total_count}\n"
            current_max = min(start_at + len(requested) - 1, total_count)
            output_text += f"DISPLAYING: {start_at} to {current_max}\n\n"

            for i, match in enumerate(requested):
                current_num = start_at + i
                output_text += f"--- RECORD {current_num} ---\n"
                output_text += f"{match.group(0).strip()}\n\n"

            return [types.TextContent(type="text", text=output_text)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"STREAM ERROR: {str(e)}")]


@mcp.tool()
def read_specification_resource(resource_name: str) -> str:
    """Reads an ADIF 3.1.6 specification resource (e.g., 'mode')."""
    return get_spec_text(resource_name)


@mcp.tool()
def list_enumerations() -> Dict[str, Any]:
    """Lists all 25 ADIF 3.1.6 enumerations with record counts and fields."""
    result: Dict[str, Any] = {}
    for enum_name, fields in ENUMERATION_FIELDS.items():
        records = _load_enum_records(enum_name)
        import_only_count = sum(
            1 for rec in records.values()
            if rec.get("Import-only", "") == "true"
        )
        result[enum_name] = {
            "record_count": len(records),
            "import_only_count": import_only_count,
            "searchable_fields": fields,
        }
    return {"enumeration_count": len(result), "enumerations": result}


@mcp.tool()
def search_enumerations(
    search_term: str,
    enumeration: Optional[str] = None,
) -> Dict[str, Any]:
    """Searches ADIF 3.1.6 enumerations. Optionally filter by enumeration name."""
    term = search_term.upper().strip()
    if not term:
        return {"error": "Search term must not be empty."}

    # Determine which enumerations to search
    if enumeration:
        # Case-insensitive match against known enum names
        matched_enum = None
        for name in ENUMERATION_FIELDS:
            if name.upper() == enumeration.upper().strip():
                matched_enum = name
                break
        if not matched_enum:
            return {
                "error": f"Unknown enumeration '{enumeration}'. Use "
                f"list_enumerations to see valid names.",
            }
        enums_to_search = {matched_enum: ENUMERATION_FIELDS[matched_enum]}
    else:
        enums_to_search = ENUMERATION_FIELDS

    all_results: Dict[str, Any] = {}

    for enum_name, search_fields in enums_to_search.items():
        records = _load_enum_records(enum_name)
        matches: Dict[str, Any] = {}

        for rec_id, rec in records.items():
            for field in search_fields:
                field_val = str(rec.get(field, "")).upper()
                if term in field_val:
                    matches[rec_id] = rec
                    break

        if matches:
            all_results[enum_name] = {
                "match_count": len(matches),
                "records": matches,
            }

    if not all_results:
        return {"message": f"'{search_term}' not found in any enumeration."}

    return {
        "search_term": search_term,
        "enumerations_matched": len(all_results),
        "results": all_results,
    }


@mcp.tool()
def validate_adif_record(adif_string: str) -> Dict[str, Any]:
    """Validates an ADIF record against 3.1.6 rules including enum membership."""
    parsed = parse_adif_internal(adif_string)

    try:
        raw_fields = get_spec_text("fields")
        fields_spec = json.loads(raw_fields)["Adif"]["Fields"]["Records"]
    except Exception as e:
        return {"status": "error", "message": f"Could not load spec: {str(e)}"}

    report: Dict[str, Any] = {
        "status": "success",
        "errors": [],
        "warnings": [],
        "record": parsed,
    }

    for field_name, value in parsed.items():
        upper_field = field_name.upper()

        if upper_field not in fields_spec:
            msg = f"Field '{upper_field}' is not in spec."
            report["warnings"].append(msg)
            continue

        spec_info = fields_spec[upper_field]
        data_type = spec_info.get("Data Type")

        # Number/Integer/PositiveInteger validation + bounds
        if data_type in ("Number", "Integer", "PositiveInteger"):
            stripped = str(value).strip()
            if data_type == "Number":
                valid_fmt = bool(re.match(r"^-?\d*\.?\d+$", stripped))
            elif data_type == "Integer":
                valid_fmt = bool(re.match(r"^-?\d+$", stripped))
            else:  # PositiveInteger
                valid_fmt = bool(re.match(r"^\d+$", stripped))

            if not valid_fmt:
                msg = (
                    f"Field '{upper_field}' expects {data_type}, "
                    f"got '{value}'."
                )
                report["errors"].append(msg)
                report["status"] = "invalid"
            else:
                # Bounds checking from fields.json
                num_val = float(stripped)
                min_val = spec_info.get("Minimum Value")
                max_val = spec_info.get("Maximum Value")
                if min_val is not None:
                    if num_val < float(min_val):
                        report["errors"].append(
                            f"Field '{upper_field}': value {stripped} "
                            f"is below minimum {min_val}."
                        )
                        report["status"] = "invalid"
                if max_val is not None:
                    if num_val > float(max_val):
                        report["errors"].append(
                            f"Field '{upper_field}': value {stripped} "
                            f"is above maximum {max_val}."
                        )
                        report["status"] = "invalid"

        # Date validation
        if data_type == "Date":
            date_errors = _validate_date(upper_field, str(value).strip())
            report["errors"].extend(date_errors)
            if date_errors:
                report["status"] = "invalid"

        # Time validation
        if data_type == "Time":
            time_errors = _validate_time(upper_field, str(value).strip())
            report["errors"].extend(time_errors)
            if time_errors:
                report["status"] = "invalid"

        # Enumeration validation
        enum_spec_str = FIELD_ENUM_MAP.get(upper_field)
        if enum_spec_str:
            if not value.strip():
                report["errors"].append(
                    f"Field '{upper_field}': value is empty."
                )
                report["status"] = "invalid"
            elif upper_field not in _INCOMPLETE_ENUM_FIELDS:
                errs, warns = _validate_enum_field(
                    upper_field, value.strip(), enum_spec_str, parsed
                )
                report["errors"].extend(errs)
                report["warnings"].extend(warns)
                if errs:
                    report["status"] = "invalid"

    # DXCC cross-validation: STATE must be valid for DXCC entity
    _cross_validate_dxcc_state(parsed, report, "STATE", "DXCC")
    _cross_validate_dxcc_state(parsed, report, "MY_STATE", "MY_DXCC")

    return report


def _cross_validate_dxcc_state(
    parsed: Dict[str, str],
    report: Dict[str, Any],
    state_field: str,
    dxcc_field: str,
) -> None:
    """Cross-validate STATE against DXCC — warn if STATE is invalid for DXCC."""
    state_val = parsed.get(state_field, "").strip()
    dxcc_val = parsed.get(dxcc_field, "").strip()

    if not state_val or not dxcc_val:
        return

    dxcc_pas = _build_dxcc_pas_map()
    valid_codes = dxcc_pas.get(dxcc_val)

    if valid_codes is None:
        # No PAS data for this DXCC — skip
        return

    if state_val.upper() not in valid_codes:
        report["warnings"].append(
            f"Field '{state_field}': value '{state_val}' is not a valid "
            f"subdivision for {dxcc_field}={dxcc_val}."
        )


# --- Entry Points ---


def run() -> None:
    """Entry point for the server."""
    mcp.run()


def main() -> None:
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()
