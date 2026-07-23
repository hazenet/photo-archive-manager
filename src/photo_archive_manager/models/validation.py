#!/usr/bin/env python3

@dataclass
class ValidationIssue:
    photo_file: PhotoFile
    message: str