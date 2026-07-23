#!/usr/bin/env python3

from datetime import datetime

from .constants import (
    FILENAME_FORMAT,
    FILENAME_FORMAT_NO_ORIGINAL,
)
from ..models.photo import PhotoFile


def group_files_by_timestamp(
    photo_files: list[PhotoFile],
) -> dict[datetime, list[PhotoFile]]:
    """Group files by capture timestamp."""

    timestamp_groups: dict[datetime, list[PhotoFile]] = {}

    for photo_file in photo_files:

        if photo_file.capture_datetime is None:
            raise ValueError("capture_datetime has not been assigned.")
        capture_datetime = photo_file.capture_datetime

        timestamp_groups.setdefault(
            capture_datetime,
            [],
        ).append(photo_file)

    return timestamp_groups


def assign_sequence_numbers(
    photo_files: list[PhotoFile],
    existing_sequences: dict[datetime, int],
) -> None:
    """Assign sequence numbers to files sharing a capture timestamp."""

    timestamp_groups = group_files_by_timestamp(photo_files)

    for capture_datetime in sorted(timestamp_groups):

        group = timestamp_groups[capture_datetime]

        group.sort(
            key=lambda photo_file: photo_file.file_path.name.lower()
        )

        next_sequence = (
            existing_sequences.get(capture_datetime, 0) + 1
        )

        for photo_file in group:

            photo_file.sequence_number = next_sequence

            next_sequence += 1


def generate_new_filenames(
    photo_files: list[PhotoFile],
) -> None:
    """Generate the new filename for each photo."""

    for photo_file in photo_files:

        if photo_file.capture_datetime is None:
            raise ValueError("capture_datetime has not been assigned.")
        if photo_file.sequence_number is None:
            raise ValueError("sequence_number has not been assigned.")

        timestamp = photo_file.capture_datetime.strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        if photo_file.include_original_filename:

            photo_file.new_filename = FILENAME_FORMAT.format(
                timestamp=timestamp,
                sequence=photo_file.sequence_number,
                original_filename=photo_file.file_path.name,
            )

        else:

            photo_file.new_filename = FILENAME_FORMAT_NO_ORIGINAL.format(
                timestamp=timestamp,
                sequence=photo_file.sequence_number,
                extension=photo_file.file_path.suffix.lower(),
            )