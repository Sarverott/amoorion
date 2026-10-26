# amoorion-tumblr

Tumblr plugin of [amoorion](../../README.md): post and read through the Tumblr
API v2 (Neue Post Format), signed with OAuth 1.0a.

Secrets in amoorion's vault, from an app [registered at
Tumblr](https://www.tumblr.com/oauth/apps): `tumblr/consumer-key`,
`tumblr/consumer-secret`, `tumblr/token`, `tumblr/token-secret` (the
account's), and `tumblr/blog` (the blog, e.g. `myblog.tumblr.com`). Optional
`tumblr/uri` (default https://api.tumblr.com).

A post's title becomes a heading, its links link blocks, its tags Tumblr
tags. Tumblr's API has no plain reply (only reblogs), so `reply` is not
offered.
