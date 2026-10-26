# Contributing

amoorion is in an early stage. Before you start, read [AGENTS.md](../AGENTS.md)
(it is for humans too) and [docs/devlog/TODO.md](../docs/devlog/TODO.md).

1. Branch from `development`; pull requests go to `development`.
2. `uv sync && uv run task setup` installs the tools and the git hooks.
3. Commits follow [conventional commits](https://www.conventionalcommits.org/),
   checked by commitizen.
4. `uv run task check` must pass before you open a pull request.
5. Never commit platform tokens or passwords.
