"""What GitHub and PyPI say: the open release pull request, the last run of every workflow,
the latest GitHub release, the version on PyPI. GitHub is asked with GH_TOKEN or
GITHUB_TOKEN when set, else without (60 calls an hour).
"""

import json
import os
import urllib.request
from typing import Any

from amoorion_dev.repo import Repo

TIMEOUT = 5


def fetch(url: str) -> Any:

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "amoorion-dev",
        },
    )

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    if token and url.startswith("https://api.github.com/"):
        request.add_header(
            "Authorization",
            f"Bearer {token}",
        )

    with urllib.request.urlopen(request, timeout=TIMEOUT) as answer:
        return json.load(answer)


def remote(repo: Repo) -> dict[str, Any]:

    settings = repo.settings()

    slug = settings.get(
        "repository",
        {},
    ).get(
        "slug",
        "",
    )

    work = settings.get(
        "branches",
        {},
    ).get(
        "work",
        "development",
    )

    release = settings.get(
        "branches",
        {},
    ).get(
        "release",
        "master",
    )

    api = f"https://api.github.com/repos/{slug}"

    found: dict[str, Any] = {}

    asks = {
        "pull_request": f"{api}/pulls?state=open&base={release}&head={slug.split('/')[0]}:{work}",
        "runs": f"{api}/actions/runs?per_page=30",
        "release": f"{api}/releases/latest",
        "pypi": "https://pypi.org/pypi/amoorion/json",
    }

    for name, url in asks.items():
        try:
            answer = fetch(url)
        except (
            Exception
        ) as error:  # offline, rate-limited, not there yet: say so, go on
            found[name] = {"error": f"{type(error).__name__}: {error}"}

            continue

        if name == "pull_request":
            found[name] = (
                {
                    "number": answer[0]["number"],
                    "title": answer[0]["title"],
                    "url": answer[0]["html_url"],
                }
                if answer
                else None
            )

        elif name == "runs":
            latest: dict[str, dict[str, str]] = {}

            for run in answer.get("workflow_runs", []):
                latest.setdefault(
                    run["name"],
                    {
                        "branch": run["head_branch"],
                        "status": run["conclusion"] or run["status"],
                        "url": run["html_url"],
                    },
                )

            found[name] = latest

        elif name == "release":
            found[name] = {
                "tag": answer["tag_name"],
                "url": answer["html_url"],
            }

        else:
            found[name] = {"version": answer["info"]["version"]}

    return found
