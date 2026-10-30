#!/usr/bin/env bash
# Start a platform plugin package in packages/amoorion-<platform>/ (see docs/plugins.md).
# Usage: scripts/new-plugin.sh <platform> <ClassName> "<one-line description>"
set -euo pipefail
if [ $# -ne 3 ]; then
    echo "usage: $0 <platform> <ClassName> \"<description>\"" >&2
    exit 2
fi
platform=$1 class=$2 description=$3
root=$(cd "$(dirname "$0")/.." && pwd)
# Released with the same version as every package (lock-step).
version=$(sed -n 's/^version = "\(.*\)"$/\1/p' "$root/pyproject.toml" | head -1)
pkg=$root/packages/amoorion-$platform
module=amoorion_${platform//-/_}
if [ -e "$pkg" ]; then
    echo "$pkg exists already" >&2
    exit 1
fi
mkdir -p "$pkg/src/$module" "$pkg/tests"
cat > "$pkg/pyproject.toml" <<TOML
[project]
name = "amoorion-$platform"
version = "$version"
description = "$description"
readme = "README.md"
license = "MIT"
authors = [
    { name = "Sett Sarverott", email = "sett@sarverott.com" }
]
requires-python = ">=3.12"
dependencies = [
    "amoorion",
]

[project.urls]
Homepage = "https://github.com/Sarverott/amoorion"
Documentation = "https://amoorion.readthedocs.io/en/latest/platforms/$platform.html"
Source = "https://github.com/Sarverott/amoorion/tree/master/packages/amoorion-$platform"
Issues = "https://github.com/Sarverott/amoorion/issues"
Changelog = "https://github.com/Sarverott/amoorion/blob/master/CHANGELOG.md"

[project.entry-points."amoorion.plugins"]
$platform = "$module:$class"

[tool.uv.sources]
amoorion = { workspace = true }

[build-system]
requires = ["uv_build>=0.12.20,<0.13.0"]
build-backend = "uv_build"
TOML
printf '# amoorion-%s\n\n%s\n\nSecrets in amoorion'"'"'s vault: `%s/<key>` … (TODO)\n' \
    "$platform" "$description" "$platform" > "$pkg/README.md"
cat > "$pkg/src/$module/schema.vault.json" <<JSON
{
  "vault": {
    "$platform": {
      "description": "$description",
      "scopes": {},
      "optional": {}
    }
  }
}
JSON
cat > "$root/docs/platforms/$platform.md" <<DOC
\`\`\`{include} ../../packages/amoorion-$platform/README.md
\`\`\`

## Its vault entry

\`\`\`{literalinclude} ../../packages/amoorion-$platform/src/$module/schema.vault.json
:language: json
\`\`\`
DOC
cat > "$pkg/src/$module/__init__.py" <<PY
"""amoorion-$platform: $description."""

from $module.base import $class

__all__ = ["$class"]
PY
cat > "$pkg/src/$module/base.py" <<PY
"""$platform plugin.

Secrets (\`$platform/<key>\`): … (TODO)
"""

from typing import ClassVar

from amoorion.models import Message, Post
from amoorion.plugins import Capability, HttpPlugin


class $class(HttpPlugin):
    name: ClassVar[str] = "$platform"
    description: ClassVar[str] = "$description"
    capabilities: ClassVar[frozenset[Capability]] = frozenset({Capability.POST})
    secrets: ClassVar[tuple[str, ...]] = ()

    def post(self, post: Post) -> Message:
        raise NotImplementedError
PY
cd "$root"
python3 -I - "$platform" <<'PYEDIT'
import sys

platform = sys.argv[1]
text = open("pyproject.toml").read()
line = f"amoorion-{platform} = {{ workspace = true }}\n"
if line not in text:
    text = text.replace("[tool.uv.sources]\n", "[tool.uv.sources]\n" + line)
# commitizen bumps its version with the others.
entry = f'    "packages/amoorion-{platform}/pyproject.toml:^version",\n'
if entry not in text:
    text = text.replace("version_files = [\n", "version_files = [\n" + entry)
open("pyproject.toml", "w").write(text)
PYEDIT
uv add --dev "amoorion-$platform"
echo "created $pkg: write base.py, schema.vault.json and tests/, add docs/platforms/$platform to docs/platforms.md, then: uv run amoorion plugins"
