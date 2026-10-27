# Contributing

amoorion is in an early stage. The contributors guide is in the docs:
[docs/contributing.md](../docs/contributing.md) (on Read the Docs:
Development → Contributors guide). In short:

1. Work on `development`; pull requests go to `development`, never `master`.
2. `uv run task init` installs the tools and the git hooks, then checks.
3. Start with `git pull --rebase origin development` and `uv run task state`.
4. Commits follow [conventional commits](https://www.conventionalcommits.org/),
   checked by commitizen; their type decides the next version.
5. `uv run task check` must pass before you push or open a pull request.
6. Never commit platform tokens or passwords.
