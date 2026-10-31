#!/usr/bin/env bash
# The presentation page: the source of amoorion-website (pages.website in
# .github/flow.toml), cloned into website/ and built by its `npm run build` into
# website/dist/ for the project's GitHub Pages path (/<repository>/).
# website/ is ignored by .gitignore. `amoorion-dev site --website website/dist`
# puts it at the root of the web page. Run after `task examples:build`, for the
# examples of the manifest.
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
# What the website reads while it builds: openapi.json, manifest.json, manifest.schema.json.
data=$root/website/.amoorion-data
(cd "$root" && "${dev[@]}" site-data --out "$data")
# The contract with the website: `npm run build` takes --base and writes dist/, by whatever tool it uses
# (vite and Astro both do); AMOORION_DATA and AMOORION_BASE are there for it.
npm install --no-audit --no-fund --loglevel=error --legacy-peer-deps
AMOORION_DATA=$data AMOORION_BASE=$base npm run build -- --base "$base"
# The source names its pictures from the root (/assets/…); under /<repository>/ they move with the base.
grep -rlZ -e '"/assets/' -e "'/assets/" -e '`/assets/' dist | xargs -0 -r sed -i \
    -e "s#\"/assets/#\"${base}assets/#g" -e "s#'/assets/#'${base}assets/#g" -e "s#\`/assets/#\`${base}assets/#g"
echo "built $root/website/dist for $base"
