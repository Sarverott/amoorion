---
name: amoorion
description: Use amoorion to publish, read and reply on chatting and communication platforms (Bluesky, Mastodon, X, Tumblr, Blogger, Facebook, Discord, Telegram, Matrix) from one CLI, HTTP API or MCP server; secrets come from a vault. Use when asked to post to several platforms, read what came in, answer it, or check which platforms are set up.
---

# amoorion

One tool for many platforms. Every operation is a **method**; the CLI,
the HTTP API and the MCP server all expose the same methods.

## Before anything

1. `amoorion plugins`: the platforms installed and what each can do
   (`post`, `read`, `reply`).
2. `amoorion accounts`: which platforms have their secrets in the vault.
   A platform without them refuses to work; never ask the user for a
   token in the chat, it belongs in their vault.
3. Try with `dryrun` first: it sends nothing.

## Methods

```sh
amoorion publish --text "hello" --to dryrun bluesky mastodon   # changes something: confirm with the user first
amoorion --json read --platform bluesky                        # read-only
amoorion reply --platform bluesky --to "<post id>" --text "…"   # changes something: confirm first
amoorion inbox                                                 # everything read or received so far
```

`--json` gives machine-readable output. `amoorion mcp` runs the MCP server
(stdio) with the same methods as tools; the ones that change something
on a platform are not read-only.

## Rules

- Posting and replying are visible to real people: get the user's
  confirmation of the text and the platforms before running them.
- Secrets live only in the vault the user's `.env` links to; never print,
  log or commit them.
- Docs: https://amoorion.readthedocs.io (Markdown of any page: ask with
  `Accept: text/markdown`, or read https://amoorion.readthedocs.io/llms.txt).
