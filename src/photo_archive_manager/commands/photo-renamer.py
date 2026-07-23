#!/usr/bin/env python3

"""
Photo Renamer
Version 0.2

Renames photo and video files to:

    YYYY-MM-DD_HH-MM-SS_XXX - OriginalFilename.ext

Design principle

Once a file has been renamed into the archive naming format, 
the filename becomes the canonical source of truth for its timestamp and sequence number. 
The script will never re-read EXIF metadata from already-renamed files.
"""

# ============================================================================
# Imports
# ============================================================================

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
import json
import re
import shutil
import subprocess
import sys
import time
import argparse


# ============================================================================
# Constants
# ============================================================================

PHOTO_EXTENSIONS = {
    ".dng",
    ".heic",
    ".jpeg",
    ".jpg",
    ".nef",
    ".png",
    ".raf",
    ".tif",
    ".tiff",
    ".rw2",
}

VIDEO_EXTENSIONS = {
    ".m4v",
    ".mov",
    ".mp4",
    ".3gp",
}

SUPPORTED_EXTENSIONS = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS

ASSOCIATED_EXTENSIONS = {
    ".xmp",
    ".photo-edit",
    ".pxd",
}

TIMESTAMP_FIELDS = (
    "DateTimeOriginal",
    "CreateDate",
    "MediaCreateDate",
    "TrackCreateDate",
    "FileModifyDate",
)

# Matches files already renamed by this application.
# Expected filename format:
#   YYYY-MM-DD_HH-MM-SS_XXX - OriginalFilename.ext
# Named capture groups:
#   timestamp    YYYY-MM-DD_HH-MM-SS
#   sequence     XXX
# The original filename is not captured because it is not needed.
RENAMED_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_"
    r"(?P<sequence>\d{3}).*\.[^.]+$",
    re.IGNORECASE,
)

EXCLUDE_ORIGINAL_FILENAME_PATTERNS = [
    # Dropbox date-based format, e.g. 2026-07-20 15.38.58.jpg
    re.compile(
        r"^\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}$",
        re.IGNORECASE,
    ),
]

FILENAME_FORMAT = (
    "{timestamp}_{sequence:03d} - {original_filename}"
)

FILENAME_FORMAT_NO_ORIGINAL = (
    "{timestamp}_{sequence:03d}{extension}"
)


# ============================================================================
# Models
# ============================================================================

@dataclass(eq=False)
class PhotoFile:
    file_path: Path
    associated_paths: list[Path] = field(default_factory=list)
    capture_datetime: datetime | None = None
    sequence_number: int | None = None
    new_filename: str | None = None
    include_original_filename: bool = True

    @property
    def destination_path(self) -> Path:
        """Return the destination path after the planned rename."""

        assert self.new_filename is not None

        return self.file_path.with_name(
            self.new_filename,
        )

    @property
    def destination_stem(self) -> str:
        """Return the destination filename without extension."""

        return self.destination_path.stem

@dataclass
class ValidationIssue:
    photo_file: PhotoFile
    message: str


# ============================================================================
# Dependency checking
# ============================================================================

def check_dependencies(
) -> None:
    """Verify that required external programs are installed."""

    if shutil.which("exiftool") is None:
        print()
        print("ERROR")
        print("-----")
        print("ExifTool was not found.")
        print()
        print("Install it with:")
        print()
        print("    brew install exiftool")
        print()

        sys.exit(1)


# ============================================================================
# Folder selection
# ============================================================================

def choose_folder(
) -> Path:
    """Display the native macOS folder picker."""

    applescript = (
        'POSIX path of (choose folder '
        'with prompt "Select folder to rename")'
    )

    result = subprocess.run(
        ["osascript", "-e", applescript],
        capture_output=True,
        text=True,
        check=True,
    )

    return Path(result.stdout.strip())


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Rename photos and videos in a folder."
    )

    parser.add_argument(
        "folder",
        nargs="?",
        type=Path,
        help="Folder to process. If omitted, a folder picker is shown.",
    )

    return parser.parse_args()


# ============================================================================
# Discovery functions
# ============================================================================

