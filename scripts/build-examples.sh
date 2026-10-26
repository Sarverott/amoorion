#!/usr/bin/env bash
# marimo builds of the example notebooks: each examples/<name>.ipynb becomes
# a marimo notebook examples/build/<name>.py and a page examples/build/<name>.html
# with its outputs. examples/build/ is ignored by examples/.gitignore.
# Usage: scripts/build-examples.sh   (task examples:build)
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
build=$root/examples/build
marimo=(uv run --frozen --group examples marimo)
rm -rf "$build"
mkdir -p "$build"
for notebook in "$root"/examples/*.ipynb; do
    name=$(basename "$notebook" .ipynb)
    "${marimo[@]}" convert "$notebook" -o "$build/$name.py"
    # Run from build/, with the examples' own safe settings (env vault, temporary inbox).
    (cd "$build" && env -u AMOORION_VAULT "${marimo[@]}" export html "$name.py" -o "$name.html")
    echo "built $build/$name.html"
done
