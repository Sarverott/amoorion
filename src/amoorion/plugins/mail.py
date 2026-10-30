"""Sending mail: what the plugins that speak SMTP share (blogger, email). Only ever encrypted."""

import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import unquote, urlparse

from amoorion.core import AmoorionError

PORTS = {"smtps": 465, "smtp": 587}


def smtp_user(uri: str) -> str:
    return unquote(urlparse(uri).username or "")


def send_mail(name: str, smtp_uri: str, password: str, mail: EmailMessage) -> None:
    """`smtp_uri` is `smtps://user@host[:port]` (TLS) or `smtp://user@host[:port]` (STARTTLS)."""
    uri = urlparse(smtp_uri)
    if uri.scheme not in PORTS or not uri.hostname or not uri.username:
        raise AmoorionError(f"{name}/smtp-uri must be smtps://user@host[:port] or smtp://user@host[:port]")
    user, port, context = unquote(uri.username), uri.port or PORTS[uri.scheme], ssl.create_default_context()
    try:
        if uri.scheme == "smtps":
            server = smtplib.SMTP_SSL(uri.hostname, port, context=context, timeout=30)
        else:
            server = smtplib.SMTP(uri.hostname, port, timeout=30)
        with server:
            if uri.scheme == "smtp":
                server.starttls(context=context)
            server.login(user, password)
            server.send_message(mail)
    except (smtplib.SMTPException, OSError) as error:
        raise AmoorionError(f"{name}: mail not sent: {error}") from None
