"""Command-line interface entry point for Photo Archive Manager."""

import argparse

from photo_archive_manager.commands.rename import rename


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
        "rename", help="Rename supported photo and video files."
    )

    rename_parser.add_argument(
        "folder",
        nargs="?",
        metavar="FOLDER",
        help="Folder containing the files to rename. If omitted, a folder picker is shown.",
    )

    rename_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without modifying any files.",
    )

    rename_parser.add_argument(
        "--show-results",
        action="store_true",
        help="Show the result for every processed file.",
    )

    rename_parser.set_defaults(
        func=rename,
    )

    return parser


def main() -> int:
    """Run the command-line interface."""

    parser = build_parser()
    args = parser.parse_args()

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
