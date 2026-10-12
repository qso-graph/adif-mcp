"""CLI smoke tests for `adif-mcp`."""

# tests/test_cli_test.py
from cli_test_helpers import shell


def test_entrypoint_help() -> None:
    """Test the help message for the main entry point."""
    r = shell("adif-mcp --help")
    assert r.exit_code == 0
    assert "adif-mcp CLI" in r.stdout


def test_convert_help() -> None:
    """Test the help message for the convert command."""
    r1 = shell("adif-mcp convert --help")
    r2 = shell("adif-mcp convert-adi --help")
    assert r1.exit_code == 0
    assert r2.exit_code == 0
