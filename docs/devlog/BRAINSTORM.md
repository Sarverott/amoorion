# BRAINSTORM

Open questions. Each `Q<n>` gets a **Decision:** when the author answers it
in [ORDERS.md](ORDERS.md); answered ones move to `docs/changelog/`.

## Q1: shape of the tool

CLI only, a long-running daemon (bots, webhooks, NATS listeners), or both?

## Q2: adapter model

One common interface for every platform (post, read, reply), with
per-platform plugins; or loose per-platform modules first?

## Q3: secrets

Where platform tokens live: environment / `.env`, `.BOS/setup/`, a
vault (e.g. Vaultwarden of the zone)?

## Q4: deployment

Run locally only, or as a container on the zone (`rs-tech-infra`, which
already has ntfy)?

## Q5: licence

The repository carries MIT (2024). Keep it, or align with MPL-2.0 used by
rs-tech-brandstyle?
