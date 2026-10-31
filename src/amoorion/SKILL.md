---
name: amoorion
description: Use amoorion to publish, read, reply, delete and search on chatting and communication platforms (Bluesky, Mastodon, X, Tumblr, Blogger, Facebook, Discord, Telegram, Matrix, ntfy, e-mail) from one CLI, Python object, HTTP API or MCP server; secrets come from a vault. Use when asked to post to several platforms, read what came in, answer it, automate reactions to messages, or check which platforms are set up.
---

# amoorion

One tool for many platforms. Every operation is a **method**; the CLI, the
Python object, the HTTP API and the MCP server all expose the same methods.

## Before anything

1. `amoorion plugins`: the platforms installed and what each can do. Each
   platform is its own package: `pip install amoorion-bluesky`.
2. `amoorion accounts`: which platforms have their secrets in the vault. A
   platform without them refuses to work; never ask the user for a token in
   the chat, it belongs in their vault.
3. Try with the platform `dryrun` first: it sends nothing.

## Methods

Read-only, safe to run:

```sh
amoorion --json plugins                               # what is installed
amoorion --json accounts                              # which secrets are set (values never shown)
amoorion --json read --platform bluesky --limit 5     # latest messages; also kept in the inbox and dataset
amoorion --json inbox                                 # everything read or received so far
amoorion --json search --text "invoice"               # find in the inbox
amoorion --json snapshot --platform bluesky           # a profile's posts into the dataset
amoorion --json wiki --title "Cupid"                  # a Wikipedia summary
amoorion --json simulate --topic "…" --personas …     # personas react, locally; needs a language model
amoorion --json skill                                 # this text, and where the file is
```

They change something on a platform or reach people, so **confirm first**:

```sh
amoorion publish --text "hello" --to dryrun bluesky mastodon
amoorion reply --platform bluesky --to "<post id>" --text "…"
amoorion delete --platform bluesky --id "<post id>"            # a copy stays in the dataset
amoorion notify --text "…"                                     # to the platforms of AMOORION_NOTIFY
amoorion workflow --steps …                                    # methods in order, stops at the first failure
amoorion automate --rules …                                    # rules on the inbox, once per message
```

`amoorion compose --prompt "…"` asks a language model (from the vault) to write
something; it posts nothing. `amoorion <method> -h` tells the parameters of any
method, and `--json` before the method gives machine-readable output.

## From Python

```python
from amoorion import Amoorion, Plugins

amo = Amoorion().use(Plugins["dryrun"])    # a sandbox: nothing of the real setup
amo.publish(text="hello")                  # every method by its name

real = Amoorion(".env").use(Plugins["bluesky"])    # the user's real vault, inbox and dataset
```

`Amoorion.init()` puts the whole process in a sandbox: also the CLI, `Inbox()`
and `Plugins`, for what doesn't go through an object.

## As servers

`amoorion mcp` runs the MCP server (stdio) with the methods as tools; the ones
that change something on a platform are not marked read-only. `amoorion api`
serves them over HTTP, `amoorion daemon` runs the long-running services.

## Rules

- Publishing, replying, deleting and notifying are visible to real people: get
  the user's confirmation of the text and the platforms before running them.
- Secrets live only in the vault the user's `.env` links to; never print, log
  or commit them.
- Docs: https://amoorion.readthedocs.io (Markdown of any page: ask with
  `Accept: text/markdown`, or read https://amoorion.readthedocs.io/llms.txt).
