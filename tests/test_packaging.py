"""Conventions that drift unless a test holds them.

Adapted from qso-graph-sim's copy (Bob, qso-graph-sim#2) with one change the
fleet needs: `cmd.startswith(f"{name}-")` alone rejects second commands that
are legitimate — `ionis-download` in ionis-mcp, `qsp-adif-convert` in
qsp-client. See the stem rule below.

This exists because of qso-graph-auth#28: that package installed as
`qso-graph-auth` and ran as `qso-auth`, so you had to open the README to find
out what to type. It was a convention nobody asserted, which is exactly the
kind that drifts.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

# Commands kept only so existing scripts and notes keep working. Each must
# print where it went and be removed in a later release. Listing them here
# rather than widening the rule keeps every exception visible and reviewable.
DEPRECATED: set[str] = set()


def _project() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]


def test_the_primary_command_is_the_package_name() -> None:
    """`uv tool install <pkg>` must give you a command called `<pkg>`."""
    p = _project()
    name, scripts = p["name"], p.get("scripts", {})
    assert name in scripts, f"{name} installs no command called {name}"


def test_extra_commands_carry_the_package_name_or_its_stem() -> None:
    """A second command is fine; an unrelated name is not.

    The stem is the package name with its role suffix removed, so ionis-mcp may
    ship `ionis-download` and qsp-client may ship `qsp-adif-convert`. It is NOT
    the first segment: `qso-graph-auth`.split("-")[0] is "qso", which would let
    `qso-auth` pass — precisely the defect this file exists to prevent.
    """
    p = _project()
    name, scripts = p["name"], p.get("scripts", {})
    stem = re.sub(r"-(mcp|client|auth|sim)$", "", name)
    for cmd in scripts:
        if cmd in DEPRECATED:
            continue
        assert cmd == name or cmd.startswith(f"{name}-") or cmd.startswith(f"{stem}-"), (
            f"{cmd} is neither {name} nor prefixed with {name}- or {stem}-"
        )


def test_each_deprecated_alias_is_declared_and_distinct() -> None:
    """An alias must point somewhere else, or it cannot print the notice.

    Skipped rather than passed when there are no aliases: a green tick for an
    empty loop reads as "checked" when nothing was.
    """
    if not DEPRECATED:
        pytest.skip("no deprecated aliases declared in this package")
    p = _project()
    scripts = p.get("scripts", {})
    primary = scripts[p["name"]]
    for alias in DEPRECATED:
        assert alias in scripts, f"{alias} is listed as deprecated but not declared"
        assert scripts[alias] != primary, (
            f"{alias} points at the same entry point as {p['name']}, so it cannot "
            f"warn that it is deprecated"
        )


def test_the_stem_rule_would_still_reject_the_original_defect() -> None:
    """The guard is only worth having if it fails on what it was written for.

    Asserted rather than trusted, and it runs in every repo so the rule itself
    is exercised even where the package declares one command.
    """
    name = "qso-graph-auth"
    stem = re.sub(r"-(mcp|client|auth|sim)$", "", name)
    cmd = "qso-auth"
    assert not (cmd == name or cmd.startswith(f"{name}-") or cmd.startswith(f"{stem}-")), (
        "the stem rule accepts qso-auth for qso-graph-auth; it has the same hole "
        "as name.split('-')[0]"
    )
