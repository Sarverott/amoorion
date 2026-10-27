# Phase 4: documentation, examples, releases

Append-only.

## UNIXUSAT=1793054132742 · commit 340b67d

The author's first inquiry (docs/devlog/INQUIRIES.md), word for word:

````markdown
### inquiry

> for clearify whole we have done here for users we need to improove our docs. i initialized project in readthedocs and placed some stuff there.
> we want to make it be genetared from markdown we will gona place in "docs/" with partial autonomous generation of docs based on code for code
> referencing. besides that we need to present some examples of usage in "examples/" written in jupyter notebooks files. we need also to write
> script with marimo generated builds of examples that will be .gitignored by "examples/.gitignore". add also workflow for publishing git package
> and pypi package at release been created. releases should be generated at pull request megre or push to master. begin draft of plan first based on
> this message for phase 4 (current 4->5 and 5->6 now) then realize the steps
````

It opens a new phase 4; linking becomes phase 5 and deployment phase 6.
Where earlier entries say "phase 4" (rules on the inbox, Q11) or "phase 5"
(deployment), they mean phases 5 and 6 now. The plan drawn from it is in
VISION.md (phase 4) and TODO.md.

## UNIXUSAT=1793054962845 · commit d947a88

The inquiry carried out. The author's Read the Docs start works: the docs
are a Sphinx site from the Markdown in `docs/` (MyST), with the README,
the platforms' READMEs, the guides, the plan and this changelog as pages and
an API reference generated from the code; `task docs:build` builds it with
warnings as errors inside `task check`. Four Jupyter notebooks in
`examples/` (first steps, vault and accounts, API with hooks and inbox, an
own plugin) run in the tests and show in the docs; `task examples:build`
makes marimo builds of them into the ignored `examples/build/`. A push to
`master` releases: commitizen bumps every package to one version, tags it
and makes a GitHub release, whose packages are attached to it and published
to PyPI. Not run for real yet: the workflows and Read the Docs. Q15 opened.
INQUIRIES.md joins the devlog.

## UNIXUSAT=1793057763731 · commit fc0baef

The author merged development into master to try the release: v0.2.0 was
tagged and released on GitHub with its packages; PyPI refused it, having
no trusted publisher. Their order, given in the chat, word for word:

````markdown
i made there pull request and merged it to reproduce situation i want to test for further stuff. we have now bumped version there and i want to pull it from master to dev. also i made PYPI_TOKEN secret in pypi environment. we can make it automated here with workflows we had made previously. check gitrecon and ~/_WORKSHOP/forge/sarverott/github-repos/sarverott - one of them i think was complex use of these branch flow mechanics. we want to change some things. right now i see also diffrences between versioning numebers on readthedocs and released package. in future bump the version at state of master to development and mark it as pre-release by lefthook pulls, at push dev local to origin unmark pre-release and create pull request dev to master on workflow
````

Master is pulled into development. The loop now: pulling master in marks
the next pre-release (lefthook post-merge, `scripts/version.py mark`); a
push to development makes it final with its changelog section and opens
the pull request to master (flow workflow); merging it tags, releases and
publishes, with the `PYPI_TOKEN` secret, committing nothing on master.
The docs read the version from the package, as the package does.

## UNIXUSAT=1793062052329 · commit 72d048f

PR #3 (Release v0.2.2) was opened by the flow itself. The author's next
order, given in the chat, word for word:

````markdown
okidoki then. split our workflow and make each package publishing as internal action calling there. also add for all workflows optional dispach besides standard calling. add tools to manage states, read state of developement and hide in readthedocs section with devlog stuff. each release will be also contain now besides listing of commit messages content of changelog. each phase will be automaticly releasing and add yourself map of all of that inside your "docs/.agents/" dir. think for some structural moves and make yourself guidance around to have strict and organized approach for yourself iterations and other AI agents. we need to create cli interface for easy to use - this is why i added rich to dependings package list. we need also to delegate at each release been made to produce webpage for this project - place it in gh-pages.yml for github-pages branch production like here it is done (besides change of branch name where it is placed): "https://github.com/redscope-pl/redscope.pl"
````

Drawn into phase 4 (VISION.md items 5–8, TODO.md). The bot's identity in
the workflows is the author's: mr. Cravley, the git bot.

