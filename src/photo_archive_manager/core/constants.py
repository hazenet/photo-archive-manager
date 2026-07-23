#!/usr/bin/env python3

"""Shared constants used throughout Photo Archive Manager."""

import re

# ---------------------------------------------------------------------------
# Supported media types
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Associated files
# ---------------------------------------------------------------------------

ASSOCIATED_EXTENSIONS = {
    ".xmp",
    ".photo-edit",
    ".pxd",
}

# ---------------------------------------------------------------------------
# EXIF
# ---------------------------------------------------------------------------

TIMESTAMP_FIELDS = (
    "DateTimeOriginal",
    "CreateDate",
    "MediaCreateDate",
    "TrackCreateDate",
    "FileModifyDate",
)

# ---------------------------------------------------------------------------
# Filename patterns
# ---------------------------------------------------------------------------

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

EXCLUDE_ORIGINAL_FILENAME_PATTERNS = (
    # Dropbox date-based format, e.g. 2026-07-20 15.38.58.jpg
    re.compile(
        r"^\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}$",
        re.IGNORECASE,
    ),
)

# ---------------------------------------------------------------------------
# Output filename formats
# ---------------------------------------------------------------------------

FILENAME_FORMAT = (
    "{timestamp}_{sequence:03d} - {original_filename}"
)

FILENAME_FORMAT_NO_ORIGINAL = (
    "{timestamp}_{sequence:03d}{extension}"
)