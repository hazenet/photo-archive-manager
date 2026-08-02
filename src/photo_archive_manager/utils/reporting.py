"""Functions for presenting information to the user."""

from photo_archive_manager.models import (
    RenameSession,
    RenameStatus,
)


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
        print(f"Duration : {session.duration}")

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
        return

    print()
    print("Results")
    print("-------")

    for result in sorted(
        session.results,
        key=lambda result: result.original_path.name.lower(),
    ):
        match result.status:
            case RenameStatus.RENAMED:
                assert result.destination_path is not None

                print(
                    f"RENAMED  "
                    f"{result.original_path.name} "
                    f"-> "
                    f"{result.destination_path.name}"
                )

            case RenameStatus.SKIPPED:
                print(f"SKIPPED  {result.original_path.name}")

            case RenameStatus.FAILED:
                print(f"FAILED   {result.original_path.name}")

                if result.message:
                    print(f"         {result.message}")
