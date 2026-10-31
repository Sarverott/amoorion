"""HttpPlugin: what plugins speaking JSON over HTTP share.

`request` sends, turns network failures and error answers into
`AmoorionError` with the platform's own reason, and returns the JSON body.
Plugins whose platform words its errors differently override `reason`;
plugins whose URL carries a secret (a bot token, a webhook) name it in
`hidden`, so no error shows it.
"""

from typing import Any, ClassVar
from urllib.parse import urlparse

import requests

from amoorion.core import AmoorionError
from amoorion.plugins.base import Plugin

REASON_KEYS = (
    "message",
    "error",
    "detail",
    "title",
    "error_description",
)


class HttpPlugin(Plugin):
    """A plugin talking to an HTTP API: shared requests, errors and hiding of secrets.

    Its errors say what the platform answered, and never contain a secret (`hidden`).
    """

    timeout: ClassVar[float] = 30

    def reason(
        self,
        response: requests.Response,
    ) -> str:
        """What the platform said went wrong: from the usual keys of its JSON, or the raw text."""

        try:
            body = response.json()
        except ValueError:
            return response.text[:200]

        if isinstance(body, dict):
            for key in REASON_KEYS:
                value = body.get(key)

                if isinstance(value, dict):
                    value = value.get("message")

                if isinstance(value, str) and value:
                    return value

        return response.text[:200]

    def hidden(self) -> list[str]:
        """Secrets that are part of the URLs and must not appear in errors."""

        return []

    def _error(
        self,
        text: str,
    ) -> AmoorionError:
        """An error with every secret masked: URLs and answers can contain them."""

        for secret in self.hidden():
            if secret:
                text = text.replace(
                    secret,
                    "***",
                )

        return AmoorionError(text)

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Any:
        """One request with a timeout; a network failure or an error status raises `AmoorionError`."""

        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as error:
            raise self._error(f"{self.name} unreachable: {error}") from None

        if not response.ok:
            raise self._error(
                f"{self.name} {urlparse(url).path} answered {response.status_code}: {self.reason(response)}"
            )

        return response.json() if response.content else {}
