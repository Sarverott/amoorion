"""Every package of the workspace is released together (lock-step versions)."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGES = sorted(path.parent for path in (ROOT / "packages").glob("*/pyproject.toml"))


def load(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def test_every_package_is_bumped_with_the_others():
    root = load(ROOT / "pyproject.toml")
    files = root["tool"]["commitizen"]["version_files"]
    assert sorted(files) == sorted(f"packages/{package.name}/pyproject.toml:^version" for package in PACKAGES)
    versions = {load(package / "pyproject.toml")["project"]["version"] for package in PACKAGES}
    assert versions == {root["project"]["version"]}
