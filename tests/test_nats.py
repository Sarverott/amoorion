"""NATS against a fake client: what amoorion publishes and keeps (no server is needed)."""

import asyncio
import json
from types import SimpleNamespace

import pytest

import amoorion.nats.base as bus
from amoorion.daemon.base import services
from amoorion.inbox import Inbox
from amoorion.methods import METHODS
from amoorion.vault import VaultLink, open_vault


class FakeClient:
    published: list[tuple[str, bytes]] = []
    options: dict = {}
    fail = False
    callback = None

    async def publish(self, subject, body):
        self.published.append((subject, body))

    async def flush(self, timeout=None):
        pass

    async def close(self):
        pass

    async def drain(self):
        pass

    async def subscribe(self, subject, cb=None):
        type(self).subject, type(self).callback = subject, cb


async def connect(server, **options):
    if FakeClient.fail:
        raise OSError("no servers available")
    FakeClient.server, FakeClient.options = server, options
    return FakeClient()


@pytest.fixture
def vault(monkeypatch):
    FakeClient.published, FakeClient.fail, FakeClient.options = [], False, {}
    monkeypatch.setattr(bus.nats, "connect", connect)
    monkeypatch.setenv("AMOORION_NATS", "nats://bus.test:4222")
    monkeypatch.delenv("AMOORION_NATS_PREFIX", raising=False)
    monkeypatch.delenv("AMOORION_SECRET_NATS_TOKEN", raising=False)
    return open_vault(VaultLink(kind="env"))


def publish(vault):
    return METHODS.get("publish")(vault).run(METHODS.get("publish").Params(to=["dryrun"], text="hi"))


def test_a_method_that_changes_something_announces_its_result(vault):
    [result] = publish(vault)
    assert result.ok
    subjects = [subject for subject, _ in FakeClient.published]
    assert subjects == ["amoorion.methods.publish"]
    assert json.loads(FakeClient.published[0][1])[0]["platform"] == "dryrun"


def test_a_read_only_method_announces_nothing(vault):
    METHODS.get("plugins")(vault).run(METHODS.get("plugins").Params())
    assert FakeClient.published == []


def test_off_without_the_server(vault, monkeypatch):
    monkeypatch.delenv("AMOORION_NATS")
    publish(vault)
    assert FakeClient.published == []


def test_nats_down_never_fails_the_method(vault):
    FakeClient.fail = True
    assert publish(vault)[0].ok


def test_the_token_comes_from_the_vault(vault, monkeypatch):
    monkeypatch.setenv("AMOORION_SECRET_NATS_TOKEN", "tok")
    publish(vault)
    assert FakeClient.options["token"] == "tok"


def test_the_service_keeps_what_comes_in(vault, tmp_path):
    inbox = Inbox(tmp_path / "inbox.sqlite3")
    service = bus.NatsService("nats://bus.test:4222", vault, inbox)

    async def scenario():
        task = asyncio.create_task(service.run())
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        assert FakeClient.subject == "amoorion.in.>"
        await FakeClient.callback(SimpleNamespace(subject="amoorion.in.ci", data=b'{"text": "built", "author": "bot"}'))
        await FakeClient.callback(SimpleNamespace(subject="amoorion.in.ci", data=b"plain"))
        await service.stop()
        await task

    asyncio.run(scenario())
    kept = {message.text: message for message in inbox.list()}
    assert kept["built"].platform == "nats:ci" and kept["built"].author.handle == "bot"
    assert "plain" in kept


def test_the_daemon_runs_it_only_when_on(vault, monkeypatch):
    assert "nats" in [service.name for service in services("127.0.0.1", 0)]
    monkeypatch.delenv("AMOORION_NATS")
    assert "nats" not in [service.name for service in services("127.0.0.1", 0)]
