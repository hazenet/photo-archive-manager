"""Rename photo files in a selected folder."""

from datetime import datetime
from pathlib import Path

from photo_archive_manager.core.discovery import (
    build_existing_sequences,
    find_supported_files,
)
from photo_archive_manager.core.exif import read_capture_datetimes
from photo_archive_manager.core.filesystem import rename_files
from photo_archive_manager.core.planning_rename import (
    assign_sequence_numbers,
    generate_new_filenames,
)
from photo_archive_manager.core.validation_rename import validate_renames
from photo_archive_manager.models import (
    PhotoFile,
    RenameResult,
    RenameSession,
    RenameStatus,
)


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

    already_renamed: list[PhotoFile] = []
    needs_rename: list[PhotoFile] = []

    for photo in photo_files:
        if photo.is_renamed:
            already_renamed.append(photo)

            session.results.append(
                RenameResult(
                    photo=photo,
                    original_path=photo.file_path,
                    destination_path=photo.file_path,
                    status=RenameStatus.SKIPPED,
                )
            )

            continue

        needs_rename.append(photo)

    #
    # Nothing left to rename.
    #

    if not needs_rename:
        session.ended_at = datetime.now()
        return session

    #
    # Read capture timestamps.
    #

    read_capture_datetimes(
        needs_rename,
    )

    #
    # Generate rename plan.
    #

    existing_sequences = build_existing_sequences(
        already_renamed,
    )

    assign_sequence_numbers(
        needs_rename,
        existing_sequences,
    )

    generate_new_filenames(
        needs_rename,
    )

    #
    # Validate rename plan.
    #

    session.validation_issues = validate_renames(
        needs_rename,
    )

    if session.validation_issues:
        session.ended_at = datetime.now()
        return session

    #
    # Execute rename plan.
    #

    session.results.extend(
        rename_files(
            needs_rename,
            dry_run=dry_run,
        )
    )

    session.ended_at = datetime.now()

    return session
