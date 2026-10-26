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

## Q14: deleting posts

No plugin can delete. The live tests (Q13) leave their test posts behind,
and a post sent by mistake can only be removed by hand on each platform.

- no deleting: amoorion only adds; mistakes are fixed by hand
- a `delete` capability and method (`amoorion delete --platform x --id …`),
  where the platform allows it (all but Blogger by mail and the Discord
  webhook without its message id kept; Telegram only within 48 hours in
  groups), not `read_only`, so agents get it only as a destructive tool
- only inside the live tests, through each platform's API directly

*Lean:* a `delete` capability and method; the live test then deletes its
own test post and reply.

## Q15: releases and packages

The inquiry's release workflows are in place (docs/releasing.md); a few
choices in them are the author's to confirm before the first merge to
`master`:

- "git package": the built wheels and source archives attached to each
  GitHub release. GitHub Packages has no Python registry; a container
  image on ghcr.io fits phase 6 (Dockerfile). Enough, or the image now?
- one version for all packages (lock-step), bumped together; or each
  plugin package versioned on its own (more work per release)?
- the PyPI names `amoorion` and `amoorion-<platform>`, ten projects, each
  with a trusted publisher; and the `pypi` environment with or without a
  required reviewer.

*Lean:* release assets now and the image in phase 6, lock-step versions,
the `pypi` environment with the author as required reviewer.
