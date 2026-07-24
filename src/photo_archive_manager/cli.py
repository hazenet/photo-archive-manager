#!/usr/bin/env python3

"""Command-line interface entry point for Photo Archive Manager."""

from __future__ import annotations

import argparse

from .commands.rename import rename


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="pam",
        description="Photo Archive Manager",
        epilog="Use 'pam <command> --help' for more information.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    rename_parser = subparsers.add_parser(
        "rename",
        help="Rename photo files.",
    )
    rename_parser.set_defaults(func=rename)

    return parser


def main() -> int:
    """Run the command-line interface."""

    parser = build_parser()
    args = parser.parse_args()

    return args.func()


if __name__ == "__main__":
    raise SystemExit(main())