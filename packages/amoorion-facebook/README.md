# amoorion-facebook

Facebook plugin of [amoorion](../../README.md): post on a Facebook Page, read
its posts, reply as comments, and delete posts or comments, through the Graph
API.

Secrets in amoorion's vault: `facebook/page-id` and `facebook/page-token` (a
Page access token with `pages_manage_posts`, `pages_read_engagement` and
`pages_manage_engagement`). Optional `facebook/uri`: the Graph API with its
version, default `https://graph.facebook.com/v24.0`.

Posting to personal profiles is not possible through the Graph API; only
Pages.
