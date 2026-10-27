"""bitwarden backend: Bitwarden / Vaultwarden through the `bw` CLI.

Bitwarden decrypts on the client, so amoorion asks `bw`, logged in and
unlocked beforehand (`task vault:login`: `bw login`, then `bw unlock --raw`
gives the session, written into .env; bw itself by npm into tools/,
`task vault:tools`):

    AMOORION_VAULT=bitwarden
    AMOORION_VAULT_TOKEN=<session from bw unlock --raw>
    AMOORION_VAULT_ADDR=<server URL>    optional: refuse if bw talks to another
    AMOORION_VAULT_PATH=<prefix>        optional: item names, default `amoorion`
    AMOORION_BW=<path of bw>            optional: else bw on PATH, else tools/'s

Secret `bluesky/password` is the item named `amoorion/bluesky`: keys
`username`, `password`, `totp`, `uri` and `notes` come from the item's login
and notes, any other key from the custom field of that name. The session goes
to `bw` through its environment (BW_SESSION), never on the command line.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, ClassVar

from amoorion.core import AmoorionError
from amoorion.vault.base import BACKENDS, PREFIX, Vault, VaultLink

LOGIN_KEYS = ("username", "password", "totp")
# Where `task vault:tools` (npm, tools/package.json) puts bw in a checkout.
NPM_BW = Path("tools") / "node_modules" / ".bin" / "bw"


def find_bw() -> str | None:
    if binary := os.environ.get("AMOORION_BW"):
        return binary
    if binary := shutil.which("bw"):
        return binary
    local = Path.cwd() / NPM_BW
    return str(local) if local.is_file() else None


@BACKENDS.register
class BitwardenVault(Vault):
    name: ClassVar[str] = "bitwarden"
    description: ClassVar[str] = "Bitwarden / Vaultwarden through the bw CLI"

    def __init__(self, link: VaultLink) -> None:
        super().__init__(link)
        self.prefix = link.path or PREFIX
        self._items: dict[str, dict[str, Any]] = {}
        self._checked = False

    def _bw(self, *args: str) -> Any:
        binary = find_bw()
        if binary is None:
            raise AmoorionError("the Bitwarden CLI `bw` is not on PATH (nor AMOORION_BW, nor tools/node_modules/.bin/bw)")
        env = dict(os.environ)
        if self.link.token:
            env["BW_SESSION"] = self.link.token
        done = subprocess.run(
            [binary, "--nointeraction", *args], env=env, capture_output=True, text=True, timeout=60, check=False
        )
        if done.returncode != 0:
            raise AmoorionError(f"bw {args[0]} failed: {done.stderr.strip() or done.stdout.strip()}")
        return json.loads(done.stdout)

    def _check(self) -> None:
        if self._checked:
            return
        status = self._bw("status")
        if status.get("status") != "unlocked":
            raise AmoorionError(
                f"Bitwarden vault is {status.get('status')}: run `task vault:login` (or `bw unlock --raw` into AMOORION_VAULT_TOKEN)"
            )
        if self.link.addr and status.get("serverUrl", "").rstrip("/") != self.link.addr.rstrip("/"):
            raise AmoorionError(f"bw talks to {status.get('serverUrl')}, not to {self.link.addr}")
        self._checked = True

    def _item(self, platform: str) -> dict[str, Any]:
        if platform not in self._items:
            self._check()
            wanted = f"{self.prefix}/{platform}"
            found = [item for item in self._bw("list", "items", "--search", wanted) if item.get("name") == wanted]
            if len(found) != 1:
                raise AmoorionError(f"Bitwarden has {len(found)} items named {wanted!r}, needs exactly one")
            self._items[platform] = found[0]
        return self._items[platform]

    def get(self, name: str) -> str:
        platform, key = self.split(name)
        item = self._item(platform)
        login = item.get("login") or {}
        if key in LOGIN_KEYS:
            value = login.get(key)
        elif key == "uri":
            value = next((uri.get("uri") for uri in login.get("uris") or []), None)
        elif key == "notes":
            value = item.get("notes")
        else:
            value = next((field.get("value") for field in item.get("fields") or [] if field.get("name") == key), None)
        if not value:
            raise AmoorionError(f"secret {name!r} not found in Bitwarden item {item['name']!r}")
        return value
