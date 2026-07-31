#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from photo_archive_manager.models.issues import ValidationIssue
from photo_archive_manager.models.results import (
    ImportResult,
    RenameResult,
)

@dataclass(slots=True)
class ExecutionSession:
    """Represents a single execution of PAM."""

    dry_run: bool = False

    started_at: datetime | None = None
    ended_at: datetime | None = None

    import_sessions: list[ImportSession] = field(default_factory=list)
    rename_sessions: list[RenameSession] = field(default_factory=list)

    warning_messages: list[str] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RenameSession:
    """Represents a single folder rename operation."""

    #
    # Configuration
    #

    dry_run: bool = False

    #
    # Input
    #

    folder: Path

    #
    # Timing
    #

    started_at: datetime | None = None
    ended_at: datetime | None = None

    #
    # Results
    #

    results: list[RenameResult] = field(default_factory=list)

    #
    # Diagnostics
    #

    validation_issues: list[ValidationIssue] = field(default_factory=list)

    warning_messages: list[str] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)

    #
    # Computed properties
    #

    @property
    def processed_count(self) -> int:
        return len(self.results)

    @property
    def renamed_count(self) -> int:
        return sum(result.renamed for result in self.results)

    @property
    def skipped_count(self) -> int:
        return sum(result.skipped for result in self.results)

    @property
    def failed_count(self) -> int:
        return sum(result.failed for result in self.results)

    @property
    def has_errors(self) -> bool:
        return bool(self.error_messages)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warning_messages)

    @property
    def has_validation_issues(self) -> bool:
        return bool(self.validation_issues)

    @property
    def succeeded(self) -> bool:
        return (
            not self.has_errors
            and not self.has_validation_issues
            and self.failed_count == 0
        )

    @property
    def duration(self) -> timedelta | None:
        if self.started_at is None or self.ended_at is None:
            return None

        return self.ended_at - self.started_at


@dataclass(slots=True)
class ImportSession:
    """Represents a single folder import operation."""

    #
    # Configuration
    #

    dry_run: bool = False

    #
    # Input
    #

    source_folder: Path
    destination_folder: Path

    #
    # Timing
    #

    started_at: datetime | None = None
    ended_at: datetime | None = None

    #
    # Results
    #

    results: list[ImportResult] = field(default_factory=list)

    #
    # Diagnostics
    #

    warning_messages: list[str] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)

    #
    # Computed properties
    #

    @property
    def processed_count(self) -> int:
        return len(self.results)

    @property
    def imported_count(self) -> int:
        return sum(result.imported for result in self.results)

    @property
    def skipped_count(self) -> int:
        return sum(result.skipped for result in self.results)

    @property
    def duplicate_count(self) -> int:
        return sum(result.duplicate for result in self.results)

    @property
    def conflict_count(self) -> int:
        return sum(result.conflict for result in self.results)

    @property
    def failed_count(self) -> int:
        return sum(result.failed for result in self.results)

    @property
    def has_errors(self) -> bool:
        return bool(self.error_messages)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warning_messages)

    @property
    def succeeded(self) -> bool:
        return (
            not self.has_errors
            and self.failed_count == 0
            and self.conflict_count == 0
        )

    @property
    def duration(self) -> timedelta | None:
        if self.started_at is None or self.ended_at is None:
            return None

        return self.ended_at - self.started_at