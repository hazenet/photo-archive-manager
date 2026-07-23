#!/usr/bin/env python3

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