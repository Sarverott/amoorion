# amoorion-mastodon

Mastodon plugin of [amoorion](https://github.com/Sarverott/amoorion): post, read, reply and delete
through the REST API of a Mastodon (or compatible) server.

Secrets in amoorion's vault: `mastodon/uri` (the server, e.g.
https://mastodon.social) and `mastodon/token` (access token of an
application from Preferences → Development, scopes `read:accounts
read:statuses write:statuses`; deleting is part of `write:statuses`).

The server's character limit is asked once (`/api/v2/instance`, 500 when it
doesn't say) and checked before sending; links count as 23 characters.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/mastodon.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/mastodon.html.md)
- [PyPI](https://pypi.org/project/amoorion-mastodon/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-mastodon) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-mastodon/src/amoorion_mastodon/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Mastodon API](https://docs.joinmastodon.org/api/)
