# For agents

The map of the repository and the working guide that AI agents (and
people) follow here. They live in `docs/.agents/`.

## amoorion as a skill

amoorion can teach an agent to use it, wherever the agent is:

```sh
amoorion --json skill                          # the text, and the path of the file installed with the package
/plugin install amoorion --marketplace Sarverott/amoorion     # in Claude Code
```

Any agent reading `SKILL.md` files can take the file from that path or from
[/skills/amoorion/SKILL.md](https://amoorion.readthedocs.io/en/latest/skills/amoorion/SKILL.md).

```{include} .agents/MAP.md
:heading-offset: 1
```

```{include} .agents/GUIDE.md
:heading-offset: 1
```
