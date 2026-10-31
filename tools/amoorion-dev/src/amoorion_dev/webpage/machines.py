"""What the site says to machines: manifests, 404.html, robots.txt, llms.txt."""

import json
from pathlib import Path

from amoorion_dev import version as versions
from amoorion_dev.repo import Repo
from amoorion_dev.webpage.page import page


def data(
    repo: Repo,
    out: Path,
    version: str,
    slug: str,
    docs: str,
    examples: list[str],
    pages: list[str],
) -> list[Path]:
    """The files other programs build on: openapi.json, manifest.json, and manifest.schema.json saying its shape."""

    from amoorion_dev.webpage.contract import Manifest, openapi, platforms

    manifest = Manifest(
        name="amoorion",
        version=version,
        repository=f"https://github.com/{slug}",
        docs=docs,
        openapi="openapi.json",
        packages={
            package.name: package.version(repo)
            for package in versions.packages(repo)
        },
        platforms=platforms(),
        pages=pages,
        examples=examples,
    )

    contents = {
        out / "openapi.json": openapi(),
        out / "manifest.json": manifest.model_dump(mode="json"),
        out / "manifest.schema.json": Manifest.model_json_schema(),
    }

    for path, content in contents.items():
        path.write_text(json.dumps(content, indent=2) + "\n")

    return list(contents)


def manifests(
    repo: Repo,
    out: Path,
    version: str,
    slug: str,
    docs: str,
    examples: list[Path],
) -> list[Path]:
    """What the site and the release hold, for machines (see `data`); site.webmanifest: for browsers."""

    contents = data(
        repo,
        out,
        version,
        slug,
        docs,
        [f"examples/{path.name}" for path in examples],
        sorted(str(path.relative_to(out)) for path in out.rglob("*.html")),
    )

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

    (out / "site.webmanifest").write_text(json.dumps(web, indent=2) + "\n")

    return contents + [out / "site.webmanifest"]


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
        f"- [What the site holds]({base}manifest.json)\n- [The HTTP API, as OpenAPI]({base}openapi.json)\n"
        + (f"\n## Examples (marimo)\n\n{entries}\n" if entries else "")
        + f"\n## Code\n\n- [GitHub](https://github.com/{slug})\n- [PyPI](https://pypi.org/project/amoorion/)\n"
    )

    return files
