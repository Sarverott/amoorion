# amoorion-dev

Development tools of [amoorion](../../README.md), never published. One CLI,
`uv run amoorion-dev …` (or the `task` names in brackets):

| Command | Does |
| ------- | ---- |
| `state` (`task state`) | the state of development: branch, version, releases, the open pull request, workflows, phases, questions, orders |
| `version current\|mark\|final` (`task version`) | the versions of the release loop |
| `phases` | the phases of TODO.md, done or not, and which one a release would complete |
| `notes <tag>` | release notes: the commits and the story of `docs/changelog/` since the last release |
| `packages` | the published packages (for the publish workflow) |
| `site --out <dir>` | the project's web page |
| `identity` | sets git's user to the bot of `.github/flow.toml` |

Settings: [`.github/flow.toml`](../../.github/flow.toml).
