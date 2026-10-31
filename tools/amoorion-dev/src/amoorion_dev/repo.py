"""The repository: git, its files at any revision, and the settings of `.github/flow.toml`."""

import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import git


@dataclass
class Repo:
    """The git repository worked on, and the files in it at any revision."""

    root: Path

    @classmethod
    def here(
        cls,
        start: Path | None = None,
    ) -> "Repo":
        """The repository around `start`, by default the current directory."""

        start = start or Path.cwd()

        try:
            top = git.Repo(
                start,
                search_parent_directories=True,
            ).working_tree_dir
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            top = None

        return cls(Path(top or start))

    def run(self, *args: str, check: bool = True) -> str:
        """Run a program at the root; answers its output."""

        result = subprocess.run(
            args,
            cwd=self.root,
            check=check,
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
        )

        return result.stdout.strip()

    def git(
        self,
        *args: str,
    ) -> str:
        """git's answer, or "" when git has none (no such revision, no repository)."""

        try:
            return (
                git.Git(self.root)
                .execute(
                    [
                        "git",
                        *args,
                    ]
                )
                .strip()
            )
        except (git.GitCommandError, FileNotFoundError):
            return ""

    def read(
        self,
        path: str,
        revision: str | None = None,
    ) -> str:
        """A file now, or as it was at `revision` ("" when it wasn't there)."""

        if revision is None:
            file = self.root / path

            return file.read_text() if file.exists() else ""

        return self.git(
            "show",
            f"{revision}:{path}",
        )

    def settings(self) -> dict[str, Any]:
        """The settings of .github/flow.toml, empty if there is none."""

        file = self.root / ".github" / "flow.toml"

        return tomllib.loads(file.read_text()) if file.exists() else {}

    def tagged(
        self,
        version: str,
    ) -> bool:
        """Whether a version has its tag."""

        return bool(
            self.git(
                "tag",
                "--list",
                f"v{version}",
            )
        )
