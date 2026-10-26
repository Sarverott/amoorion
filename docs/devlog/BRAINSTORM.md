# BRAINSTORM

Open questions. Each `Q<n>` gets a **Decision:** when the author answers it
in [ORDERS.md](ORDERS.md); answered ones move to `docs/changelog/`.
Answered so far: Q1–Q5 in [phase-0](../changelog/phase-0.md), Q6–Q8 in
[phase-1](../changelog/phase-1.md).

## Q9: default platforms for `publish`

`publish` needs `--to`. Where do the default platforms come from when it is
left out?

- an environment setting in `.env` (`AMOORION_PUBLISH_TO=bluesky,x`), though
  `.env` was meant only for the vault link (Q3)
- a config file (`amoorion.toml` in the working directory or
  `~/.config/amoorion/`)
- every plugin that can post and whose `accounts` status is ready (never
  `dryrun`)
- no defaults: `--to` stays required

*Lean:* a config file, `amoorion.toml`, which can later hold other
non-secret settings too (routing in phase 3).

## Q10: where platform plugins live

Q7 says a plugin *can* be a separate package. Should the platforms of
phases 2–4 be

- built in, `src/amoorion/plugins/<platform>/` (as `dryrun`, and as the
  Bluesky plugin is now), or
- one package each (`amoorion-bluesky`, …), in this repository as a uv
  workspace (`packages/<platform>/`) or in repositories of their own?

*Lean:* built in until the plugin interface settles; moving one out later is
cheap, since both use the same entry point.
