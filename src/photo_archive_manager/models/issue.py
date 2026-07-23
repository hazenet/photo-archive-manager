#!/usr/bin/env python3

from dataclasses import dataclass

from .photo import PhotoFile


@dataclass
class ValidationIssue:
    photo_file: PhotoFile
    message: str