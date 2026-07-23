#!/usr/bin/env python3

from ..models.issue import ValidationIssue
from ..models.photo import PhotoFile


def _add_validation_issue(
    issues: list[ValidationIssue],
    photo_file: PhotoFile,
    message: str,
) -> None:
    """Append a validation issue to the results."""

    issues.append(
        ValidationIssue(
            photo_file=photo_file,
            message=message,
        )
    )


def validate_renames(
    photo_files: list[PhotoFile],
) -> list[ValidationIssue]:
    """Validate that all generated renames are safe to perform."""

    issues: list[ValidationIssue] = []
    generated_filename_map: dict[str, PhotoFile] = {}
    reported_collision_files: set[PhotoFile] = set()

    for photo_file in photo_files:

        if photo_file.new_filename is None:
            raise ValueError("new_filename has not been assigned.")

        #
        # Check for generated filename collisions.
        #

        existing_photo_file = generated_filename_map.get(
            photo_file.new_filename,
        )

        if existing_photo_file is None:

            generated_filename_map[
                photo_file.new_filename
            ] = photo_file

        else:

            if existing_photo_file not in reported_collision_files:

                _add_validation_issue(
                    issues,
                    existing_photo_file,
                    "Generated filename collision with "
                    f"'{photo_file.file_path.name}'.",
                )

                reported_collision_files.add(
                    existing_photo_file,
                )

            _add_validation_issue(
                issues,
                photo_file,
                "Generated filename collision with "
                f"'{existing_photo_file.file_path.name}'.",
            )

        #
        # Check whether the destination filename already exists.
        #

        destination_path = photo_file.destination_path

        if (
            destination_path.exists()
            and destination_path != photo_file.file_path
        ):

            _add_validation_issue(
                issues,
                photo_file,
                "Destination filename already exists: "
                f"'{destination_path.name}'.",
            )

    return issues
