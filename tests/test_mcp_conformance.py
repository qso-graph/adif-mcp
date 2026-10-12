"""Conformance with the Model Context Protocol, revision 2026-07-28.

Nothing in this project's documents required this until 2026-10-11 — not
CLAUDE.md, not .claude/rules/security.md, not MCP-SECURITY-FRAMEWORK.md, not
qso-graph-spec. We documented how to *publish* an MCP server in detail and
never wrote down what makes one *valid*, which is how a missing ``isError``
and missing annotations reached all 22 servers in the fleet unnoticed.

So these are asserted rather than trusted. ``get_version_info`` is the cautionary
case: it was a convention nobody tested, and it drifted — 13 servers return
``{service_name, service_version, spec_version}`` while this one dropped
``service_name`` and renamed the third field.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp.exceptions import ToolError

from adif_mcp.mcp import server

ANNOTATION_HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")


def _tools() -> dict[str, object]:
    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


class TestToolAnnotations:
    def test_every_tool_declares_all_four_hints(self) -> None:
        """ADIF-C01: the defaults are pessimistic, so silence is the wrong answer.

        Omitting them advertises a read-only tool as ``destructiveHint: true``
        and ``openWorldHint: true``, and the specification tells clients to keep
        a human in the loop for operations like that — so a client may
        reasonably put a confirmation prompt in front of reading a spec table.
        """
        for name, tool in _tools().items():
            ann = getattr(tool, "annotations", None)
            assert ann is not None, f"{name} declares no annotations"
            # Asserted on the serialised form, not the Python attributes. The
            # SDK renamed its fields to snake_case; the protocol did not, and
            # it is the wire the client reads.
            wire = ann.model_dump(by_alias=True, exclude_none=True)
            for hint in ANNOTATION_HINTS:
                assert hint in wire, f"{name} omits {hint} on the wire; got {sorted(wire)}"

    def test_the_hints_say_what_this_server_actually_is(self) -> None:
        """ADIF-C02: every tool here reads; none writes, and none leaves the host.

        After the 2026-10-11 cleanup there is no outbound HTTP and no
        credential access anywhere in ``src/``, so ``openWorldHint`` is false
        for all of them. If that ever stops being true, this test is where it
        should be noticed.
        """
        for name, tool in _tools().items():
            wire = tool.annotations.model_dump(  # type: ignore[attr-defined]
                by_alias=True, exclude_none=True
            )
            assert wire["readOnlyHint"] is True, name
            assert wire["destructiveHint"] is False, name
            assert wire["idempotentHint"] is True, name
            assert wire["openWorldHint"] is False, name

    def test_the_server_really_has_no_outbound_network(self) -> None:
        """ADIF-C03: the control for openWorldHint being false.

        A claim in an annotation is worth what the code behind it is worth.
        """
        import pathlib
        import re

        src = pathlib.Path(server.__file__).parent.parent
        outbound = re.compile(
            r"urllib\.request\.(urlopen|Request)|httpx\.|requests\.(get|post)"
        )
        offenders = []
        for path in src.rglob("*.py"):
            if outbound.search(path.read_text(encoding="utf-8", errors="replace")):
                offenders.append(path.name)
        assert not offenders, f"outbound HTTP found in {offenders}"


class TestToolErrorsAreFlagged:
    """A tool execution error belongs in the result with ``isError: true``.

    The specification states the cost of getting this wrong: otherwise "the LLM
    would not be able to see that an error occurred and self-correct".
    """

    def test_an_unknown_enumeration_raises(self) -> None:
        """ADIF-C10: input the caller can fix."""
        with pytest.raises(ToolError):
            server.search_enumerations("CW", enumeration="NoSuchEnum")

    def test_an_empty_search_term_raises(self) -> None:
        """ADIF-C11."""
        with pytest.raises(ToolError):
            server.search_enumerations("   ")

    def test_an_unknown_spec_resource_raises_and_names_the_choices(self) -> None:
        """ADIF-C12: refused, and the message tells the model what to try.

        Issue #9: an unknown name must never fall back to returning the whole
        of all.json. It returns an error naming the valid resources, and that
        error now reaches the client as a failure rather than as content.
        """
        with pytest.raises(ToolError) as caught:
            server.read_specification_resource("nosuchresource")
        message = str(caught.value)
        assert "mode" in message and "all" in message

    def test_a_path_traversal_attempt_raises(self) -> None:
        """ADIF-C13: and the message carries nothing from outside the spec dir."""
        for probe in ("../fields", "/etc/passwd", "all/../fields"):
            with pytest.raises(ToolError) as caught:
                server.read_specification_resource(probe)
            assert "secret" not in str(caught.value).lower()

    def test_a_valid_resource_still_returns_content(self) -> None:
        """ADIF-C14: the control — the above is not refusing everything."""
        assert '"Version"' in server.read_specification_resource("all")


class TestAVerdictIsNotAnError:
    """The distinction the specification draws, and the easy one to get wrong."""

    def test_an_invalid_record_is_a_successful_call(self) -> None:
        """ADIF-C20: "this record is invalid" is an answer, not a failure.

        Conflating the two would make every rejected record look like a broken
        tool, and a model would retry instead of reporting the verdict. Only the
        tool failing — a specification that will not load — is an error.
        """
        answer = server.validate_adif_record(
            "<CALL:4>K1JT<BAND:5>99cm<MODE:7>NOTAMOD<EOR>"
        )
        assert isinstance(answer, dict)
        assert answer["status"] == "invalid"
        assert answer["errors"]

    def test_a_valid_record_is_also_a_successful_call(self) -> None:
        """ADIF-C21."""
        answer = server.validate_adif_record(
            "<CALL:4>K1JT<BAND:2>6M<MODE:6>MSK144<QSO_DATE:8>20260812<EOR>"
        )
        assert answer["status"] == "success"
        assert not answer["errors"]


class TestVersionInfoShape:
    def test_it_matches_the_shape_the_fleet_returns(self) -> None:
        """ADIF-C30: the drift this repo was the only one to have.

        Thirteen servers return ``{service_name, service_version,
        spec_version}``. This one omitted ``service_name`` altogether and called
        the third field ``adif_spec_version``, so a caller reading
        ``service_name`` across the fleet got a KeyError on the server
        everything else depends on.
        """
        info = server.get_version_info()
        assert info["service_name"] == "adif-mcp"
        assert info["service_version"]
        assert info["spec_version"]

    def test_the_old_key_is_kept_so_nothing_breaks(self) -> None:
        """ADIF-C31: additive, not a rename.

        Callers of 1.2.3 and earlier read ``adif_spec_version``. Removing it to
        tidy the shape would break them for no benefit.
        """
        info = server.get_version_info()
        assert info["adif_spec_version"] == info["spec_version"]


class TestRegistration:
    def test_the_eight_tools_a_client_sees(self) -> None:
        """ADIF-C40: calling a function directly is not proof a client can."""
        assert set(_tools()) == {
            "get_version_info",
            "calculate_distance",
            "calculate_heading",
            "parse_adif",
            "read_specification_resource",
            "list_enumerations",
            "search_enumerations",
            "validate_adif_record",
        }