## UNIXUSAT=1793062999168 · commit e86848f

The author's second inquiry (docs/devlog/INQUIRIES.md), word for word:

````markdown
--

### github pages should contain builded examples
````

The order and the inquiry carried out. `tools/amoorion-dev`, a workspace
package never published, holds the development tools behind one rich CLI:
the state of development (also a page of the docs, made at every build),
the versions of the loop (moved from scripts/version.py), the phases,
release notes and the web page; the loop's settings are in
`.github/flow.toml`. Releases now carry the commits and the story of
`docs/changelog/` since the last release. A phase whose last item is ticked
since the last release releases by itself (the flow merges its pull
request). Publishing runs one job per package through the local action
`.github/actions/publish-package`; every workflow can be started by hand;
`gh-pages.yml` builds the web page with the marimo builds of the examples
into the `github-pages` branch and GitHub Pages. `amoorion` alone asks step
by step. The docs gather the devlog under one Development section, with
`docs/.agents/MAP.md` and `GUIDE.md`, the map and the working guide for
agents. Phase 4 is complete; it was complete at v0.2.1 already, so it
doesn't release itself this time.

## UNIXUSAT=1793068385753 · commit dcc5db5

After v0.3.0 was released, the author's order in the chat, word for word:

````markdown
great work Cleo! looks great my friend! feel free to write own thoughts in docs/.agents/ like you did that in previous projects. we need to make some stuff related with pull the current state of project, pushing changes, versioning and all that guidance should be written into contributors guide in developement pages on readthedocs
````

Drawn into phase 4 (TODO.md): a contributors guide in the docs'
Development section. The thoughts go to `docs/.agents/CLEO.md`, as in
rs-tech-infra.

## UNIXUSAT=1793068537104 · commit bfeea4f

The order carried out. `docs/contributing.md`, the contributors guide,
opens the docs' Development section: a checkout, pulling the current state
(development, then master after a release, then `task state`), making a
change, which commit type asks for which version, pushing and what the
flow does with it, the version stages, the release and what never to do.
`.github/CONTRIBUTING.md`, AGENTS.md, the map and the working guide point
to it. Cleo's own thoughts started in `docs/.agents/CLEO.md`.

Along the way, after v0.3.0: the author's empty Taskfiles committed as
they are; development marked 0.3.1a0 by hand, as the hook hadn't; the
`gh-pages` workflow keeps the page in the `github-pages` branch before it
asks for GitHub Pages, which v0.3.0's run had stopped at.

## UNIXUSAT=1793085881648 · commit 62a3343

The author's answers (docs/devlog/ORDERS.md), word for word:

````markdown
### Q13
we need where to put our access data first
well... at now i placed `bw` command as package dependency inside tools with npm
let's begin with initializing our credentials been placed in .env - place them there
prepare me please livetests for all platforms under one command 
go ahead and try to connect with actual apis

