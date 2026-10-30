# amoorion-matrix

Matrix plugin of [amoorion](https://github.com/Sarverott/amoorion): posts, reads, replies and
deletes (redacts) in one room through the client-server API of any homeserver.

Secrets in amoorion's vault: `matrix/uri` (the homeserver, e.g.
https://matrix.org), `matrix/token` (an access token of the account, e.g.
Element → Settings → Help & About → Access Token; better a separate bot
account) and `matrix/room` (the room's id `!…:server` or an alias
`#…:server`). The account has to be a member of the room.

End-to-end encrypted rooms are not supported yet: amoorion sends and reads
plain events, so use a room without encryption.

## Links

- [Documentation](https://amoorion.readthedocs.io/en/latest/platforms/matrix.html) · [as Markdown](https://amoorion.readthedocs.io/en/latest/platforms/matrix.html.md)
- [PyPI](https://pypi.org/project/amoorion-matrix/)
- [GitHub](https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-matrix) · [issues](https://github.com/Sarverott/amoorion/issues)
- [What its vault entry holds](https://github.com/Sarverott/amoorion/blob/master/packages/amoorion-matrix/src/amoorion_matrix/schema.vault.json)
- [amoorion](https://github.com/Sarverott/amoorion) · [its documentation](https://amoorion.readthedocs.io/en/latest/) · [its web page](https://sarverott.github.io/amoorion/)
- [Matrix client-server API](https://spec.matrix.org/latest/client-server-api/)
