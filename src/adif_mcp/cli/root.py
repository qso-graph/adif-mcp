"""Root CLI wiring for adif-mcp.

Builds the top-level argument parser and registers all subcommands.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import sys
from typing import Callable, Protocol, cast

from . import convert_adi, validate


class _RegisterCLI(Protocol):
    """Protocol for subcommand registration functions."""

    def __call__(self, sp: argparse._SubParsersAction[argparse.ArgumentParser]) -> None: ...


# ------------------------ parser ------------------------


def build_parser() -> argparse.ArgumentParser:
    """Create and return the root argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="adif-mcp", description="adif-mcp CLI")

    # Dynamic versioning from metadata
    try:
        ver = importlib.metadata.version("adif-mcp")
    except importlib.metadata.PackageNotFoundError:
        ver = "0.0.0-dev"
    parser.add_argument("--version", action="version", version=f"%(prog)s {ver}")

    subparsers: argparse._SubParsersAction[argparse.ArgumentParser] = parser.add_subparsers(
        dest="command"
    )

    # convert + alias
    p_conv = subparsers.add_parser(
        "convert",
        help="Convert ADIF to JSON/NDJSON",
        description="Convert ADIF (.adi) to QsoRecord JSON/NDJSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    convert_adi.add_convert_args(p_conv)
    p_conv.set_defaults(func=lambda _args: convert_adi.main(sys.argv[2:]))

    p_conv_alias = subparsers.add_parser(
        "convert-adi",
        help="(alias) Convert ADIF to JSON/NDJSON",
        description="Convert ADIF (.adi) to QsoRecord JSON/NDJSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    convert_adi.add_convert_args(p_conv_alias)
    p_conv_alias.set_defaults(func=lambda _args: convert_adi.main(sys.argv[2:]))

    if hasattr(validate, "register_cli"):
        cast(_RegisterCLI, getattr(validate, "register_cli"))(subparsers)

    # --------------------------------------------------------
    # MCP Gateway Subcommand
    # --------------------------------------------------------
    p_mcp = subparsers.add_parser(
        "mcp",
        help="Start the MCP server gateway for AI integration",
        description="Starts the Stdio-based MCP server for use with Cline, Claude, etc.",
    )

    def handle_mcp(_args: argparse.Namespace) -> int:
        """Entry point for AI agents to start the MCP server."""
        try:
            from adif_mcp.mcp.server import run as run_mcp

            run_mcp()
            return 0
        except ImportError as e:
            print(f"Error: MCP server module not found in the package: {e}")
            return 1

    p_mcp.set_defaults(func=handle_mcp)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the adif-mcp CLI."""
    args_in = sys.argv[1:] if argv is None else argv
    parser = build_parser()

    # Default to MCP server if no subcommand was provided
    if not args_in:
        from adif_mcp.mcp.server import run as run_mcp

        run_mcp()
        return 0

    args = parser.parse_args(args_in)
    func = cast(Callable[[argparse.Namespace], int] | None, getattr(args, "func", None))
    if func is not None:
        return func(args)

    parser.print_help()
    return 2
