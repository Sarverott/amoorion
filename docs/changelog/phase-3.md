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
