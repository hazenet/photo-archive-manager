#!/usr/bin/env python3

import json
import subprocess
from datetime import datetime


from .constants import (
    TIMESTAMP_FIELDS,
)
from ..models.photo import PhotoFile


def _get_exif_json(
    photo_files: list[PhotoFile],
) -> list[dict[str, object]]:
    """Read metadata for multiple files using a single ExifTool process."""

    if not photo_files:
        return []

    command = [
        "exiftool",
        "-json",
        "-q",
        "-m",
    ]

    command.extend(
        str(photo_file.file_path)
        for photo_file in photo_files
    )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def read_capture_datetimes(
    photo_files: list[PhotoFile]
) -> None:
    """Read capture timestamps for all files."""

    exif_data_list = _get_exif_json(photo_files)

    for photo_file, exif_data in zip(
        photo_files,
        exif_data_list,
        strict=True,
    ):

        for field_name in TIMESTAMP_FIELDS:

            timestamp_string = exif_data.get(field_name)

            if timestamp_string is None:
                continue

            timestamp_string = timestamp_string[:19]

            try:

                photo_file.capture_datetime = datetime.strptime(
                    timestamp_string,
                    "%Y:%m:%d %H:%M:%S",
                )

                break

            except ValueError:
                continue

        if photo_file.capture_datetime is None:

            raise ValueError(
                f"No usable capture timestamp found in "
                f"'{photo_file.file_path.name}'."
            )