#!/usr/bin/env bash
# The access to the Bitwarden vault, kept in .env (decision Q13): bw from
# tools/ (npm, `task vault:tools`), logged in and unlocked; its session is
# AMOORION_VAULT_TOKEN. The platforms' secrets stay in the vault. In .env
# only that line changes (and AMOORION_VAULT, when it isn't set); a missing
# .env is made from example.env.
# Usage: scripts/vault.sh login|lock|status   (task vault:login, vault:lock, vault:status)
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
bw=${AMOORION_BW:-$(command -v bw || echo "$root/tools/node_modules/.bin/bw")}
if [ ! -x "$bw" ]; then
    echo "no Bitwarden CLI: run \`uv run task vault:tools\` (npm puts it in tools/)" >&2
    exit 1
fi
[ -f .env ] || { cp example.env .env; echo "made .env from example.env"; }
chmod 600 .env

setting() { grep -E "^$1=" .env | tail -1 | cut -d= -f2- | sed -E 's/[[:space:]]+#.*$//; s/^[[:space:]]+|[[:space:]]+$//g' || true; }
status() { "$bw" status 2>/dev/null | tail -1 | python3 -c 'import json, sys; print(json.load(sys.stdin)["status"])'; }

# Sets the token line from $TOKEN in the environment, never from arguments (they show in `ps`).
keep() {
    TOKEN="$1" python3 - <<'PY'
import os
import re
from pathlib import Path

env = Path(".env")
text = env.read_text()
line = f"AMOORION_VAULT_TOKEN={os.environ['TOKEN']}"
text, found = re.subn(r"^AMOORION_VAULT_TOKEN=.*$", line, text, count=1, flags=re.M)
if not found:
    text = text.rstrip("\n") + "\n" + line + "\n"
if not re.search(r"^AMOORION_VAULT=", text, flags=re.M):
    text = "AMOORION_VAULT=bitwarden\n" + text
env.write_text(text)
PY
}

case "${1:-}" in
    login)
        if [ "$(status)" = unauthenticated ]; then
            addr=$(setting AMOORION_VAULT_ADDR)
            [ -n "$addr" ] && "$bw" config server "$addr"
            "$bw" login
        fi
        session=$("$bw" unlock --raw)
        BW_SESSION=$session "$bw" sync >/dev/null
        keep "$session"
        echo "the vault is unlocked; its session is in .env (AMOORION_VAULT_TOKEN)"
        ;;
    lock)
        "$bw" lock >/dev/null || true
        keep ""
        echo "the vault is locked; AMOORION_VAULT_TOKEN in .env is empty"
        ;;
    status)
        echo "bw: $bw ($("$bw" --version 2>/dev/null | tail -1)), $(status)"
        ;;
    *)
        echo "usage: $0 login|lock|status" >&2
        exit 2
        ;;
esac
