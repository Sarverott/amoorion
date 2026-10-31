"""Code that .gitignore hides works here and is missing everywhere else: `dataset/` once hid src/amoorion/dataset/."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_no_source_file_is_ignored_by_git():

    ignored = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "src",
            "packages",
            "tools/amoorion-dev",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    assert [file for file in ignored if "__pycache__" not in file] == []
