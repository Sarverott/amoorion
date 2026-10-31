"""What the site says to machines: manifests, 404.html, robots.txt, llms.txt."""

import json
from pathlib import Path

from amoorion_dev import version as versions
from amoorion_dev.repo import Repo
from amoorion_dev.webpage.page import page


def manifests(
    repo: Repo,
    out: Path,
    version: str,
    slug: str,
    docs: str,
    examples: list[Path],
) -> list[Path]:
    """manifest.json: what the site and the release hold, for machines; site.webmanifest: for browsers."""

    contents = {
        "name": "amoorion",
        "version": version,
        "repository": f"https://github.com/{slug}",
        "docs": docs,
        "packages": {
            package.name: package.version(repo)
            for package in versions.packages(repo)
        },
        "pages": sorted(
            str(path.relative_to(out)) for path in out.rglob("*.html")
        ),
        "examples": [f"examples/{path.name}" for path in examples],
    }

    web = {
        "name": "amoorion",
        "short_name": "amoorion",
        "description": "Universal tool for administration of chatting and communication platforms",
        "start_url": "./",
        "display": "browser",
        "background_color": "#07090e",
        "theme_color": "#e14c62",
        "icons": [
            {
                "src": "graphics/cupid.png",
                "sizes": "512x512",
                "type": "image/png",
            }
        ],
    }

    files = [
        out / "manifest.json",
        out / "site.webmanifest",
    ]

    files[0].write_text(json.dumps(contents, indent=2) + "\n")

    files[1].write_text(json.dumps(web, indent=2) + "\n")

    return files


def for_machines(
    out: Path,
    version: str,
    links: dict[str, str],
    slug: str,
    docs: str,
    examples: list[Path],
) -> list[Path]:
    """404.html (GitHub Pages shows it for any missing page), robots.txt and llms.txt."""

    base = (
        f"https://{slug.split('/')[0].lower()}.github.io/{slug.split('/')[1]}/"
    )

    lost = (
        "<h2>Lost between platforms</h2>\n<p>This page isn't here: it may have moved, or never was.</p>\n"
        f'<p><a href="{base}">Back to the start</a>, or read <a href="{docs}">the docs</a>.</p>\n'
    )

    # Absolute links: GitHub Pages serves 404.html at whatever path was asked for.
    absolute = {
        name: url if ":" in url else base + url for name, url in links.items()
    }

    files = [
        out / "404.html",
        out / "robots.txt",
        out / "llms.txt",
    ]

    files[0].write_text(
        page(
            "amoorion: not found",
            lost,
            version,
            absolute,
            root=base,
        )
    )

    files[1].write_text(
        f"User-agent: *\nAllow: /\n\n# The docs keep their own: {docs}robots.txt\n"
    )

    entries = "\n".join(
        f"- [{path.stem.split('-', 1)[-1].replace('-', ' ')}]({base}examples/{path.name})"
        for path in examples
    )

    files[2].write_text(
        f"# amoorion\n\n> Universal tool for administration of chatting and communication platforms: publish, "
        f"read and reply on many platforms from one CLI, HTTP API or MCP server. Version {version}.\n\n"
        f"## Docs\n\n- [Documentation, as an index for agents]({docs}llms.txt)\n"
        f"- [Agent skill]({docs}skills/amoorion/SKILL.md)\n\n"
        f"## This site\n\n- [Project]({base}project.html)\n- [Releases]({base}releases.html)\n"
        f"- [What the site holds]({base}manifest.json)\n"
        + (f"\n## Examples (marimo)\n\n{entries}\n" if entries else "")
        + f"\n## Code\n\n- [GitHub](https://github.com/{slug})\n- [PyPI](https://pypi.org/project/amoorion/)\n"
    )

    return files
