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
