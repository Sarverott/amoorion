# amoorion-blogger

Blogger plugin of [amoorion](../../README.md): posts by e-mail to the blog's
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
