import pytest

from amoorion.methods import METHODS, Plugins, Publish, Read
from amoorion.vault import VaultLink, open_vault


@pytest.fixture
def vault():
    return open_vault(VaultLink(kind="env"))


def test_built_in_methods():
    assert {"accounts", "plugins", "publish", "read"} <= set(METHODS.names())


def test_plugins_lists_dryrun(vault):
    dryrun = next(info for info in Plugins(vault)() if info["name"] == "dryrun")
    assert dryrun["capabilities"] == ["post", "read", "reply"] and dryrun["error"] is None


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


def test_accounts_tells_what_is_missing_without_values(vault, monkeypatch):
    from amoorion.methods import Accounts
    from amoorion.plugins import PLUGINS, Plugin

    class Needy(Plugin):
        name = "needy"
        secrets = ("token", "user")

    monkeypatch.setitem(PLUGINS._items, "needy", Needy)
    monkeypatch.setenv("AMOORION_SECRET_NEEDY_TOKEN", "hidden-value")
    monkeypatch.delenv("AMOORION_SECRET_NEEDY_USER", raising=False)
    statuses = {status["platform"]: status for status in Accounts(vault)()}
    assert statuses["dryrun"]["ready"]
    assert statuses["needy"]["missing"] == ["user"] and not statuses["needy"]["ready"]
    assert "hidden-value" not in str(statuses)


def test_reply_by_id(vault):
    from amoorion.methods import Reply

    [published] = Publish(vault)(text="question", to=["dryrun"])
    answer = Reply(vault)(platform="dryrun", to=published["message"]["id"], text="answer")
    assert answer["reply_to"] == published["message"]["id"]
