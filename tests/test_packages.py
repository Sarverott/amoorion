"""Every package of the workspace has its own version (Q15), written by amoorion-dev, not commitizen."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGES = sorted(path.parent for path in (ROOT / "packages").glob("*/pyproject.toml"))


def load(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def test_commitizen_writes_no_versions():
    commitizen = load(ROOT / "pyproject.toml")["tool"]["commitizen"]
    assert "version_files" not in commitizen and "pre_bump_hooks" not in commitizen


def test_no_package_is_ahead_of_amoorion():
    """amoorion is bumped at every release, a package only when it changed."""
    from amoorion_dev.version import parse

    main = parse(load(ROOT / "pyproject.toml")["project"]["version"])
    for package in PACKAGES:
        assert parse(load(package / "pyproject.toml")["project"]["version"])[:3] <= main[:3], package.name
