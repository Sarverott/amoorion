#!/usr/bin/env bash
# The presentation page: the source of amoorion-website (pages.website in
# .github/flow.toml), cloned into website/ and built by vite into
# website/dist/ for the project's GitHub Pages path (/<repository>/).
# website/ is ignored by .gitignore. `amoorion-dev site --website website/dist`
# puts it at the root of the web page.
# Usage: scripts/build-website.sh   (task site:website)
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
dev=(uv run -q --frozen amoorion-dev)
cd "$root"
repository=$("${dev[@]}" setting pages.website)
ref=$("${dev[@]}" setting pages.website_ref)
base=/$("${dev[@]}" setting repository.slug | cut -d/ -f2)/
rm -rf website
git clone -q --depth 1 --branch "$ref" "https://github.com/$repository.git" website
cd website
# Its esbuild pin (^0.25) is older than vite 8 asks for as an optional peer; bun.lock gets by, npm needs this.
npm install --no-audit --no-fund --loglevel=error --legacy-peer-deps
npx vite build --base "$base" --outDir dist --emptyOutDir
# The source names its pictures from the root (/assets/…); under /<repository>/ they move with the base.
grep -rlZ -e '"/assets/' -e "'/assets/" -e '`/assets/' dist | xargs -0 -r sed -i \
    -e "s#\"/assets/#\"${base}assets/#g" -e "s#'/assets/#'${base}assets/#g" -e "s#\`/assets/#\`${base}assets/#g"
echo "built $root/website/dist for $base"
