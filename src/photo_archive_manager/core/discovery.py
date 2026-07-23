#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

from .constants import (
    ASSOCIATED_EXTENSIONS,
    EXCLUDE_ORIGINAL_FILENAME_PATTERNS,
    RENAMED_PATTERN,
    SUPPORTED_EXTENSIONS,
)
from ..models.photo import PhotoFile


def is_supported_file(
    file_path: Path
) -> bool:
    """Return True if the file type is supported."""

    return (
        file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def is_already_renamed(file_path: Path) -> bool:
    """Return True if the filename already follows our naming convention."""

    return bool(RENAMED_PATTERN.match(file_path.name))


def find_associated_files(
    file_path: Path,
) -> list[Path]:
    """Return all associated files for the given photo or video."""

    associated_files: list[Path] = []

    for associated_extension in ASSOCIATED_EXTENSIONS:

        associated_path = file_path.with_suffix(associated_extension)

        if associated_path.is_file():
            associated_files.append(associated_path)

    return associated_files


def find_supported_files(
    selected_root_folder: Path,
) -> list[PhotoFile]:
    """Return all supported photo and video files in the selected folder."""

    supported_files: list[PhotoFile] = []

    for file_path in sorted(selected_root_folder.iterdir()):

        if not is_supported_file(file_path):
            continue

        supported_files.append(
            PhotoFile(
                file_path=file_path,
                associated_paths=find_associated_files(file_path),
                include_original_filename=should_include_original_filename(
                    file_path
                ),
            )
        )

    return supported_files


def read_existing_sequences(
    photo_files: list[PhotoFile],
) -> dict[datetime, int]:
    """Read the highest sequence number already used for each timestamp."""

    existing_sequences: dict[datetime, int] = {}

    for photo_file in photo_files:

        match = RENAMED_PATTERN.match(photo_file.file_path.name)

        if match is None:
            raise ValueError(
                f"Unexpected filename: {photo_file.file_path.name}"
            )

        capture_datetime = datetime.strptime(
            match.group("timestamp"),
            "%Y-%m-%d_%H-%M-%S",
        )

        sequence_number = int(match.group("sequence"))

        current_max = existing_sequences.get(
            capture_datetime,
            0,
        )

        existing_sequences[capture_datetime] = max(
            current_max,
            sequence_number,
        )

    return existing_sequences


def should_include_original_filename(
    file_path: Path,
) -> bool:
    """Return True if the original filename should be included."""

    stem = file_path.stem

    return not any(
        pattern.match(stem)
        for pattern in EXCLUDE_ORIGINAL_FILENAME_PATTERNS
    )


def split_files_by_rename_status(
    supported_files: list[PhotoFile],
) -> tuple[list[PhotoFile], list[PhotoFile]]:
    """Split files into already renamed and files needing rename."""

    already_renamed: list[PhotoFile] = []
    needs_rename: list[PhotoFile] = []

    for photo_file in supported_files:

        if is_already_renamed(photo_file.file_path):
            already_renamed.append(photo_file)
        else:
            needs_rename.append(photo_file)

    return already_renamed, needs_rename