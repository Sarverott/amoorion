# Phase 0: the skeleton

Append-only.

## UNIXUSAT=1792981738401 · commit b77e0fc

The repository is set up after the BOS rules and the recent projects
(rs-tech-brandstyle, rs-tech-infra, nuklearium): BOS anatomy, uv package
`amoorion` with a CLI entry point, go-task, commitizen, lefthook, yamllint,
pytest, CI running `task check`. Work moved to the `development` branch.
The platform list of the README became [../devlog/TODO.md](../devlog/TODO.md).

## UNIXUSAT=1792984063141 · commit a2b7f57

The author's first orders, word for word:

````markdown
## based on below answerings make new detailed plan of work in vision

### Q1
take look at src/amoorion 
i create there some directories where you can build parts of codes
place CLI in cli and other stuff according standard assignation of namespace
prepare in docs plan of shape in file "structure.md" with listing of these structures
each dir in src/amoorion should have own core mechanics in `src/amoorion/*/base.py` or `src/amoorion/*/__main__.py` that is based on core stuff in core.py

### Q2 
adopt per-platform plugins with 

### Q3
let's make it reached from a vault for stuff like passwords and else things. base stuff from `.env` to estabilish link.

### Q4
first local, then dockerfile, then compose, then prepare for be usable inside zone

### Q5
let it be free as-is. we can add link to license with years since 2024 https://sett.mit-license.org 
do not connect it directly with rs-tech - it will be first area of use but not limited to it

## update README.md with all we know now
````

The questions they answer, with their decisions:

### Q1: shape of the tool

CLI only, a long-running daemon (bots, webhooks, NATS listeners), or both?

**Decision:** both, and more: the namespaces under `src/amoorion/` (`api`,
`cli`, `daemon`, `hooks`, `mcp`, `methods`, `models`, `plugins`), each with
its own core mechanics in `base.py` or `__main__.py` built on `core.py`.
Their shapes are listed in `docs/structure.md`.

### Q2: adapter model

One common interface for every platform (post, read, reply), with
per-platform plugins; or loose per-platform modules first?

**Decision:** per-platform plugins. (The answer ends in "with": the rest is
asked again in Q7.)

### Q3: secrets

Where platform tokens live: environment / `.env`, `.BOS/setup/`, a
vault (e.g. Vaultwarden of the zone)?

**Decision:** passwords and other secrets are reached from a vault; `.env`
holds only the base settings needed to establish the link to it.

### Q4: deployment

Run locally only, or as a container on the zone (`rs-tech-infra`, which
already has ntfy)?

**Decision:** first local, then a Dockerfile, then compose, then prepared to
be usable inside the zone.

### Q5: licence

The repository carries MIT (2024). Keep it, or align with MPL-2.0 used by
rs-tech-brandstyle?

**Decision:** MIT as it is, with a link to https://sett.mit-license.org
(years since 2024). Not tied to rs-tech: the zone is the first area of use,
not the only one.

## UNIXUSAT=1792984438330 · commit 8456800

The orders carried out. `core.py` grew from the author's sketch into
model, view, controller and a registry; every namespace has its `base.py`
on it: models, vault (new: the link of Q3 needed a home), plugins with the
`dryrun` platform, methods (`plugins`, `publish`, `read`), hooks with
the token-guarded `generic` hook, cli, api (bearer token from the vault),
mcp (tools from the methods), daemon. `docs/structure.md` lists them, VISION
holds the plan of phases 0–5, the README tells what is known. Q6–Q8 opened.
