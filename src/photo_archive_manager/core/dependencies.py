#!/usr/bin/env python3

import shutil
import sys


def check_dependencies(
) -> None:
    """Verify that required external programs are installed."""

    if shutil.which("exiftool") is None:
        print()
        print("ERROR")
        print("-----")
        print("ExifTool was not found.")
        print()
        print("Install it with:")
        print()
        print("    brew install exiftool")
        print()

        sys.exit(1)