def is_supported_file(
    file_path: Path
) -> bool:
    """Return True if the file type is supported."""

    return (
        file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def is_already_renamed(file_path: Path) -> bool:
    """Return True if the filename already follows our naming convention."""

    return bool(RENAMED_PATTERN.match(file_path.name))


def read_existing_sequences(
    photo_files: list[PhotoFile],
) -> dict[datetime, int]:
    """Read the highest sequence number already used for each timestamp."""

    existing_sequences: dict[datetime, int] = {}

    for photo_file in photo_files:

        match = RENAMED_PATTERN.match(photo_file.file_path.name)

        if match is None:
            raise ValueError(
                f"Unexpected filename: {photo_file.file_path.name}"
            )

        capture_datetime = datetime.strptime(
            match.group("timestamp"),
            "%Y-%m-%d_%H-%M-%S",
        )

        sequence_number = int(match.group("sequence"))

        current_max = existing_sequences.get(
            capture_datetime,
            0,
        )

        existing_sequences[capture_datetime] = max(
            current_max,
            sequence_number,
        )

    return existing_sequences


def should_include_original_filename(
    file_path: Path,
) -> bool:
    """Return True if the original filename should be included."""

    stem = file_path.stem

    return not any(
        pattern.match(stem)
        for pattern in EXCLUDE_ORIGINAL_FILENAME_PATTERNS
    )


def find_associated_files(
    file_path: Path,
) -> list[Path]:
    """Return all associated files for the given photo or video."""

    associated_files: list[Path] = []

    for associated_extension in ASSOCIATED_EXTENSIONS:

        associated_path = file_path.with_suffix(associated_extension)

        if associated_path.is_file():
            associated_files.append(associated_path)

    return associated_files


def find_supported_files(
    selected_root_folder: Path,
) -> list[PhotoFile]:
    """Return all supported photo and video files in the selected folder."""

    supported_files: list[PhotoFile] = []

    for file_path in sorted(selected_root_folder.iterdir()):

        if not is_supported_file(file_path):
            continue

        supported_files.append(
            PhotoFile(
                file_path=file_path,
                associated_paths=find_associated_files(file_path),
                include_original_filename=should_include_original_filename(
                    file_path
                ),
            )
        )

    return supported_files


def get_exif_json(
    photo_files: list[PhotoFile],
) -> list[dict]:
    """Read metadata for multiple files using a single ExifTool process."""

    if not photo_files:
        return []

    command = [
        "exiftool",
        "-json",
        "-q",
        "-m",
    ]

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

    exif_data_list = get_exif_json(photo_files)

    for photo_file, exif_data in zip(photo_files, exif_data_list):

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


# ============================================================================
# Processing functions
# ============================================================================

def split_files_by_rename_status(
    supported_files: list[PhotoFile],
) -> tuple[list[PhotoFile], list[PhotoFile]]:
    """Split files into already renamed and files needing rename."""

    already_renamed = []
    needs_rename = []

    for photo_file in supported_files:

        if is_already_renamed(photo_file.file_path):
            already_renamed.append(photo_file)
        else:
            needs_rename.append(photo_file)

    return already_renamed, needs_rename


def group_files_by_timestamp(
    photo_files: list[PhotoFile],
) -> dict[datetime, list[PhotoFile]]:
    """Group files by capture timestamp."""

    timestamp_groups: dict[datetime, list[PhotoFile]] = {}

    for photo_file in photo_files:

        assert photo_file.capture_datetime is not None
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

        assert photo_file.capture_datetime is not None
        assert photo_file.sequence_number is not None

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

        assert photo_file.new_filename is not None

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


# ============================================================================
# Debug functions
# ============================================================================

def debug_print_rename_preview(
    photo_files: list[PhotoFile],
) -> None:
    """DEBUG - Preview the planned file renames."""

    sorted_photo_files = sorted(
        photo_files,
        key=lambda photo_file: (
            photo_file.capture_datetime,
            photo_file.sequence_number,
            photo_file.file_path.name.lower(),
        ),
    )

    for photo_file in sorted_photo_files:

        assert photo_file.new_filename is not None

        print(
            f"{photo_file.file_path.name:<35} -> "
            f"{photo_file.new_filename}"
        )


# ============================================================================
# Main
# ============================================================================

def main() -> None:

    check_dependencies()

    args = parse_arguments()

    if args.folder is None:

        selected_root_folder = choose_folder()

    else:

        selected_root_folder = args.folder.expanduser().resolve()

        if not selected_root_folder.is_dir():

            print(f"ERROR: '{selected_root_folder}' is not a folder.")
            sys.exit(1)

    start_time = time.perf_counter()

    supported_files = find_supported_files(selected_root_folder)

    already_renamed_files, files_to_rename = split_files_by_rename_status(
        supported_files
    )

    existing_sequences = read_existing_sequences(
        already_renamed_files,
    )

    print()
    print(f"Selected folder : {selected_root_folder}")
    print(f"Supported files : {len(supported_files)}")
    print(f"Already renamed : {len(already_renamed_files)}")
    print(f"Needs rename    : {len(files_to_rename)}")
    print()

    if not files_to_rename:

        print("Nothing to rename")

    else:

        read_capture_datetimes(files_to_rename)

        assign_sequence_numbers(
            files_to_rename,
            existing_sequences,
        )

        generate_new_filenames(
            files_to_rename,
        )

        validation_issues = validate_renames(
            files_to_rename,
        )

        if validation_issues:

            print()
            print("VALIDATION ERRORS")
            print("-----------------")
            print()

            for issue in validation_issues:

                print(issue.photo_file.file_path.name)
                print(f"    {issue.message}")
                print()

            sys.exit(1)

        rename_files(
            files_to_rename,
        )

        debug_print_rename_preview(
            files_to_rename,
        )

    elapsed_time = time.perf_counter() - start_time

    print()
    print(f"Elapsed time    : {elapsed_time:.3f} seconds")

if __name__ == "__main__":
    main()