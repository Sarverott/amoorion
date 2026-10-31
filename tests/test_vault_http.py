"""The http backend against a local server shaped like Vault's KV v2 API."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from amoorion.core import AmoorionError
from amoorion.vault import HttpVault, VaultLink, open_vault

ENTRIES = {
    "/v1/secret/data/amoorion/bluesky": {
        "password": "app-pass",
        "handle": "@me",
    }
}


class FakeVault(BaseHTTPRequestHandler):
    calls: list[str] = []

    def do_GET(self):

        self.calls.append(self.path)

        if self.headers.get("X-Vault-Token") != "tok":
            self.send_response(403)

            self.end_headers()

            return

        data = ENTRIES.get(self.path)

        self.send_response(200 if data else 404)

        self.end_headers()

        if data:
            self.wfile.write(
                json.dumps(
                    {
                        "data": {
                            "data": data,
                            "metadata": {"version": 1},
                        }
                    }
                ).encode()
            )

    def log_message(
        self,
        *args,
    ):

        pass


@pytest.fixture(scope="module")
def addr():

    server = ThreadingHTTPServer(
        (
            "127.0.0.1",
            0,
        ),
        FakeVault,
    )

    threading.Thread(
        target=server.serve_forever,
        daemon=True,
    ).start()

    yield f"http://127.0.0.1:{server.server_port}"

    server.shutdown()


def test_reads_keys_of_one_entry_once(addr):

    FakeVault.calls.clear()

    vault = open_vault(
        VaultLink(
            kind="http",
            addr=addr,
            token="tok",
        )
    )

    assert isinstance(vault, HttpVault)

    assert vault.get("bluesky/password") == "app-pass"

    assert vault.get("bluesky/handle") == "@me"

    assert FakeVault.calls == ["/v1/secret/data/amoorion/bluesky"]


def test_missing_entry_key_and_wrong_token(addr):

    vault = open_vault(
        VaultLink(
            kind="http",
            addr=addr,
            token="tok",
        )
    )

    with pytest.raises(
        AmoorionError, match="no entry secret/amoorion/telegram"
    ):
        vault.get("telegram/token")

    with pytest.raises(AmoorionError, match="'bluesky/totp' not found"):
        vault.get("bluesky/totp")

    with pytest.raises(AmoorionError, match="answered 403"):
        open_vault(
            VaultLink(
                kind="http",
                addr=addr,
                token="bad",
            )
        ).get("bluesky/password")


def test_custom_mount_and_prefix(addr):

    FakeVault.calls.clear()

    with pytest.raises(AmoorionError):
        open_vault(
            VaultLink(
                kind="http",
                addr=addr,
                token="tok",
                path="kv/team",
            )
        ).get("bluesky/password")

    assert FakeVault.calls == ["/v1/kv/data/team/bluesky"]


def test_needs_addr_and_token():

    with pytest.raises(AmoorionError, match="AMOORION_VAULT_ADDR"):
        open_vault(VaultLink(kind="http"))


def test_unreachable():

    vault = open_vault(
        VaultLink(
            kind="http",
            addr="http://127.0.0.1:9",
            token="tok",
        )
    )

    with pytest.raises(AmoorionError, match="unreachable"):
        vault.get("bluesky/password")
