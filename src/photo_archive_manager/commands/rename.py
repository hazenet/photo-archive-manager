#!/usr/bin/env python3

"""Rename photo files in a selected folder."""

from ..core.dependencies import check_dependencies
from ..core.discovery import (
    find_supported_files,
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
from ..utils.reporting import (
    print_completion_summary,
    print_discovery_summary,
    print_rename_preview,
    print_validation_issues,
)


def rename() -> int:
    """Run the rename command."""

    check_dependencies()

    folder = choose_folder()
    if folder is None:
        return 1

    photo_files = find_supported_files(folder)

    already_renamed, needs_rename = split_files_by_rename_status(photo_files)

    print_discovery_summary(
        total_files=len(photo_files),
        already_renamed=len(already_renamed),
        needs_rename=len(needs_rename),
    )

    if not needs_rename:
        return 0

    read_capture_datetimes(needs_rename)

    grouped = group_files_by_timestamp(needs_rename)

    assign_sequence_numbers(grouped)

    generate_new_filenames(needs_rename)

    issues = validate_renames(needs_rename)

    if issues:
        print_validation_issues(issues)
        return 1

    print_rename_preview(needs_rename)

    rename_files(needs_rename)

    print_completion_summary(
        total_files=len(photo_files),
        already_renamed=len(already_renamed),
        renamed=len(needs_rename),
    )

    return 0