# amoorion-email

E-mail plugin of [amoorion](https://github.com/Sarverott/amoorion): post (send
to one address), read a mailbox and reply to the sender. Mail only ever goes
encrypted.

Secrets in amoorion's vault:

- `email/to`: where a post goes
- `email/smtp-uri`: `smtps://user@host:465` (TLS) or `smtp://user@host:587` (STARTTLS)
- `email/smtp-password`
- `email/imap-uri`: `imaps://user@host:993` (TLS) or `imap://user@host:143` (STARTTLS)
- `email/imap-password`
- optional `email/from`: the sender address, default the SMTP user
- optional `email/mailbox`: the mailbox read, default INBOX

The title becomes the subject (or the first line when there is no title).
Reading leaves mail unread. Mail is not deleted through amoorion.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/email.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/email.html.md)
- [PyPI](https://pypi.org/project/amoorion-email/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-email) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-email/src/amoorion_email/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
