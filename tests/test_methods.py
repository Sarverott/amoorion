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
    assert dryrun["capabilities"] == ["delete", "post", "read", "reply"] and dryrun["error"] is None


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


def test_read_keeps_posts_in_the_dataset(vault, tmp_path):
    from amoorion.dataset import Dataset

    Publish(vault)(text="kept", to=["dryrun"])
    Read(vault)(platform="dryrun", limit=5)
    entries = Dataset(tmp_path / "dataset").index("dryrun", "default")
    assert any(entry.text == "kept" and entry.state == "present" for entry in entries.values())


def test_snapshot_marks_what_is_gone_when_it_read_everything(vault, tmp_path):
    from amoorion.dataset import Dataset
    from amoorion.methods import SnapshotMethod
    from amoorion.plugins.dryrun.base import DryRun

    DryRun._messages.clear()
    [first] = Publish(vault)(text="first", to=["dryrun"])
    Publish(vault)(text="second", to=["dryrun"])
    assert SnapshotMethod(vault)(platform="dryrun")["present"] == 2
    DryRun._messages[:] = [m for m in DryRun._messages if m.id != first["message"]["id"]]  # removed elsewhere
    snapshot = SnapshotMethod(vault)(platform="dryrun")
    assert snapshot["complete"] and snapshot["gone"] == 1 and snapshot["present"] == 1
    index = tmp_path / "dataset" / "dryrun" / "default" / "index.json"
    assert index.is_file() and Dataset(tmp_path / "dataset").find("dryrun", "default", first["message"]["id"]).text == "first"


def test_delete_keeps_what_it_deletes(vault, tmp_path):
    from amoorion.dataset import Dataset
    from amoorion.methods import Delete

    [published] = Publish(vault)(text="regret", to=["dryrun"])
    id = published["message"]["id"]
    result = Delete(vault)(platform="dryrun", id=id)
    assert result["ok"] and result["message"]["text"] == "regret"
    assert id not in [m["id"] for m in Read(vault)(platform="dryrun", limit=50)]
    kept = tmp_path / "dataset" / "dryrun" / "default" / "deleted"
    assert "regret" in next(kept.glob("*.json")).read_text()
    assert Dataset(tmp_path / "dataset").index("dryrun", "default")[id].state == "deleted"


def test_delete_where_the_platform_cannot(vault):
    from amoorion.methods import Delete
    from amoorion.plugins import PLUGINS, Plugin

    class Mute(Plugin):
        name = "mute"

    PLUGINS._items["mute"] = Mute
    try:
        assert Delete(vault)(platform="mute", id="1") == {"platform": "mute", "ok": False, "message": None, "error": "mute can't delete"}
    finally:
        del PLUGINS._items["mute"]


def test_ids_become_safe_file_names():
    from amoorion.dataset.base import safe

    assert safe("123") == "123"
    assert safe("at://did:plc:me/app.bsky.feed.post/rkey1").startswith("at_did_plc_me_app.bsky.feed.post_rkey1-")
    assert safe("a/b") != safe("a:b")
