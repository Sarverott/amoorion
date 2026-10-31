"""email plugin: send by SMTP, read by IMAP, reply to the sender. Only ever encrypted.

Secrets (`email/<key>`): `to` (where a post goes), `smtp-uri`
(`smtps://user@host:465` or `smtp://user@host:587`, the latter with
STARTTLS), `smtp-password`, `imap-uri` (`imaps://user@host:993` or
`imap://user@host:143`, the latter with STARTTLS), `imap-password`; optional
`from` and `mailbox` (default INBOX). Reading leaves mail unread.
"""

import imaplib
import ssl
from datetime import UTC, datetime
from email import message_from_bytes, policy
from email.message import EmailMessage
from email.utils import make_msgid, parseaddr, parsedate_to_datetime
from typing import ClassVar
from urllib.parse import unquote, urlparse

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, Plugin
from amoorion.plugins.mail import send_mail, smtp_user

PORTS = {
    "imaps": 993,
    "imap": 143,
}


def body_of(mail: EmailMessage) -> str:

    part = mail.get_body(
        preferencelist=(
            "plain",
            "html",
        )
    )

    return part.get_content().strip() if part else ""


class Email(Plugin):
    name: ClassVar[str] = "email"
    description: ClassVar[str] = "E-mail: send by SMTP, read by IMAP, reply"
    capabilities: ClassVar[frozenset[Capability]] = frozenset(
        {
            Capability.POST,
            Capability.READ,
            Capability.REPLY,
        }
    )
    secrets: ClassVar[tuple[str, ...]] = (
        "to",
        "smtp-uri",
        "smtp-password",
        "imap-uri",
        "imap-password",
    )

    def _optional(
        self,
        key: str,
        default: str,
    ) -> str:

        try:
            return self.secret(key)
        except AmoorionError:
            return default

    def _sender(self) -> str:

        return self._optional(
            "from",
            smtp_user(self.secret("smtp-uri")),
        )

    def _send(
        self,
        to: str,
        subject: str,
        text: str,
        reply_to: str | None = None,
    ) -> Message:

        mail = EmailMessage()

        mail["From"], mail["To"], mail["Subject"] = self._sender(), to, subject

        mail["Message-ID"] = make_msgid(domain="amoorion")

        if reply_to:
            mail["In-Reply-To"] = mail["References"] = reply_to

        mail.set_content(text)

        send_mail(
            self.name,
            self.secret("smtp-uri"),
            self.secret("smtp-password"),
            mail,
        )

        return Message(
            platform=self.name,
            text=f"{subject}\n\n{text}",
            id=mail["Message-ID"],
            author=Account(
                platform=self.name,
                handle=mail["From"],
            ),
            reply_to=reply_to,
            created_at=datetime.now(UTC),
        )

    def post(
        self,
        post: Post,
    ) -> Message:

        first, _, rest = post.text.partition("\n")

        subject = post.title or first.strip()[:100]

        text = post.text if post.title or not rest.strip() else rest.strip()

        if post.links:
            text += "\n\n" + "\n".join(post.links)

        if post.tags:
            text += "\n\n" + " ".join(
                "#" + tag.lstrip("#") for tag in post.tags
            )

        return self._send(
            self.secret("to"),
            subject,
            text,
        )

    def _imap(self) -> imaplib.IMAP4:

        uri = urlparse(self.secret("imap-uri"))

        if uri.scheme not in PORTS or not uri.hostname or not uri.username:
            raise AmoorionError(
                "email/imap-uri must be imaps://user@host[:port] or imap://user@host[:port]"
            )

        port, context = (
            uri.port or PORTS[uri.scheme],
            ssl.create_default_context(),
        )

        if uri.scheme == "imaps":
            client: imaplib.IMAP4 = imaplib.IMAP4_SSL(
                uri.hostname,
                port,
                ssl_context=context,
                timeout=30,
            )

        else:
            client = imaplib.IMAP4(
                uri.hostname,
                port,
                timeout=30,
            )

            client.starttls(ssl_context=context)

        client.login(
            unquote(uri.username),
            self.secret("imap-password"),
        )

        return client

    def read(
        self,
        limit: int = 20,
    ) -> list[Message]:

        messages = []

        try:
            client = self._imap()

            try:
                client.select(
                    self._optional(
                        "mailbox",
                        "INBOX",
                    ),
                    readonly=True,
                )

                _, found = client.search(
                    None,
                    "ALL",
                )

                for number in reversed(found[0].split()[-limit:]):
                    _, data = client.fetch(
                        number,
                        "(BODY.PEEK[])",
                    )

                    messages.append(self._message(data[0][1]))
            finally:
                client.logout()
        except (imaplib.IMAP4.error, OSError) as error:
            raise AmoorionError(f"email: mail not read: {error}") from None

        return messages

    def _message(
        self,
        raw: bytes,
    ) -> Message:

        mail = message_from_bytes(
            raw,
            policy=policy.default,
        )

        address = parseaddr(str(mail["From"] or ""))

        date = mail["Date"]

        return Message(
            platform=self.name,
            text=f"{mail['Subject'] or ''}\n\n{body_of(mail)}",
            id=mail["Message-ID"],
            author=Account(
                platform=self.name,
                handle=address[1],
                name=address[0] or None,
            ),
            reply_to=mail["In-Reply-To"],
            created_at=parsedate_to_datetime(date) if date else None,
        )

    def reply(
        self,
        to: Message,
        text: str,
    ) -> Message:

        if not to.id or not to.author:
            raise AmoorionError(
                "email needs the Message-ID and the sender of the mail to reply to"
            )

        subject = to.text.partition("\n")[0].strip()

        subject = (
            subject if subject.lower().startswith("re:") else f"Re: {subject}"
        )

        return self._send(
            to.author.handle,
            subject,
            text,
            reply_to=to.id,
        )

    def profile(self) -> str:

        return smtp_user(self.secret("smtp-uri"))
