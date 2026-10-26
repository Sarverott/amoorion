# BRAINSTORM

Open questions. Each `Q<n>` gets a **Decision:** when the author answers it
in [ORDERS.md](ORDERS.md); answered ones move to `docs/changelog/`.
Q1–Q5 are answered: [../changelog/phase-0.md](../changelog/phase-0.md).

## Q6: which vault

Secrets come from a vault (Q3). Which one does amoorion talk to first?

- HashiCorp Vault / OpenBao, KV v2 over HTTP (`requests` is already a
  dependency; a token or AppRole in `.env` establishes the link)
- Bitwarden / Vaultwarden through the `bw` CLI (client-side decryption, so
  no plain HTTP API)
- KeePassXC database file

*Lean:* OpenBao / HashiCorp Vault KV v2 first; the backend sits behind
`amoorion.vault.base.Vault`, so others can follow.

## Q7: per-platform plugins "with …"

The answer to Q2 ends in "adopt per-platform plugins with". With what?

*Lean:* with Python entry points (group `amoorion.plugins`), so a platform
can live in this repository (`src/amoorion/plugins/<platform>/`) or as a
separate package, and one shared interface (`post`, `read`, `reply`).

## Q8: `dotenv` package

`pyproject.toml` has `dotenv`, a shim that only installs `python-dotenv`.
Depend on `python-dotenv` directly?

*Lean:* yes.