### Q14
add deleting but with storage of what was deleted
same place will be for readed state of all posts currently are on each socialmedia
present them as json files with index for each profile in each platform (./platform/profile/*)
create dataset/ dir that is gitignored - there will be our data stored

### Q15
wait...
why we update packages that are not changed?
if package is not changed then leave version updating and bumping 
for example:
- if in next update we change something in main amoorion and blogger package
- then we bump version of both, rest we leave unchanged
- release carries only updated wheels if it is `Z` number change (`vX.Y.Z`) if `X` or `Y` all must be placed in release
- let's reduce calls to pypi, we still do not have couple of subpackages published yet
after that
- now we change accordingly docs and dev tools
- we do not bump rest, only these one whitch has changes... and the main amoorion, but if main amoorion is not changed then it is always `Z` bump


release of `X` stage will be after all current phases will be ended

every phase end is bump of `Y`

every step now should be bump of `Z`, pushed to origin dev branch, pull request created and automerged to master branch

after all workflows ends then pull it back to dev on origin and pulled to local repository
````

The questions they answer (docs/devlog/BRAINSTORM.md), word for word:

````markdown
## Q13: trying the platforms for real

All six publication plugins are tested only against fakes. Which accounts
can be used for a first real post, and may the agent post there (one test
post each, deleted afterwards where the platform allows)?

*Lean:* the author gives a test account per platform in the vault and the
go-ahead per platform; the agent runs `amoorion publish` once each and
fixes what the real API answers differently.

Ready for it: `uv run task test:live -- <platform>…` posts one marked test
post per platform named, reads it back and replies to it where the plugin
can, and prints the links (no plugin deletes yet, so deleting is by hand).
It covers the communication platforms of phase 3 too: Discord (bot and
webhook), Telegram, Matrix. The author can run it alone, or name the
platforms the agent may run it for.

## Q14: deleting posts

No plugin can delete. The live tests (Q13) leave their test posts behind,
and a post sent by mistake can only be removed by hand on each platform.

- no deleting: amoorion only adds; mistakes are fixed by hand
- a `delete` capability and method (`amoorion delete --platform x --id …`),
  where the platform allows it (all but Blogger by mail and the Discord
  webhook without its message id kept; Telegram only within 48 hours in
  groups), not `read_only`, so agents get it only as a destructive tool
- only inside the live tests, through each platform's API directly

*Lean:* a `delete` capability and method; the live test then deletes its
own test post and reply.

## Q15: releases and packages

The inquiry's release workflows are in place (docs/releasing.md); a few
choices in them are the author's to confirm before the first merge to
`master`:

- "git package": the built wheels and source archives attached to each
  GitHub release. GitHub Packages has no Python registry; a container
  image on ghcr.io fits phase 6 (Dockerfile). Enough, or the image now?
- one version for all packages (lock-step), bumped together; or each
  plugin package versioned on its own (more work per release)?
- the PyPI names `amoorion` and `amoorion-<platform>`, ten projects, each
  with a trusted publisher; and the `pypi` environment with or without a
  required reviewer.

*Lean:* release assets now and the image in phase 6, lock-step versions,
the `pypi` environment with the author as required reviewer.
````

**Decisions** (as I read the answers above):

- **Q13:** the platforms' secrets stay in the Bitwarden vault, reached by
  `bw`, now installed by npm in `tools/` (`tools/node_modules/.bin/bw`);
  the access to it (the session of `bw unlock`) is initialized into
  `.env` by a task, so `.env` holds the link and the session, never the
  platforms' secrets. The live tests of all platforms run under one
  command, and the agent has the go-ahead to try the real APIs.
- **Q14:** a `delete` capability and method that first stores what it
  deletes; the same storage keeps the read state of all posts on every
  platform, as JSON files with an index per profile,
  `dataset/<platform>/<profile>/`; `dataset/` is gitignored.
- **Q15:** each package has its own version and is bumped only when it
  changed; `amoorion` is bumped at every release (a `Z` bump when it
  didn't change). Every step is a `Z` bump, pushed to development, its
  pull request created and merged by itself; a phase completed is a `Y`
  bump of all packages; `X` comes when all current phases (0–6) are
  done. A `Z` release carries and publishes only the bumped packages, an
  `X` or `Y` release all of them. After all workflows of a release end,
  master is merged back into development on origin and pulled locally.

## UNIXUSAT=1793085944110 · commit 397143f

The author's third inquiry (docs/devlog/INQUIRIES.md), word for word:

````markdown
---

# rebuild of presentation page

we need to produce similar styled templating of readthedocs setup of sphinx, similar jekyll theme paging and reforging of README to present better project.

in resources there are graphics, one logo and one mockup of page

now we have also whole presentative page source code: https://github.com/Sarverott/amoorion-website

in github-pages you can place produced marimo examples html, manifest files and builded source code for amoorion-website

# llms.txt, robots.txt and error pages
add according to that 
- https://pypi.org/project/sphinx-llm/
- https://docs.readthedocs.com/platform/stable/reference/agent-skills.html
- https://docs.readthedocs.com/platform/stable/reference/llms-txt.html
- https://docs.readthedocs.com/platform/stable/reference/markdown-for-agents.html
- https://docs.readthedocs.com/platform/stable/reference/404-not-found.html
- https://docs.readthedocs.com/platform/stable/reference/robots.html
````

Drawn, with the answers to Q13–Q15, into the plan: VISION.md phase 2
items 6–8 and phase 4 items 9–11, TODO.md phases 2 and 4. The author's
order in the chat with it: "adopt all these you will find around and
update all according to new information. proceede new guidelines and
commit on every small step you does."
