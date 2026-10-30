"""schema.vault.json of every package says what its plugin really asks the vault for."""

import inspect
import json
import re
from pathlib import Path

import pytest

from amoorion.plugins import PLUGINS, load_plugins

ROOT = Path(__file__).parents[1]
load_plugins()
ASKED = re.compile(r"""secret\(["']([^"']+)["']\)""")
NAMES = [name for name in PLUGINS.names() if PLUGINS.get(name).secrets]


@pytest.mark.parametrize("name", NAMES)
def test_schema_matches_the_plugin(name):
    plugin = PLUGINS.get(name)
    schema = plugin.schema()
    assert set(schema["scopes"]) == set(plugin.secrets)
    assert all(schema["scopes"].values()) and all(schema["optional"].values())
    asked = set(ASKED.findall(inspect.getsource(plugin)))
    assert asked <= set(schema["scopes"]) | set(schema["optional"])


@pytest.mark.parametrize("package", sorted((ROOT / "packages").iterdir()), ids=lambda path: path.name)
def test_every_package_has_a_schema(package):
    [file] = package.glob("src/*/schema.vault.json")
    assert json.loads(file.read_text())["vault"]


@pytest.mark.parametrize("package", sorted((ROOT / "packages").iterdir()), ids=lambda path: path.name)
def test_every_package_has_its_page_and_links(package):
    platform = package.name.removeprefix("amoorion-")
    assert (ROOT / "docs/platforms" / f"{platform}.md").is_file()
    assert f"platforms/{platform}\n" in (ROOT / "docs/platforms.md").read_text()
    readme = (package / "README.md").read_text()
    assert "../" not in readme  # PyPI shows it apart from the repository
    assert f"https://pypi.org/project/{package.name}/" in readme
