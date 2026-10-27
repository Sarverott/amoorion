# amoorion-matrix

Matrix plugin of [amoorion](../../README.md): posts, reads, replies and
deletes (redacts) in one room through the client-server API of any homeserver.

Secrets in amoorion's vault: `matrix/uri` (the homeserver, e.g.
https://matrix.org), `matrix/token` (an access token of the account, e.g.
Element → Settings → Help & About → Access Token; better a separate bot
account) and `matrix/room` (the room's id `!…:server` or an alias
`#…:server`). The account has to be a member of the room.

End-to-end encrypted rooms are not supported yet: amoorion sends and reads
plain events, so use a room without encryption.
