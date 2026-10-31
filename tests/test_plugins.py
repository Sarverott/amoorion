import pytest

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import (
    Capability,
    Plugin,
    Unsupported,
    load_plugins,
    open_plugin,
)
from amoorion.vault import VaultLink, open_vault


@pytest.fixture
def vault():

    return open_vault(VaultLink(kind="env"))


def test_dryrun_is_built_in():

    assert "dryrun" in load_plugins()


def test_plugin_package_imported_before_amoorion_plugins():
    """A plugin package imports amoorion.plugins itself; loading must not catch it half-imported."""

    import subprocess

    import sys

    code = (
        "import amoorion_bluesky; from amoorion.plugins import FAILED, load_plugins; "
        "assert 'bluesky' in load_plugins(), FAILED"
    )

    subprocess.run(
        [
            sys.executable,
            "-c",
            code,
        ],
        check=True,
    )


def test_dryrun_posts_reads_and_replies(vault):

    plugin = open_plugin(
        "dryrun",
        vault,
    )

    posted = plugin.post(
        Post(
            text="hello",
            title="Hi",
        )
    )

    assert posted.text == "Hi\n\nhello" and posted.id

    answer = plugin.reply(
        posted,
        "hello back",
    )

    assert answer.reply_to == posted.id

    assert plugin.read(2) == [answer, posted]


def test_missing_capability_is_unsupported(vault):

    class Mute(Plugin):
        name = "mute"

    with pytest.raises(Unsupported, match="mute can't post"):
        Mute(vault).post(Post(text="x"))

    assert Capability.POST not in Mute.capabilities


def test_plugin_secret_is_named_by_platform(
    vault,
    monkeypatch,
):

    monkeypatch.setenv(
        "AMOORION_SECRET_DRYRUN_TOKEN",
        "t",
    )

    assert open_plugin("dryrun", vault).secret("token") == "t"


def test_unknown_plugin(vault):

    with pytest.raises(AmoorionError):
        open_plugin(
            "nope",
            vault,
        )


class FakeEntryPoint:
    def __init__(
        self,
        name,
        target,
    ):

        self.name, self.value, self._target = name, f"fake:{name}", target

    def load(self):

        if isinstance(self._target, Exception):
            raise self._target

        return self._target


def test_dryrun_comes_from_an_entry_point():

    from importlib.metadata import entry_points

    from amoorion.plugins import ENTRY_POINTS

    assert "dryrun" in {
        entry_point.name for entry_point in entry_points(group=ENTRY_POINTS)
    }


def test_outside_plugins_load_and_failures_are_kept(monkeypatch):

    from amoorion.plugins import loading

    class Outside(Plugin):
        name = "outside"

    monkeypatch.setattr(
        loading,
        "PLUGINS",
        loading.Registry("plugin"),
    )

    monkeypatch.setattr(
        loading,
        "FAILED",
        {},
    )

    monkeypatch.setattr(
        loading,
        "entry_points",
        lambda group: [
            FakeEntryPoint("outside", Outside),
            FakeEntryPoint("broken", ImportError("no module named broken")),
            FakeEntryPoint("notaplugin", object),
            FakeEntryPoint("misnamed", Outside),
        ],
    )

    loading.load_plugins()

    assert loading.PLUGINS.names() == ["outside"]

    assert set(loading.FAILED) == {"broken", "notaplugin", "misnamed"}

    assert "ImportError" in loading.FAILED["broken"]
