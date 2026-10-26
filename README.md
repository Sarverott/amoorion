# amoorion
Universal tool for administration of chatting and communication platforms

---

## **EARLY STAGE OF PROJECT**

---

*TODO:*

#### Publication platforms
- twitter (x.com) posting by api
- bluesky posting
- tumblr posting by api
- blogger posting by mail
- facebook posting

#### Communication platforms
- discord
- telegram
- matrix
- ~whatsapp~
- ~signal~

#### Additional functionality
- email client
- ~rss feed receiver~
- ~phone manage by adb~
- webhooks - standard linkings with services like gitlab, github, discord etc.
- ntfy notifications
- nats.io

---

## Development

```sh
uv sync && uv run task setup   # tools and git hooks
uv run task check              # tests, YAML, commit messages (= CI)
uv run amoorion                # the CLI
```

Plan and open questions: [docs/devlog/](docs/devlog/). Guide for agents and
contributors: [AGENTS.md](AGENTS.md).
