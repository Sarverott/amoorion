# BRAINSTORM

Open questions. Each `Q<n>` gets a **Decision:** when the author answers it
in [ORDERS.md](ORDERS.md); answered ones move to `docs/changelog/`.
Answered so far: Q1–Q5 in [phase-0](../changelog/phase-0.md), Q6–Q8 in
[phase-1](../changelog/phase-1.md), Q9–Q10 in [phase-2](../changelog/phase-2.md).

## Q11: what happens to incoming messages

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

## Q12: Discord: bot or webhooks

Posting into a Discord channel works with a channel webhook URL alone (no
bot, post only); reading and replying need a bot token and the gateway.

*Lean:* bot token (post, read, reply), and a channel webhook only as a
lighter `discord-webhook` way to post.

## Q13: trying the platforms for real

All six publication plugins are tested only against fakes. Which accounts
can be used for a first real post, and may the agent post there (one test
post each, deleted afterwards where the platform allows)?

*Lean:* the author gives a test account per platform in the vault and the
go-ahead per platform; the agent runs `amoorion publish` once each and
fixes what the real API answers differently.
