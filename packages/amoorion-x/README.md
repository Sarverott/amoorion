# amoorion-x

X (twitter) plugin of [amoorion](https://github.com/Sarverott/amoorion): post, read, reply and delete
through the X API v2, signed with OAuth 1.0a for the account itself.

Secrets in amoorion's vault, from an app of the
[developer portal](https://developer.x.com) with read and write permission:
`x/api-key`, `x/api-secret` (the app's consumer keys), `x/access-token`,
`x/access-secret` (the account's). Optional `x/uri` (default
https://api.x.com).

Reading needs an access tier that allows reading timelines; posting works on
the free tier within its monthly limit. Posts are checked against the 280
weighted characters before sending (links count 23, most non-Latin
characters 2).

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/x.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/x.html.md)
- [PyPI](https://pypi.org/project/amoorion-x/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-x) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-x/src/amoorion_x/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [X API](https://developer.x.com/en/docs/x-api)
