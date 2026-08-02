"""Rename photo files in a selected folder."""

import argparse
from pathlib import Path

from photo_archive_manager.core.dependencies import check_dependencies
from photo_archive_manager.services.renamer import rename_folder
from photo_archive_manager.utils.dialogs import choose_folder
from photo_archive_manager.utils.reporting import print_rename_session


def rename(args: argparse.Namespace) -> int:
    """Run the rename command."""

    check_dependencies()

    if args.folder is None:
        folder = choose_folder()

        if folder is None:
            return 1

    else:
        folder = Path(args.folder)

    folder = folder.expanduser().resolve()

    if not folder.exists():
        print(f"Error: '{folder}' does not exist.")
        return 1

    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory.")
        return 1

    session = rename_folder(
        folder,
        dry_run=args.dry_run,
    )

    print_rename_session(
        session,
        show_results=args.show_results,
    )

    if session.validation_issues:
        return 1

    return 0
