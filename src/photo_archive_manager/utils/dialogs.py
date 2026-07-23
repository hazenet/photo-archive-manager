#!/usr/bin/env python3

from pathlib import Path
import subprocess


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