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

        original_path = photo.path
        destination_path = photo.destination_path

        try:

            if not dry_run:
                original_path.rename(destination_path)

                #
                # Keep the PhotoFile in sync with the filesystem.
                #

                photo.path = destination_path

            results.append(
                RenameResult(
                    photo=photo,
                    original_path=original_path,
                    destination_path=destination_path,
                    status=RenameStatus.RENAMED,
                )
            )

        except Exception as ex:

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