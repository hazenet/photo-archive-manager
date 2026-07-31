#!/usr/bin/env python3

"""Rename photo files in a selected folder."""

from pathlib import Path

from photo_archive_manager.models import RenameSession

from photo_archive_manager.core.discovery import (
    find_supported_files,
    split_files_by_rename_status,
)
from photo_archive_manager.core.exif import read_capture_datetimes
from photo_archive_manager.core.filesystem import rename_files
from photo_archive_manager.core.planning_rename import (
    assign_sequence_numbers,
    generate_new_filenames,
    group_files_by_timestamp,
)
from photo_archive_manager.core.validation import validate_renames


def rename_folder(
    folder: Path,
    session: ExecutionSession,
) -> ExecutionSession:
    """Rename files in a specified folder"""

    photo_files = find_supported_files(folder)

    already_renamed, needs_rename = split_files_by_rename_status(photo_files)

    session.discovered_files = photo_files
    session.already_renamed_files = already_renamed
    session.skipped_files.extend(already_renamed)

    if not needs_rename:
        return session

    read_capture_datetimes(needs_rename)

    grouped = group_files_by_timestamp(needs_rename)

    assign_sequence_numbers(grouped)

    generate_new_filenames(needs_rename)

    session.validation_issues = validate_renames(needs_rename)

    if session.validation_issues:
        return session

    rename_files(needs_rename)

    session.renamed_files.extend(needs_rename)

    return session