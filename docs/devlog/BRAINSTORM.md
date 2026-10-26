# BRAINSTORM

Open questions. Each `Q<n>` gets a **Decision:** when the author answers it
in [ORDERS.md](ORDERS.md); answered ones move to `docs/changelog/`.
Answered so far: Q1–Q5 in [phase-0](../changelog/phase-0.md), Q6–Q8 in
[phase-1](../changelog/phase-1.md), Q9–Q10 in [phase-2](../changelog/phase-2.md), Q11–Q12 in
[phase-3](../changelog/phase-3.md).

## Q13: trying the platforms for real

All six publication plugins are tested only against fakes. Which accounts
can be used for a first real post, and may the agent post there (one test
post each, deleted afterwards where the platform allows)?

*Lean:* the author gives a test account per platform in the vault and the
go-ahead per platform; the agent runs `amoorion publish` once each and
fixes what the real API answers differently.

Ready for it: `uv run task test:live -- <platform>…` posts one marked test
post per platform named, reads it back and replies to it where the plugin
can, and prints the links (no plugin deletes yet, so deleting is by hand).
It covers the communication platforms of phase 3 too: Discord (bot and
webhook), Telegram, Matrix. The author can run it alone, or name the
platforms the agent may run it for.
