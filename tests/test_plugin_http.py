import pytest

from amoorion.core import AmoorionError
from amoorion.plugins import HttpPlugin
from amoorion.vault import VaultLink, open_vault


class Answer:
    def __init__(self, body=None, text="", status=400):
        self._body, self.text, self.status_code, self.content = body, text, status, b"x"
        self.ok = status < 400

    def json(self):
        if self._body is None:
            raise ValueError
        return self._body


class Somewhere(HttpPlugin):
    name = "somewhere"


@pytest.mark.parametrize(
    ("body", "text", "reason"),
    [
        ({"message": "m"}, "", "m"),
        ({"error": {"message": "nested"}}, "", "nested"),
        ({"detail": "d", "title": "t"}, "", "d"),
        (None, "plain failure", "plain failure"),
    ],
)
def test_reason_of_error_answers(body, text, reason):
    plugin = Somewhere(open_vault(VaultLink(kind="env")))
    assert plugin.reason(Answer(body, text)) == reason


def test_request_failure_names_the_platform(monkeypatch):
    import requests

    monkeypatch.setattr(requests, "request", lambda *a, **k: Answer({"message": "nope"}, status=403))
    with pytest.raises(AmoorionError, match="somewhere /x answered 403: nope"):
        Somewhere(open_vault(VaultLink(kind="env"))).request("GET", "https://h.test/x")
