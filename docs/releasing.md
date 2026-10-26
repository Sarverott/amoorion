# Releasing

Releases follow the BOS flow: work lands on `development`, goes through
`revision`, `testing` and `releasing`, and reaches `master` by a pull
request. **Every push to `master` (a merged pull request too) makes a
release** when its commits ask for one.

## What happens

1. **`release` workflow** (`.github/workflows/release.yml`), on a push to
   `master`:
   - runs `task check`;
   - `cz bump` reads the conventional commits since the last tag (`feat` →
     minor, `fix` → patch; while the version is `0.x`, breaking changes
     raise the minor) and, if any asks for it, bumps **every package of
     the workspace to the same version** (`version_files` in
     `pyproject.toml`), updates `uv.lock`, writes `CHANGELOG.md`, commits
     `bump: version …` and tags `v<version>`;
   - pushes the commit and the tag to `master`, and creates the GitHub
     release with that version's part of `CHANGELOG.md` as notes.

   Commits that ask for no version (only `docs`, `test`, `build`…) make no
   release.
2. **`publish` workflow** (`.github/workflows/publish.yml`), for the
   release (started by `release`, or by a release made by hand on GitHub):
   - builds every package (`uv build --all-packages`);
   - attaches the wheels and source archives to the GitHub release;
   - uploads them to PyPI by trusted publishing.

After a release, merge `master` back into `development`, so it has the bump
commit.

## Set up once, by the author

- **PyPI trusted publishing**, for each package (`amoorion`,
  `amoorion-bluesky`, … every one in `packages/`): on PyPI, Your projects →
  Publishing → add a (pending) publisher: owner `Sarverott`, repository
  `amoorion`, workflow `publish.yml`, environment `pypi`. No token is kept
  anywhere.
- **GitHub environment `pypi`** (Settings → Environments), optionally with
  required reviewers, so that every upload waits for a click.
- **`master` protection**, if any, must let GitHub Actions push the bump
  commit and the tag.
- **Read the Docs** builds the docs from `.readthedocs.yaml`; after a
  change of `uv.lock`, `task docs:requirements` refreshes
  `docs/requirements.txt` (`task check` fails until it does).
