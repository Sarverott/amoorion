"""blogger plugin: posting by mail to the blog's secret address.

Secrets (`blogger/<key>`): `address`, `smtp-uri` (`smtps://user@host:465`
or `smtp://user@host:587`, the latter with STARTTLS), `smtp-password`;
optional `from`. Mail is only ever sent encrypted.
"""

from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import make_msgid
from typing import ClassVar

from amoorion.core import AmoorionError
from amoorion.models import Account, Message, Post
from amoorion.plugins import Capability, Plugin
from amoorion.plugins.mail import send_mail, smtp_user


def compose(post: Post) -> tuple[str, str]:
    """Subject and body of the mail."""
    body = post.text
    subject = post.title
    if not subject:
        first, _, rest = post.text.partition("\n")
        subject, body = first.strip()[:100], rest.strip() or post.text
    if post.links:
        body += "\n\n" + "\n".join(post.links)
    if post.tags:
        body += "\n\n" + " ".join("#" + tag.lstrip("#") for tag in post.tags)
    return subject, body


class Blogger(Plugin):
    name: ClassVar[str] = "blogger"
    description: ClassVar[str] = "Blogger by mail: post"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST})
    secrets: ClassVar[tuple[str, ...]] = ("address", "smtp-uri", "smtp-password")

    def _send(self, mail: EmailMessage) -> None:
        send_mail(self.name, self.secret("smtp-uri"), self.secret("smtp-password"), mail)

    def _sender(self) -> str:
        try:
            return self.secret("from")
        except AmoorionError:
            return smtp_user(self.secret("smtp-uri"))

    def post(self, post: Post) -> Message:
        subject, body = compose(post)
        mail = EmailMessage()
        mail["From"], mail["To"], mail["Subject"] = self._sender(), self.secret("address"), subject
        mail["Message-ID"] = make_msgid(domain="amoorion")
        mail.set_content(body)
        self._send(mail)
        return Message(
            platform=self.name,
            text=f"{subject}\n\n{body}",
            id=mail["Message-ID"],
            author=Account(platform=self.name, handle=mail["From"]),
            created_at=datetime.now(UTC),
        )
