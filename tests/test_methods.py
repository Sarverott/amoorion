import pytest

from amoorion.methods import METHODS, Plugins, Publish, Read
from amoorion.vault import VaultLink, open_vault


@pytest.fixture
def vault():
    return open_vault(VaultLink(kind="env"))


def test_built_in_methods():
    assert {"plugins", "publish", "read"} <= set(METHODS.names())


def test_plugins_lists_dryrun(vault):
    assert {"name": "dryrun", "description": Plugins(vault)()[0]["description"],
            "capabilities": ["post", "read", "reply"]} in Plugins(vault)()


def test_publish_reports_per_platform(vault):
    results = Publish(vault)(text="hello", to=["dryrun", "nowhere"])
    assert results[0]["ok"] and results[0]["message"]["text"] == "hello"
    assert not results[1]["ok"] and "nowhere" in results[1]["error"]


def test_read_after_publish(vault):
    Publish(vault)(text="latest", to=["dryrun"])
    assert Read(vault)(platform="dryrun", limit=1)[0]["text"] == "latest"


def test_params_are_validated(vault):
    with pytest.raises(ValueError):
        Publish(vault)(text="x", to=[])
