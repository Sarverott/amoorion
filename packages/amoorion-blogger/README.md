# amoorion-blogger

Blogger plugin of [amoorion](https://github.com/Sarverott/amoorion): posts by e-mail to the blog's
secret posting address (Blogger → Settings → Email → Post using email).

Secrets in amoorion's vault:

- `blogger/address`: the secret address, `<name>.<secret>@blogger.com`
- `blogger/smtp-uri`: the mail server and account that sends,
  `smtps://user@host:465` (TLS) or `smtp://user@host:587` (STARTTLS);
  unencrypted mail is never sent
- `blogger/smtp-password`
- optional `blogger/from`: the sender address, default the SMTP user

The title becomes the subject (or the first line when there is no title).
Posting by mail gives no id or link back, and can neither read nor reply.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/blogger.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/blogger.html.md)
- [PyPI](https://pypi.org/project/amoorion-blogger/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-blogger) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-blogger/src/amoorion_blogger/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Blogger Help](https://support.google.com/blogger/)
