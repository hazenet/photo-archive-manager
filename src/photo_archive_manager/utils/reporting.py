"""Functions for presenting information to the user."""

from photo_archive_manager.models import (
    RenameResult,
    RenameSession,
    RenameStatus,
)


def _destination_name(result: RenameResult) -> str:
    """Return the destination filename for sorting."""

    assert result.destination_path is not None
    return result.destination_path.name


def print_rename_session(
    session: RenameSession,
    *,
    show_results: bool = False,
) -> None:
    """Print the results of a completed rename session."""

    print()
    print("Rename Session")
    print("==============")
    print()

    print(f"Folder   : {session.folder}")
    print(f"Dry Run  : {'Yes' if session.dry_run else 'No'}")

    if session.duration is not None:
        print(f"Duration : {session.duration.total_seconds():.3f} s")

    print()
    print("Summary")
    print("-------")
    print(f"Supported files : {session.processed_count}")
    print(f"Renamed         : {session.renamed_count}")
    print(f"Skipped         : {session.skipped_count}")
    print(f"Failed          : {session.failed_count}")

    if session.validation_issues:
        print()
        print("Validation Issues")
        print("-----------------")

        for issue in session.validation_issues:
            print(f"- {issue.message}")

    if not show_results:
        print()
        return

    renamed_results = sorted(
        (
            result
            for result in session.results
            if (
                result.status is RenameStatus.RENAMED
                and result.destination_path is not None
            )
        ),
        key=_destination_name,
    )

    skipped_results = sorted(
        (result for result in session.results if result.status is RenameStatus.SKIPPED),
        key=lambda result: result.original_path.name.lower(),
    )

    failed_results = sorted(
        (result for result in session.results if result.status is RenameStatus.FAILED),
        key=lambda result: result.original_path.name.lower(),
    )

    destination_name_width = max(
        (
            len(result.destination_path.name)
            for result in renamed_results
            if result.destination_path is not None
        ),
        default=0,
    )

    if renamed_results:
        print()
        print(f"Renamed ({len(renamed_results)})")
        print("-------------")

        for result in renamed_results:
            assert result.destination_path is not None

            print(
                f"{result.destination_path.name:<{destination_name_width}}"
                f"  <-  "
                f"{result.original_path.name}"
            )

    if skipped_results:
        print()
        print(f"Skipped ({len(skipped_results)})")
        print("-------------")

        for result in skipped_results:
            print(result.original_path.name)

    if failed_results:
        print()
        print(f"Failed ({len(failed_results)})")
        print("------------")

        for result in failed_results:
            print(result.original_path.name)

            if result.message:
                print(f"    {result.message}")
    print()
