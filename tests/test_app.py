"""`Amoorion` and `Plugins`: the way of using amoorion from Python."""

import gc
import os
import shutil

import pytest
import yaml
from fastapi.testclient import TestClient

from amoorion import Amoorion, Plug, Plugins
from amoorion.core import AmoorionError
from amoorion.dataset import Dataset
from amoorion.inbox import Inbox
from amoorion.methods import plugsFlagsToList


@pytest.fixture
def env(
    tmp_path,
    monkeypatch,
):

    monkeypatch.chdir(tmp_path)

    monkeypatch.setenv(
        "AMOORION_VAULT",
        "env",
    )

    monkeypatch.setenv(
        "AMOORION_INBOX",
        str(tmp_path / "inbox.sqlite3"),
    )

    monkeypatch.setenv(
        "AMOORION_DATASET",
        str(tmp_path / "dataset"),
    )

    file = tmp_path / "one.env"

    file.write_text(
        f"AMOORION_VAULT=env\nAMOORION_INBOX={tmp_path / 'one.sqlite3'}\nAMOORION_VAULT_TOKEN=secret-value\n"
    )

    return file


def test_plugins_is_names_and_objects_alike():

    assert "dryrun" in list(Plugins)

    assert all(isinstance(name, str) for name in list(Plugins))

    plug = next(plug for plug in Plugins if plug == "dryrun")

    assert plug.name == "dryrun" and plug.infoflags["can_post"] is True

    assert Plugins["dryrun"] is Plugins["dryrun"]

    assert isinstance(Plugins["dryrun"], Plug)

    assert "dryrun" in repr(Plugins["dryrun"])


def test_dict_of_plugins_gives_description_version_flags(env):

    info = dict(Plugins)["dryrun"]

    assert info.description == Plugins["dryrun"].description

    assert info.version

    assert info.flags["creds"] is True

    assert plugsFlagsToList({"creds": False, "can_post": True}) == ["can_post"]


def test_wrong_names_fail_early(env):

    with pytest.raises(AmoorionError):
        Plugins["nowhere"]

    with pytest.raises(AmoorionError):
        Amoorion().use("nowhere")

    with pytest.raises(AmoorionError):
        Amoorion("/no/such/env")

    with pytest.raises(AttributeError):
        Amoorion().nomethod


def test_use_chains_and_publish_goes_there(env):

    amo = Amoorion().use(Plugins["dryrun"]).use("dryrun")

    assert amo.used == ["dryrun"]

    [result] = amo.publish(text="hello")

    assert result["ok"] and result["platform"] == "dryrun"

    assert (
        amo.read(limit=1)[0]["text"] == "hello"
    )  # one platform in use: it needs no naming


def test_an_env_file_is_this_object_only(
    env,
    tmp_path,
    monkeypatch,
):

    one = Amoorion(env).use("dryrun")

    one.publish(text="kept")

    one.read(limit=1)

    assert one.store.path == tmp_path / "one.sqlite3"

    assert "secret-value" not in repr(one)


def test_without_args_it_is_a_sandbox_gone_with_its_object(
    env,
    tmp_path,
    monkeypatch,
):

    (tmp_path / ".env").write_text(
        "AMOORION_VAULT=keepassxc\nAMOORION_INBOX=real.sqlite3\n"
    )

    before = dict(os.environ)

    amo = Amoorion().use("dryrun")

    amo.read(limit=1)

    home = amo.store.path.parent

    assert (
        amo.link.kind == "env"
        and not home.is_relative_to(tmp_path)
        and amo.dataset.path.parent == home
    )

    assert amo.store.path.is_file() and dict(os.environ) == before

    assert Amoorion().store.path != amo.store.path

    del amo

    gc.collect()

    assert not home.exists()


def test_init_puts_the_process_in_a_sandbox(
    env,
    tmp_path,
):

    (tmp_path / ".env").write_text("AMOORION_VAULT=keepassxc\n")

    scratch = Amoorion.init()

    try:
        assert os.environ["AMOORION_VAULT"] == "env"

        assert (
            Inbox().path == scratch / "inbox.sqlite3"
            and Dataset().path == scratch / "dataset"
        )
    finally:
        shutil.rmtree(scratch)


def test_save_load_detect_changes_and_hold_no_secret(
    env,
    tmp_path,
):

    state = tmp_path / "state.yaml"

    amo = (
        Amoorion(
            env,
            tmp_path / "data",
            flags={"mode": "cli"},
        )
        .use("dryrun")
        .save(state)
    )

    assert amo.changes() == []

    written = state.read_text()

    assert "secret-value" not in written

    assert yaml.safe_load(written)["plugins"] == ["dryrun"]

    again = Amoorion().load(state)

    assert (
        again.used == ["dryrun"]
        and again.flags == {"mode": "cli"}
        and again.changes() == []
    )

    again.publish(text="moves things")

    again.read(limit=1)

    assert set(again.changes()) == {"dataset", "inbox"}

    assert again.load(state).save(state).changes() == []


def test_front_ends_use_the_object(
    env,
    capsys,
    tmp_path,
    monkeypatch,
):

    amo = Amoorion(env).use("dryrun")

    monkeypatch.setenv(
        "AMOORION_SECRET_API_TOKEN",
        "t",
    )

    client = TestClient(amo.api())

    auth = {"Authorization": "Bearer t"}

    assert (
        client.post(
            "/methods/read",
            json={"platform": "dryrun", "limit": 1},
            headers=auth,
        ).status_code
        == 200
    )

    assert (tmp_path / "one.sqlite3").exists()

    assert amo.cli("--json", "plugins") == 0

    assert "dryrun" in capsys.readouterr().out

    assert "publish" in {
        tool.name for tool in amo.mcp()._tool_manager.list_tools()
    }

    with pytest.raises(AmoorionError):
        Amoorion(flags={"mode": "nowhere"}).run()
