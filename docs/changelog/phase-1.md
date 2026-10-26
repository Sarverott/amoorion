# Phase 1: real vault and plugin loading

Append-only.

## UNIXUSAT=1792985975299 · commit a117020

The author's second orders, word for word:

````markdown
### Q6
start from Bitwarden / Vaultwarden
but each of mentioned add in separed script file in 
- `src/amoorion/vault/http_vault.py` - HashiCorp Vault / OpenBao, KV
- `src/amoorion/vault/bw_cli.py` -  Bitwarden / Vaultwarden through the `bw` CLI
- `src/amoorion/vault/kpxc_db_file.py` - KeePassXC database file
- `src/amoorion/vault/default.py` - for .env setup 

### Q7
with Python entry points
separate package, and one shared interface

### Q8
yep````

The questions they answer, with their decisions:

### Q6: which vault

Secrets come from a vault (Q3). Which one does amoorion talk to first?

- HashiCorp Vault / OpenBao, KV v2 over HTTP (`requests` is already a
  dependency; a token or AppRole in `.env` establishes the link)
- Bitwarden / Vaultwarden through the `bw` CLI (client-side decryption, so
  no plain HTTP API)
- KeePassXC database file

*Lean:* OpenBao / HashiCorp Vault KV v2 first; the backend sits behind
`amoorion.vault.base.Vault`, so others can follow.

**Decision:** Bitwarden / Vaultwarden first, and every one of them, each in
its own file: `vault/http_vault.py` (HashiCorp Vault / OpenBao KV),
`vault/bw_cli.py` (Bitwarden / Vaultwarden through `bw`),
`vault/kpxc_db_file.py` (KeePassXC database file), `vault/default.py` (the
`.env` setup).

### Q7: per-platform plugins "with …"

The answer to Q2 ends in "adopt per-platform plugins with". With what?

*Lean:* with Python entry points (group `amoorion.plugins`), so a platform
can live in this repository (`src/amoorion/plugins/<platform>/`) or as a
separate package, and one shared interface (`post`, `read`, `reply`).

**Decision:** Python entry points; a plugin can be a separate package; one
shared interface.

### Q8: `dotenv` package

`pyproject.toml` has `dotenv`, a shim that only installs `python-dotenv`.
Depend on `python-dotenv` directly?

*Lean:* yes.

**Decision:** yes.
