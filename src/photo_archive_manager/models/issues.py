#!/usr/bin/env python3

"""Models representing issues discovered during processing."""

from dataclasses import dataclass

from photo_archive_manager.models.photo_file import PhotoFile


@dataclass(slots=True)
class ValidationIssue:
    """Represents a validation issue for a photo file."""

    file: PhotoFile
    message: str