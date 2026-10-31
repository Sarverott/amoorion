"""The email plugin with smtplib and imaplib replaced by fakes (no mail leaves the machine)."""

import imaplib
import smtplib
from email.message import EmailMessage

import pytest

from amoorion.core import AmoorionError
from amoorion.models import Post
from amoorion.plugins import open_plugin
from amoorion.vault import VaultLink, open_vault


class Smtp:
    sent: list[EmailMessage] = []

    def __init__(
        self,
        host,
        port,
        context=None,
        timeout=None,
    ):

        self.tls = context is not None

    def __enter__(self):

        return self

    def __exit__(
        self,
        *exc,
    ):

        pass

    def starttls(
        self,
        context=None,
    ):

        self.tls = True

    def login(
        self,
        user,
        password,
    ):

        assert (user, password) == ("me@mail.test", "pw")

    def send_message(
        self,
        mail,
    ):

        assert self.tls, "mail sent without TLS"

        self.sent.append(mail)


def raw(number):

    return (
        f"From: Ann <ann@mail.test>\r\nSubject: Hello {number}\r\nMessage-ID: <{number}@mail.test>\r\n"
        f"Date: Mon, 06 Oct 2026 10:00:00 +0000\r\n\r\nBody {number}\r\n"
    ).encode()


class Imap:
    error = imaplib.IMAP4.error
    readonly = None
    fetched: list[str] = []
    fail = False

    def __init__(
        self,
        host,
        port,
        ssl_context=None,
        timeout=None,
    ):

        self.tls = ssl_context is not None

    def starttls(
        self,
        ssl_context=None,
    ):

        self.tls = True

    def login(
        self,
        user,
        password,
    ):

        assert self.tls, "logged in without TLS"

        if self.fail:
            raise self.error("bad credentials")

    def select(
        self,
        mailbox,
        readonly=False,
    ):

        type(self).readonly = readonly

    def search(
        self,
        charset,
        criteria,
    ):

        return "OK", [b"1 2 3"]

    def fetch(
        self,
        number,
        parts,
    ):

        self.fetched.append(parts)

        return "OK", [(b"", raw(number.decode()))]

    def logout(self):

        pass


@pytest.fixture
def email(monkeypatch):

    Smtp.sent, Imap.fail, Imap.fetched = [], False, []

    monkeypatch.setattr(
        smtplib,
        "SMTP",
        Smtp,
    )

    monkeypatch.setattr(
        smtplib,
        "SMTP_SSL",
        Smtp,
    )

    monkeypatch.setattr(
        imaplib,
        "IMAP4",
        Imap,
    )

    monkeypatch.setattr(
        imaplib,
        "IMAP4_SSL",
        Imap,
    )

    for key, value in {
        "TO": "you@mail.test",
        "SMTP_URI": "smtps://me%40mail.test@mail.test",
        "SMTP_PASSWORD": "pw",
        "IMAP_URI": "imap://me%40mail.test@mail.test",
        "IMAP_PASSWORD": "pw",
    }.items():
        monkeypatch.setenv(
            f"AMOORION_SECRET_EMAIL_{key}",
            value,
        )

    return open_plugin(
        "email",
        open_vault(VaultLink(kind="env")),
    )


def test_post_sends_to_the_address(email):

    sent = email.post(
        Post(
            text="Line one\nthe rest",
            links=["https://x.test"],
            tags=["a"],
        )
    )

    [mail] = Smtp.sent

    assert (
        mail["To"] == "you@mail.test"
        and mail["From"] == "me@mail.test"
        and mail["Subject"] == "Line one"
    )

    assert (
        "the rest" in mail.get_content()
        and "https://x.test" in mail.get_content()
        and "#a" in mail.get_content()
    )

    assert sent.id == mail["Message-ID"]


def test_read_is_newest_first_and_leaves_mail_unread(email):

    first, second = email.read(limit=2)

    assert first.text == "Hello 3\n\nBody 3" and second.id == "<2@mail.test>"

    assert first.author.handle == "ann@mail.test" and first.author.name == "Ann"

    assert Imap.readonly is True and set(Imap.fetched) == {"(BODY.PEEK[])"}


def test_reply_goes_to_the_sender_in_the_thread(email):

    original = email.read(limit=1)[0]

    sent = email.reply(
        original,
        "Thanks",
    )

    [mail] = Smtp.sent

    assert mail["To"] == "ann@mail.test" and mail["Subject"] == "Re: Hello 3"

    assert (
        mail["In-Reply-To"] == "<3@mail.test>"
        and sent.reply_to == "<3@mail.test>"
    )


def test_failures_say_so(
    email,
    monkeypatch,
):

    Imap.fail = True

    with pytest.raises(AmoorionError, match="mail not read"):
        email.read()

    monkeypatch.setenv(
        "AMOORION_SECRET_EMAIL_IMAP_URI",
        "http://me@mail.test",
    )

    with pytest.raises(AmoorionError, match="imap-uri"):
        email.read()
