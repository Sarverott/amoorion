# Phase 5: linking

## The list of the phase, and the old notebooks

UNIXUSAT=1793372376697 · commit 9abd654

The author's words:

> that check there returns this: "This workflow run required approval but was not approved before it expired." - this can be first think to be repaired in phase 5, do all of our current step list for this phase then at next step after them change every name of jupyter notebook examples file from "<NAME>.ipynb" into "old.<NAME>.ipynb". we will gonna need list of examples to be presented - based on pseudocode written and descriptions try to implement functionalities i am gonna present this way. let's go!

**Check.** `check` runs on pull requests to development only: the flow's own
to master waited for an approval nobody gives, and the flow checks before merging.

**A 502 on the way.** GitHub answered 502 when the flow started the release
of v0.4.5, after the merge, leaving master untagged. The author noticed my
watcher waiting on it and halted it. The flow now tries five times; the next
push released v0.4.5 by itself.

**Hooks.** `github`, `gitlab` and `discord`, one module each.

**ntfy.** A plugin, and a target: the method `notify` sends to the platforms
of `AMOORION_NOTIFY`, and everything the hooks receive goes there too. That
variable is my reading of "notification target"; the rules of Q11 can replace it.

**NATS.** Off unless `AMOORION_NATS` names a server. Tested against a fake
client only; no server has been tried.

**E-mail.** `amoorion-email`: SMTP, IMAP, reply; Blogger shares its sending.

**Notebooks.** Renamed `old.<NAME>.ipynb`; they still run and build. The phase
stays open for the author's list of new examples.
