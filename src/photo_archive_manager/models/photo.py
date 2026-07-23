#!/usr/bin/env python3

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


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

        if self.new_filename is None:
            raise ValueError(
                "Destination path requested before a new filename has been assigned."
            )

        return self.file_path.with_name(
            self.new_filename,
        )

    @property
    def destination_stem(self) -> str:
        """Return the destination filename without extension."""

        return self.destination_path.stem

    @property
    def filename(self) -> str:
        """Return the original filename including its extension."""
        return self.file_path.name


    @property
    def stem(self) -> str:
        """Return the original filename without its extension."""
        return self.file_path.stem


    @property
    def suffix(self) -> str:
        """Return the original filename extension."""
        return self.file_path.suffix