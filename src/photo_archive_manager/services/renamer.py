"""Rename photo files in a selected folder."""

from datetime import datetime
from pathlib import Path

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
from photo_archive_manager.core.validation_rename import validate_renames
from photo_archive_manager.models import RenameSession


def rename_folder(
    folder: Path,
    *,
    dry_run: bool = False,
) -> RenameSession:
    """Rename all supported files within a single folder."""

    session = RenameSession(
        folder=folder,
        dry_run=dry_run,
        started_at=datetime.now(),
    )

    #
    # Discovery
    #

    photo_files = find_supported_files(folder)

    already_renamed, needs_rename = split_files_by_rename_status(photo_files)

    #
    # Nothing to do
    #

    if not needs_rename:
        session.ended_at = datetime.now()
        return session

    #
    # Metadata
    #

    read_capture_datetimes(needs_rename)

    #
    # Planning
    #

    grouped = group_files_by_timestamp(needs_rename)

    assign_sequence_numbers(grouped)

    generate_new_filenames(needs_rename)

    #
    # Validation
    #

    session.validation_issues = validate_renames(needs_rename)

    if session.validation_issues:
        session.ended_at = datetime.now()
        return session

    #
    # Execution
    #

    if not dry_run:
        rename_files(needs_rename)

    #
    # TODO:
    # Build RenameResult objects and append them to
    # session.results.
    #

    session.ended_at = datetime.now()

    return session