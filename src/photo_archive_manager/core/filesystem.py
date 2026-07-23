#!/usr/bin/env python3

from pathlib import Path

from ..models.photo import PhotoFile


def rename_files(
    photo_files: list[PhotoFile],
) -> None:
    """Rename all files according to the generated rename plan."""

    for photo_file in photo_files:

        #
        # Rename the primary file.
        #

        source_path = photo_file.file_path
        destination_path = photo_file.destination_path

        source_path.rename(
            destination_path,
        )

        #
        # Rename associated files.
        #

        renamed_associated_paths: list[Path] = []

        for associated_path in photo_file.associated_paths:

            associated_destination = associated_path.with_name(
                photo_file.destination_stem
                + associated_path.suffix
            )

            associated_path.rename(
                associated_destination,
            )

            renamed_associated_paths.append(
                associated_destination,
            )

        #
        # Keep the model synchronized with the filesystem.
        #

        photo_file.file_path = destination_path
        photo_file.associated_paths = renamed_associated_paths