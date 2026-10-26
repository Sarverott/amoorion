import pytest

from amoorion.core import AmoorionError
from amoorion.hooks import HOOKS, Forbidden
from amoorion.vault import VaultLink, open_vault


@pytest.fixture
def hook(monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_HOOKS_GENERIC_TOKEN", "tok")
    return HOOKS.get("generic")(open_vault(VaultLink(kind="env")))


def test_generic_hook_turns_payload_into_message(hook):
    message = hook.handle(b"", {"x-amoorion-token": "tok"}, {"text": "deployed", "author": "ci"})
    assert message.text == "deployed" and message.author.handle == "ci"


def test_wrong_token_is_forbidden(hook):
    with pytest.raises(Forbidden):
        hook.handle(b"", {"x-amoorion-token": "nope"}, {"text": "x"})


def test_missing_secret_refuses_everything(monkeypatch):
    monkeypatch.delenv("AMOORION_SECRET_HOOKS_GENERIC_TOKEN", raising=False)
    hook = HOOKS.get("generic")(open_vault(VaultLink(kind="env")))
    with pytest.raises(Forbidden):
        hook.handle(b"", {"x-amoorion-token": ""}, {"text": "x"})


def test_bad_payload(hook):
    with pytest.raises(AmoorionError):
        hook.handle(b"", {"x-amoorion-token": "tok"}, ["not", "a", "dict"])
