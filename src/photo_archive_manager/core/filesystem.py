from photo_archive_manager.models import (
    PhotoFile,
    RenameResult,
    RenameStatus,
)


def rename_files(
    photo_files: list[PhotoFile],
    *,
    dry_run: bool = False,
) -> list[RenameResult]:
    """Rename the supplied photo files."""

    results: list[RenameResult] = []

    for photo in photo_files:
        original_path = photo.file_path
        destination_path = photo.destination_path

        try:
            if not dry_run:
                #
                # Rename the primary file.
                #

                original_path.rename(destination_path)

                #
                # Rename all associated files.
                #

                for source_path, destination_path_associated in zip(
                    photo.associated_paths,
                    photo.associated_destination_paths,
                    strict=True,
                ):
                    source_path.rename(destination_path_associated)

                #
                # Keep the PhotoFile in sync with the filesystem.
                #

                photo.file_path = destination_path
                photo.associated_paths = photo.associated_destination_paths

            results.append(
                RenameResult(
                    photo=photo,
                    original_path=original_path,
                    destination_path=destination_path,
                    status=RenameStatus.RENAMED,
                )
            )

        except OSError as ex:
            results.append(
                RenameResult(
                    photo=photo,
                    original_path=original_path,
                    destination_path=destination_path,
                    status=RenameStatus.FAILED,
                    message=str(ex),
                    exception=ex,
                )
            )

    return results
