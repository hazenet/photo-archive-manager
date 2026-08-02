import subprocess
from pathlib import Path


def choose_folder() -> Path | None:
    """Display the native macOS folder picker."""

    applescript = (
        "POSIX path of (choose folder with prompt "
        '"PAM Rename: Select the folder containing the files to rename")'
    )

    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError as ex:
        # AppleScript error -128 = User cancelled.
        if ex.returncode == 1 and "-128" in ex.stderr:
            return None

        raise

    return Path(result.stdout.strip())
