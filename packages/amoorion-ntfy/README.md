# amoorion-ntfy

ntfy plugin of [amoorion](https://github.com/Sarverott/amoorion): push
notifications to one topic, and read what the topic holds. Also a
notification target: set `AMOORION_NOTIFY=ntfy` in `.env` and everything the
hooks receive is sent there too.

Secrets in amoorion's vault: `ntfy/topic`; optional `ntfy/uri` (the server,
default https://ntfy.sh) and `ntfy/token` (for protected topics). A topic on a
public server is readable by anyone who knows its name, so pick a long one.

A post's title and tags become the notification's, its first link what a click
opens. ntfy keeps messages only for a while (12 hours on ntfy.sh), so `read`
sees no further back. It can't reply or delete.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/ntfy.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/ntfy.html.md)
- [PyPI](https://pypi.org/project/amoorion-ntfy/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-ntfy) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-ntfy/src/amoorion_ntfy/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [ntfy docs](https://docs.ntfy.sh/publish/)
