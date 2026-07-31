#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto

from photo_archive_manager.models.photo_file import PhotoFile


class RenameStatus(Enum):
    """Outcome of a rename operation."""

    RENAMED = auto()
    SKIPPED = auto()
    FAILED = auto()


@dataclass(slots=True, frozen=True)
class RenameResult:
    """Represents the result of renaming a single photo."""

    #
    # Input
    #

    photo: PhotoFile

    original_path: Path

    #
    # Output
    #

    destination_path: Path | None

    status: RenameStatus

    #
    # Diagnostics
    #

    message: str | None = None

    exception: BaseException | None = None

    @property
    def renamed(self) -> bool:
        return self.status is RenameStatus.RENAMED

    @property
    def skipped(self) -> bool:
        return self.status is RenameStatus.SKIPPED

    @property
    def failed(self) -> bool:
        return self.status is RenameStatus.FAILED


class ImportStatus(Enum):
    """Outcome of an import operation."""

    IMPORTED = auto()
    DUPLICATE = auto()
    CONFLICT = auto()
    SKIPPED = auto()
    FAILED = auto()


@dataclass(slots=True, frozen=True)
class ImportResult:
    """Represents the result of importing a single photo."""

    #
    # Input
    #

    photo: PhotoFile

    source_path: Path

    #
    # Output
    #

    destination_path: Path | None

    status: ImportStatus

    #
    # Diagnostics
    #

    message: str | None = None

    exception: BaseException | None = None

    @property
    def imported(self) -> bool:
        return self.status is ImportStatus.IMPORTED

    @property
    def duplicate(self) -> bool:
        return self.status is ImportStatus.DUPLICATE

    @property
    def conflict(self) -> bool:
        return self.status is ImportStatus.CONFLICT

    @property
    def skipped(self) -> bool:
        return self.status is ImportStatus.SKIPPED

    @property
    def failed(self) -> bool:
        return self.status is ImportStatus.FAILED