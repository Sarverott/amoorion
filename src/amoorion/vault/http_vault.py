"""http backend: HashiCorp Vault / OpenBao, KV version 2 over HTTP.

    AMOORION_VAULT=http
    AMOORION_VAULT_ADDR=https://vault.example.org
    AMOORION_VAULT_TOKEN=<token allowed to read the path>
    AMOORION_VAULT_PATH=<mount>/<prefix>    optional, default `secret/amoorion`

Secret `bluesky/password` is the key `password` of the KV entry
`<prefix>/bluesky` in the mount: `GET /v1/<mount>/data/<prefix>/bluesky`.
"""

from typing import Any, ClassVar

import requests

from amoorion.core import AmoorionError
from amoorion.vault.base import BACKENDS, PREFIX, Vault, VaultLink


@BACKENDS.register
class HttpVault(Vault):
    name: ClassVar[str] = "http"
    description: ClassVar[str] = "HashiCorp Vault / OpenBao, KV v2 over HTTP"

    def __init__(self, link: VaultLink) -> None:
        super().__init__(link)
        if not link.addr or not link.token:
            raise AmoorionError("the http vault needs AMOORION_VAULT_ADDR and AMOORION_VAULT_TOKEN")
        mount, _, prefix = (link.path or f"secret/{PREFIX}").strip("/").partition("/")
        self.mount, self.prefix = mount, prefix
        self.session = requests.Session()
        self.session.headers["X-Vault-Token"] = link.token
        self._entries: dict[str, dict[str, Any]] = {}

    def _entry(self, platform: str) -> dict[str, Any]:
        if platform not in self._entries:
            path = "/".join(part for part in (self.prefix, platform) if part)
            url = f"{self.link.addr.rstrip('/')}/v1/{self.mount}/data/{path}"
            try:
                response = self.session.get(url, timeout=10)
            except requests.RequestException as error:
                raise AmoorionError(f"vault at {self.link.addr} unreachable: {error}") from None
            if response.status_code == 404:
                raise AmoorionError(f"vault has no entry {self.mount}/{path}")
            if response.status_code != 200:
                raise AmoorionError(f"vault answered {response.status_code} for {self.mount}/{path}")
            self._entries[platform] = response.json()["data"]["data"] or {}
        return self._entries[platform]

    def get(self, name: str) -> str:
        platform, key = self.split(name)
        value = self._entry(platform).get(key)
        if not value:
            raise AmoorionError(f"secret {name!r} not found in the vault")
        return str(value)
