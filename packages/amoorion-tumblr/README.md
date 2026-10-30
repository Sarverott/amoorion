# amoorion-tumblr

Tumblr plugin of [amoorion](https://github.com/Sarverott/amoorion): post, read and delete through the
Tumblr API v2 (Neue Post Format), signed with OAuth 1.0a.

Secrets in amoorion's vault, from an app [registered at
Tumblr](https://www.tumblr.com/oauth/apps): `tumblr/consumer-key`,
`tumblr/consumer-secret`, `tumblr/token`, `tumblr/token-secret` (the
account's), and `tumblr/blog` (the blog, e.g. `myblog.tumblr.com`). Optional
`tumblr/uri` (default https://api.tumblr.com).

A post's title becomes a heading, its links link blocks, its tags Tumblr
tags. Tumblr's API has no plain reply (only reblogs), so `reply` is not
offered.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/tumblr.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/tumblr.html.md)
- [PyPI](https://pypi.org/project/amoorion-tumblr/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-tumblr) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-tumblr/src/amoorion_tumblr/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Tumblr API](https://www.tumblr.com/docs/en/api/v2)
