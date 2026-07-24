#!/usr/bin/env python3

"""Functions for presenting information to the user."""

from __future__ import annotations

from collections.abc import Sequence

from ..models.issue import ValidationIssue
from ..models.photo import PhotoFile


def print_discovery_summary(
    total_files: int,
    already_renamed: int,
    needs_rename: int,
) -> None:
    """Print a summary of the discovered photo files."""

    print()
    print("Discovery Summary")
    print("-----------------")
    print(f"Total supported files : {total_files}")
    print(f"Already renamed       : {already_renamed}")
    print(f"Needs renaming        : {needs_rename}")
    print()


def print_validation_issues(
    issues: Sequence[ValidationIssue],
) -> None:
    """Print all validation issues."""

    print()
    print("Validation failed")
    print("-----------------")

    for issue in issues:
        print(f"- {issue}")

    print()
    print(f"{len(issues)} validation issue(s) found.")
    print()


def print_rename_preview(
    photo_files: Sequence[PhotoFile],
) -> None:
    """Print the planned filename changes."""

    print()
    print("Rename Preview")
    print("--------------")

    for photo in photo_files:
        if photo.new_filename is None:
            continue

        print(
            f"{photo.filename}"
            f"  ->  "
            f"{photo.new_filename}"
        )

    print()


def print_completion_summary(
    total_files: int,
    already_renamed: int,
    renamed: int,
) -> None:
    """Print a summary after renaming has completed."""

    print()
    print("Rename Complete")
    print("---------------")
    print(f"Total supported files : {total_files}")
    print(f"Already renamed       : {already_renamed}")
    print(f"Renamed               : {renamed}")
    print()