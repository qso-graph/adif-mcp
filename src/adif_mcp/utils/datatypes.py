"""ADIF's structured data types, checked as ADIF 3.1.7 defines them (#47).

One function per data type, each quoting the sentence of the specification it
enforces, and a table from the type's name to its function. A value that breaks
the stated grammar is an error. Something the grammar allows but that cannot be
right (a latitude over 90 degrees, a hemisphere letter on the wrong axis) is a
warning: reported, never rejected, because the specification does not say so
and this package does not add rules of its own.

Every check is case-insensitive where ADIF says the type is.
"""

from __future__ import annotations

import re
from typing import Callable, Dict, List, Tuple

Result = Tuple[List[str], List[str]]  # (errors, warnings)

# The Maidenhead system ADIF's GridSquare names: pairs of letters A-R (field),
# digits 0-9 (square), letters A-X (subsquare), digits 0-9 (extended square).
_MAIDENHEAD = re.compile(r"^[A-R]{2}(?:[0-9]{2}(?:[A-X]{2}(?:[0-9]{2})?)?)?$", re.IGNORECASE)


def is_maidenhead(value: str) -> bool:
    """A 2, 4, 6 or 8 character Maidenhead locator, in any case."""
    return bool(_MAIDENHEAD.match(value))


def grid_square(field: str, value: str) -> Result:
    """GridSquare: "a case-insensitive 2-character, 4-character, 6-character, or
    8-character Maidenhead locator"."""
    if is_maidenhead(value):
        return [], []
    return [
        f"Field '{field}': '{value}' is not a 2, 4, 6 or 8 character Maidenhead locator."
    ], []


def grid_square_ext(field: str, value: str) -> Result:
    """GridSquareExt: characters 9 and 10 (and 11 and 12) of a 10 or 12 character
    locator. "Characters 9 and 10 are case-insensitive ASCII letters in the range
    A-X. Characters 11 and 12 are Digits in the range 0-9.\""""
    if re.match(r"^[A-X]{2}(?:[0-9]{2})?$", value, re.IGNORECASE):
        return [], []
    return [
        f"Field '{field}': '{value}' is not characters 9-10 (A-X) or 9-12 "
        "(A-X, then 0-9) of a locator."
    ], []


def grid_square_list(field: str, value: str) -> Result:
    """GridSquareList: "a comma-delimited list of GridSquare items". VUCC_GRIDS and
    MY_VUCC_GRIDS narrow it: "two or four adjacent Maidenhead grid locators, each
    four or six characters long". Adjacency is not checked."""
    items = value.split(",")
    errors = [
        f"Field '{field}': '{item}' is not a Maidenhead locator."
        for item in items
        if not is_maidenhead(item)
    ]
    if errors:
        return errors, []
    if field in ("VUCC_GRIDS", "MY_VUCC_GRIDS"):
        if len(items) not in (2, 4):
            errors.append(
                f"Field '{field}': ADIF requires two or four locators; got {len(items)}."
            )
        bad = [item for item in items if len(item) not in (4, 6)]
        if bad:
            errors.append(
                f"Field '{field}': each locator must be four or six characters; "
                f"not {', '.join(bad)}."
            )
    return errors, []


_LOCATION = re.compile(r"^([EWNS])(\d{3}) (\d{2}\.\d{3})$", re.IGNORECASE)


def location(field: str, value: str) -> Result:
    """Location: "a sequence of 11 characters ... in XDDD MM.MMM format, where X is
    a directional Character from the set {E, W, N, S}, DDD is a 3-Digit degrees
    specifier, where 0 <= DDD <= 180 ... a single space character in between DDD
    and MM.MMM ... where 00.000 <= MM.MMM <= 59.999"."""
    match = _LOCATION.match(value)
    if not match:
        return [
            f"Field '{field}': '{value}' is not XDDD MM.MMM (e.g. N043 30.000), "
            "as ADIF's Location requires."
        ], []
    letter, degrees, minutes = (
        match.group(1).upper(),
        int(match.group(2)),
        float(match.group(3)),
    )
    errors: List[str] = []
    if degrees > 180:
        errors.append(f"Field '{field}': degrees {degrees:03d} is above 180.")
    if minutes > 59.999:
        errors.append(f"Field '{field}': minutes {match.group(3)} is above 59.999.")
    if errors:
        return errors, []
    # Allowed by the type, which serves latitude and longitude alike, but not right.
    warnings: List[str] = []
    latitude = field.endswith("LAT")
    if latitude and letter in "EW":
        warnings.append(
            f"Field '{field}': '{letter}' is a longitude direction; a latitude is N or S."
        )
    if not latitude and letter in "NS":
        warnings.append(
            f"Field '{field}': '{letter}' is a latitude direction; a longitude is E or W."
        )
    if latitude and degrees > 90:
        warnings.append(
            f"Field '{field}': a latitude of {degrees} degrees is not on the Earth."
        )
    return [], warnings


