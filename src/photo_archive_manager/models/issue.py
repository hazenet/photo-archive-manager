#!/usr/bin/env python3

"""Models representing issues discovered during processing."""

from dataclasses import dataclass

from .photo import PhotoFile


@dataclass
class ValidationIssue:
    """Represents a validation issue for a photo file."""

    photo_file: PhotoFile
    message: str

    def __str__(self) -> str:
        """Return the validation message."""

        return self.message