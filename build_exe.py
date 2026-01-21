"""Build a standalone Windows executable using PyInstaller."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_NAME = "pdf_merge.py"
APP_NAME = "pdf_merge"


def main() -> int:
    if shutil.which("pyinstaller") is None:
        print("PyInstaller is not installed. Run: pip install pyinstaller")
        return 1

    script_path = Path(__file__).resolve().with_name(SCRIPT_NAME)
    if not script_path.exists():
        print(f"Could not find {SCRIPT_NAME} next to build_exe.py")
        return 1

    command = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        str(script_path),
    ]
    print("Running:", " ".join(command))
    subprocess.run(command, check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