def boolean(field: str, value: str) -> Result:
    """Boolean: "if True, the single ASCII character Y or y; if False, the single
    ASCII character N or n"."""
    if value in ("Y", "y", "N", "n"):
        return [], []
    return [f"Field '{field}': '{value}' is not Y or N."], []


def iota_ref(continents: Callable[[], set[str]]) -> Callable[[str, str], Result]:
    """IOTARefNo: "format CC-XXX, where CC is a member of the Continent enumeration,
    XXX is the island group designator, where 1 <= XXX <= 999 [use leading zeroes]"."""

    def check(field: str, value: str) -> Result:
        match = re.match(r"^([A-Z]{2})-(\d{3})$", value, re.IGNORECASE)
        if not match:
            return [f"Field '{field}': '{value}' is not CC-XXX (e.g. NA-001)."], []
        errors: List[str] = []
        if match.group(1).upper() not in continents():
            errors.append(f"Field '{field}': '{match.group(1)}' is not an ADIF Continent.")
        if int(match.group(2)) < 1:
            errors.append(f"Field '{field}': the island group number must be 001 to 999.")
        return errors, []

    return check


def wwff_ref(field: str, value: str) -> Result:
    """WWFFRef: "case-insensitive Characters ... in the form xxFF-nnnn comprising 8
    to 11 characters where xx is the WWFF national program and is 1 to 4 characters
    ... nnnn ... is 4 characters in length with leading zeros"."""
    if re.match(r"^[A-Z0-9]{1,4}FF-\d{4}$", value, re.IGNORECASE):
        return [], []
    return [
        f"Field '{field}': '{value}' is not a WWFF reference xxFF-nnnn (e.g. KFF-4655)."
    ], []


_POTA_REF = re.compile(r"^[A-Z0-9]{1,4}-[0-9]{4,5}(?:@[A-Z0-9-]{4,6})?$", re.IGNORECASE)


def pota_ref_list(field: str, value: str) -> Result:
    """POTARefList: "a comma-delimited list of one or more POTARef items". POTARef:
    "xxxx-nnnnn[@yyyyyy] comprising 6 to 17 characters where xxxx ... is 1 to 4
    characters ... nnnnn ... is either 4 or 5 characters ... yyyyyy Optional is the
    4 to 6 character ISO 3166-2 code"."""
    bad = [
        item
        for item in value.split(",")
        if not _POTA_REF.match(item) or not 6 <= len(item) <= 17
    ]
    if bad:
        return [
            f"Field '{field}': not a POTA reference xxxx-nnnnn[@yyyyyy]: {', '.join(bad)}."
        ], []
    return [], []


def sota_ref(field: str, value: str) -> Result:
    """SOTARef: "an ITU prefix if applicable, a SOTA subdivision, a / Character, a
    SOTA Reference Number" (e.g. W2/WE-003). ADIF states only that structure, so
    only it is checked: one /, with something on each side."""
    parts = value.split("/")
    if len(parts) == 2 and all(part.strip() for part in parts):
        return [], []
    return [
        f"Field '{field}': '{value}' is not a SOTA reference "
        "(association/reference, e.g. W2/WE-003)."
    ], []


def table(continents: Callable[[], set[str]]) -> Dict[str, Callable[[str, str], Result]]:
    """Data Type name, as fields.json gives it, to its check."""
    return {
        "GridSquare": grid_square,
        "GridSquareExt": grid_square_ext,
        "GridSquareList": grid_square_list,
        "Location": location,
        "Boolean": boolean,
        "IOTARefNo": iota_ref(continents),
        "WWFFRef": wwff_ref,
        "POTARefList": pota_ref_list,
        "SOTARef": sota_ref,
    }
