"""The blogger plugin with smtplib replaced by a recorder (no mail leaves the machine)."""

import smtplib

import pytest
from amoorion_blogger.base import compose

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import Unsupported, open_plugin
from amoorion.vault import VaultLink, open_vault


class Recorder:
    sessions: list["Recorder"] = []
    fail_login = False

    def __init__(
        self,
        host,
        port,
        context=None,
        timeout=None,
    ):

        self.host, self.port, self.tls, self.calls, self.sent = (
            host,
            port,
            context is not None,
            [],
            [],
        )

        self.sessions.append(self)

    def __enter__(self):

        return self

    def __exit__(
        self,
        *exc,
    ):

        self.calls.append("quit")

    def starttls(
        self,
        context=None,
    ):

        self.tls = True

        self.calls.append("starttls")

    def login(
        self,
        user,
        password,
    ):

        self.calls.append(f"login {user}")

        if self.fail_login or password != "pw":
            raise smtplib.SMTPAuthenticationError(
                535,
                b"bad credentials",
            )

    def send_message(
        self,
        mail,
    ):

        assert self.tls, "mail sent without TLS"

        self.sent.append(mail)


@pytest.fixture
def blogger(monkeypatch):

    Recorder.sessions = []

    monkeypatch.setattr(
        smtplib,
        "SMTP",
        Recorder,
    )

    monkeypatch.setattr(
        smtplib,
        "SMTP_SSL",
        Recorder,
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_BLOGGER_ADDRESS",
        "me.secret@blogger.com",
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_BLOGGER_SMTP_URI",
        "smtps://me%40mail.test@mail.test",
    )

    monkeypatch.setenv(
        "AMOORION_SECRET_BLOGGER_SMTP_PASSWORD",
        "pw",
    )

    monkeypatch.delenv(
        "AMOORION_SECRET_BLOGGER_FROM",
        raising=False,
    )

    return open_plugin(
        "blogger",
        open_vault(VaultLink(kind="env")),
    )


def test_post_by_mail_over_tls(blogger):

    message = blogger.post(
        Post(
            title="Hello",
            text="body",
            links=["https://a"],
            tags=["x"],
        )
    )

    [session] = Recorder.sessions

    assert (session.host, session.port, session.tls) == ("mail.test", 465, True)

    assert session.calls == ["login me@mail.test", "quit"]

    [mail] = session.sent

    assert (
        mail["To"] == "me.secret@blogger.com" and mail["From"] == "me@mail.test"
    )

    assert (
        mail["Subject"] == "Hello"
        and mail.get_content().strip() == "body\n\nhttps://a\n\n#x"
    )

    assert message.id == mail["Message-ID"]


def test_starttls_on_587(
    blogger,
    monkeypatch,
):

    monkeypatch.setenv(
        "AMOORION_SECRET_BLOGGER_SMTP_URI",
        "smtp://me@mail.test",
    )

    blogger.post(Post(text="x"))

    assert (
        Recorder.sessions[0].port == 587
        and Recorder.sessions[0].calls[0] == "starttls"
    )


def test_unencrypted_or_bad_uri_refused(
    blogger,
    monkeypatch,
):

    for uri in ("plain://me@mail.test", "smtps://mail.test"):
        monkeypatch.setenv(
            "AMOORION_SECRET_BLOGGER_SMTP_URI",
            uri,
        )

        with pytest.raises(AmoorionError, match="must be smtps://"):
            blogger.post(Post(text="x"))

    assert Recorder.sessions == []


def test_login_failure(
    blogger,
    monkeypatch,
):

    monkeypatch.setenv(
        "AMOORION_SECRET_BLOGGER_SMTP_PASSWORD",
        "wrong",
    )

    with pytest.raises(AmoorionError, match="mail not sent"):
        blogger.post(Post(text="x"))


def test_only_post(blogger):

    with pytest.raises(Unsupported):
        blogger.read()


def test_subject_from_first_line():

    assert compose(Post(text="Title line\nrest")) == ("Title line", "rest")

    assert compose(Post(text="only")) == ("only", "only")
