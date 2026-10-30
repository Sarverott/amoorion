#!/usr/bin/env bash
# The access to the vault that .env names (decision Q13); the platforms' secrets stay in it.
# - bitwarden: bw from tools/ (npm, `task vault:tools`), logged in and unlocked;
#   its session is AMOORION_VAULT_TOKEN. In .env only that line changes (and
#   AMOORION_VAULT, when it isn't set).
# - keepassxc: the file AMOORION_VAULT_PATH, its master password
#   AMOORION_VAULT_TOKEN, both written by the author; .env is never changed.
# A missing .env is made from example.env.
# Usage: scripts/vault.sh new|login|lock|status   (task vault:new, vault:login, vault:lock, vault:status)
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
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

# The password goes from .env to Python alone, never through arguments or output.
keepassxc() {
    "$root/.venv/bin/python" - "$1" <<'PY'
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError

from amoorion.core import AmoorionError
from amoorion.hooks import schema as hooks_schema
from amoorion.plugins import PLUGINS, load_plugins
from amoorion.vault import VaultLink
from amoorion.vault.kpxc_db_file import initialize

load_dotenv(".env", override=True)
path, token = os.environ.get("AMOORION_VAULT_PATH"), os.environ.get("AMOORION_VAULT_TOKEN")
if not path:
    sys.exit("no AMOORION_VAULT_PATH in .env: the path of the .kdbx file")
file = Path(path).expanduser()
if sys.argv[1] == "new":
    load_plugins()
    schemas = {name: PLUGINS.get(name).schema() for name in PLUGINS.names() if PLUGINS.get(name).secrets}
    schemas["hooks"] = hooks_schema()
    schemas["api"] = {"description": "The HTTP API", "scopes": {"token": "Bearer token of method calls"}, "optional": {}}
    try:
        added = initialize(VaultLink(kind="keepassxc", path=path, token=token), schemas)
    except AmoorionError as error:
        sys.exit(str(error))
    print(f"{file}: added {', '.join(added)}; fill them in KeePassXC" if added else f"{file}: nothing to add")
elif not file.exists():
    print(f"keepassxc: no {file}: `uv run task vault:new` makes it")
else:
    try:
        database = PyKeePass(str(file), password=token)
    except CredentialsError:
        sys.exit(f"keepassxc: {file}: AMOORION_VAULT_TOKEN is not its master password")
    group = database.find_groups(name="amoorion", first=True)
    entries = [entry.title for entry in group.entries] if group else []
    print(f"keepassxc: {file}, opens; group amoorion: {', '.join(entries) or 'no entries'}")
PY
}

if [ "$(setting AMOORION_VAULT)" = keepassxc ]; then
    case "${1:-}" in
        new | status) keepassxc "$1"; exit ;;
        login | lock)
            echo "keepassxc has no session: AMOORION_VAULT_TOKEN in .env is its master password, and stays"
            exit
            ;;
    esac
fi

bw=${AMOORION_BW:-$(command -v bw || echo "$root/tools/node_modules/.bin/bw")}
if [ ! -x "$bw" ]; then
    echo "no Bitwarden CLI: run \`uv run task vault:tools\` (npm puts it in tools/)" >&2
    exit 1
fi

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
        echo "usage: $0 new|login|lock|status (new: keepassxc only)" >&2
        exit 2
        ;;
esac
