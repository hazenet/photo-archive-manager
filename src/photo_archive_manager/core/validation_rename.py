from photo_archive_manager.models import (
    PhotoFile,
    ValidationIssue,
)


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
        #
        # Validate required planning data.
        #

        if photo_file.capture_datetime is None:
            _add_validation_issue(
                issues,
                photo_file,
                "Capture timestamp could not be determined.",
            )
            continue

        if photo_file.sequence_number is None:
            _add_validation_issue(
                issues,
                photo_file,
                "Sequence number has not been assigned.",
            )
            continue

        if photo_file.new_filename is None:
            _add_validation_issue(
                issues,
                photo_file,
                "New filename has not been generated.",
            )
            continue

        #
        # Check for generated filename collisions.
        #

        existing_photo_file = generated_filename_map.get(
            photo_file.new_filename,
        )

        if existing_photo_file is None:
            generated_filename_map[photo_file.new_filename] = photo_file

        else:
            if existing_photo_file not in reported_collision_files:
                _add_validation_issue(
                    issues,
                    existing_photo_file,
                    f"Generated filename collision with '{photo_file.file_path.name}'.",
                )

                reported_collision_files.add(existing_photo_file)

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

        if destination_path.exists() and destination_path != photo_file.file_path:
            _add_validation_issue(
                issues,
                photo_file,
                f"Destination filename already exists: '{destination_path.name}'.",
            )

    return issues