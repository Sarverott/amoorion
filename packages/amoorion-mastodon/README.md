# amoorion-mastodon

Mastodon plugin of [amoorion](../../README.md): post, read, reply and delete
through the REST API of a Mastodon (or compatible) server.

Secrets in amoorion's vault: `mastodon/uri` (the server, e.g.
https://mastodon.social) and `mastodon/token` (access token of an
application from Preferences → Development, scopes `read:accounts
read:statuses write:statuses`; deleting is part of `write:statuses`).

The server's character limit is asked once (`/api/v2/instance`, 500 when it
doesn't say) and checked before sending; links count as 23 characters.
