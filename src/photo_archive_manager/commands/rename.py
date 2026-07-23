#!/usr/bin/env python3

from ..core.dependencies import check_dependencies
from ..core.discovery import (
    discover_photo_files,
    split_files_by_rename_status,
)
from ..core.exif import read_capture_datetimes
from ..core.filesystem import rename_files
from ..core.planning import (
    assign_sequence_numbers,
    generate_new_filenames,
    group_files_by_timestamp,
)
from ..core.validation import validate_renames
from ..utils.dialogs import choose_folder


def run() -> int:
    """Run the rename command."""

    check_dependencies()

    folder = choose_folder()
    if folder is None:
        return 1

    photo_files = discover_photo_files(folder)

    already_renamed, needs_rename = split_files_by_rename_status(photo_files)

    if not needs_rename:
        print("No files require renaming.")
        return 0

    read_capture_datetimes(needs_rename)

    grouped = group_files_by_timestamp(needs_rename)

    assign_sequence_numbers(grouped)

    generate_new_filenames(needs_rename)

    issues = validate_renames(needs_rename)

    if issues:
        ...
        return 1

    ...

    rename_files(needs_rename)

    return 0