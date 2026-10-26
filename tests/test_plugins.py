import pytest

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import PLUGINS, Capability, Plugin, Unsupported, open_plugin
from amoorion.vault import VaultLink, open_vault


@pytest.fixture
def vault():
    return open_vault(VaultLink(kind="env"))


def test_dryrun_is_built_in():
    assert "dryrun" in PLUGINS


def test_dryrun_posts_reads_and_replies(vault):
    plugin = open_plugin("dryrun", vault)
    posted = plugin.post(Post(text="hello", title="Hi"))
    assert posted.text == "Hi\n\nhello" and posted.id
    answer = plugin.reply(posted, "hello back")
    assert answer.reply_to == posted.id
    assert plugin.read(2) == [answer, posted]


def test_missing_capability_is_unsupported(vault):
    class Mute(Plugin):
        name = "mute"

    with pytest.raises(Unsupported, match="mute can't post"):
        Mute(vault).post(Post(text="x"))
    assert Capability.POST not in Mute.capabilities


def test_plugin_secret_is_named_by_platform(vault, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_DRYRUN_TOKEN", "t")
    assert open_plugin("dryrun", vault).secret("token") == "t"


def test_unknown_plugin(vault):
    with pytest.raises(AmoorionError):
        open_plugin("nope", vault)
