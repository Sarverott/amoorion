# amoorion-facebook

Facebook plugin of [amoorion](https://github.com/Sarverott/amoorion): post on a Facebook Page, read
its posts, reply as comments, and delete posts or comments, through the Graph
API.

Secrets in amoorion's vault: `facebook/page-id` and `facebook/page-token` (a
Page access token with `pages_manage_posts`, `pages_read_engagement` and
`pages_manage_engagement`). Optional `facebook/uri`: the Graph API with its
version, default `https://graph.facebook.com/v24.0`.

Posting to personal profiles is not possible through the Graph API; only
Pages.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/facebook.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/facebook.html.md)
- [PyPI](https://pypi.org/project/amoorion-facebook/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-facebook) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-facebook/src/amoorion_facebook/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Graph API, Pages](https://developers.facebook.com/docs/pages-api/)
