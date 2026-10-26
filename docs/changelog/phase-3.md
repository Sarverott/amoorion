# Phase 3: communication platforms

Append-only.

## UNIXUSAT=1793002999457 · commit 348577f

The author's fourth orders, word for word, with the order to prepare tests
for each platform given in the chat ("go on, orders were provided, prepare
tests for each platform too"):

````markdown
### Q12
both webhook and bot as options

### Q11
inbox first, 
then
rules in phase 4, 
once 
ntfy and NATS 
exist as targets
````

The questions they answer, with their decisions:

### Q11: what happens to incoming messages

Phase 3 platforms (Discord, Telegram, Matrix) and the hooks receive
messages. Where do they go?

- nowhere yet: plugins only `read` on request, as the publication ones
- kept: an inbox (a small local database, e.g. SQLite) that `read` and the
  API/MCP can query across platforms
- routed: rules like "a GitHub hook → post on Discord #dev", "a Telegram
  message mentioning me → ntfy", kept in a config file
- both: inbox first, rules on top

*Lean:* inbox first (SQLite in `.BOS/data/`-like place set by `.env`), then
rules in phase 4, once ntfy and NATS exist as targets.

**Decision:** inbox first, then rules in phase 4, once ntfy and NATS exist as targets.

### Q12: Discord: bot or webhooks

Posting into a Discord channel works with a channel webhook URL alone (no
bot, post only); reading and replying need a bot token and the gateway.

*Lean:* bot token (post, read, reply), and a channel webhook only as a
lighter `discord-webhook` way to post.

**Decision:** both, the bot and the channel webhook, as options.

## UNIXUSAT=1793003573783 · commit 5a1cd16

The orders carried out. Messages received are kept in an inbox, a SQLite
file set by `AMOORION_INBOX` in `.env`: `read` and the hooks fill it,
the new `inbox` method lists it (Q11); rules on top come in phase 4.
Discord is one package with both ways (Q12): `discord`, a bot that posts,
reads and replies in a channel, and `discord-webhook`, which only posts;
neither pings anyone. Telegram (a bot in one chat) and Matrix (one room)
followed. Errors no longer show secrets that sit in URLs (Telegram's token,
a webhook's). For each platform a live test is ready (`task test:live --
<platform>…`): one marked post, read back and answered; it runs only for
the platforms named and has not been run (Q13). Still open in phase 3:
listening live through each platform's gateway or sync. Q14 opened.
