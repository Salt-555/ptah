# Ptah

Master agentic engineer and build foreman for [Hermes Agent](https://hermes-agent.nousresearch.com/docs).
Takes a vague, fuzzy product idea and ships merged-quality code through ephemeral
specialist subagents — no slab code (big unreviewed AI dumps), no self-review,
no "should pass."

## What it is

One orchestrator + two constructed-per-dispatch worker roles:

| Role | Brief kernel |
|---|---|
| builder | Terse TDD zealot. No code without a failing test. Incremental file writes; final message under 100 words. Consolidates instead of duplicating. |
| judge | Paranoid auditor with switchable lenses: SPEC, QUALITY, RESIDUE (a mechanical dead-code sweep — residue is a critical finding), ADVERSARIAL (money/auth/security surfaces). |

A **lane** is how much pipeline a task gets, chosen by objective criteria
(FAST / FULL — spend tokens proportional to the work's risk surface, never
to the agent's confidence). The foreman plans inline; an architect subagent
is dispatched only for genuinely large builds (10+ tasks), which time out.

**Discipline that the traces demanded** (hard-won over 15+ real runs):
- **Delegation mechanics**: dedup-check before any dispatch; a timed-out
  delegate is mined from its transcript, never hunted with `ps`; max 2 fix
  loops, then resample; a wall-clock budget stops silent retry loops.
- **Evidence ships with the artifact**: verification scripts, screenshots and
  probe outputs land in `_verify/` beside the deliverable — never /tmp.
- **Screenshot before claim**: anything visual requires the actual pixels
  seen before it's claimed working.
- **No duplicate implementations**: builders search the repo before shipping
  a function that already exists.

**Bounded repair** (Hermes 4): max 2 fix loops per task, then throw away the
worktree and resample a fresh builder — generating a new attempt is often
cheaper than patching a broken one. A twice-failed resample means the *task*
was wrong, not the workers.

**Model policy**: everything inherits the profile's model — no pins, no
tiering, no reviewer-model asking. Same-lineage review is the Operator's
choice; the decorrelation principle (judges with different weights from the
generator avoid self-preference bias — Hermes 4 Technical Report,
arXiv:2508.18255 §2.1.2) is cited on request, never imposed.

## Trust & safety — read before installing

This profile ships **executable doctrine**: on install, the agent can spawn
subagents, create git worktrees, and run terminal commands. Before first run,
read:

- `AGENTS.md` — the operating doctrine and iron laws
- `skills/ptah-pipeline/SKILL.md` — the pipeline the agent will execute (no
  bundled scripts; the profile spawns nothing outside Hermes itself)

**Isolation:** profile installs are scoped entirely to
`~/.hermes/profiles/ptah/` — your root config, `auth.json`, `.env`, memories,
and sessions are never touched. Your existing default agent keeps working;
ptah runs beside it via `-p ptah` or an alias. `hermes profile update` replaces
doctrine files (SOUL.md, AGENTS.md, skills/) — keep personal edits elsewhere
or expect to redo them on update.

**Credentials:** none shipped, none needed beyond what your Hermes already
has. Reviews run on whatever model/provider your Hermes is configured for.
Review payloads (specs + diffs) are sent to the provider you configured —
don't point reviews at code you wouldn't send to that provider.

## Install

Prerequisites: [Hermes Agent](https://hermes-agent.nousresearch.com/docs) >= 0.14.0, git.

```bash
hermes profile install github.com/Salt-555/ptah --alias
```

`--alias` gives you a `ptah` command. Without it, run everything as
`hermes -p ptah …`.

### First run

1. **Model** — ptah ships no model choice. Run `hermes model` (or edit
   `model:` in `~/.hermes/profiles/ptah/config.yaml`) to set the model and
   provider you want the foreman and its workers to run on. Everything
   (delegates included) inherits it by design.
2. **Workspace** — `terminal.cwd` in the profile's `config.yaml` defaults to
   `~/projects`; point it wherever you keep code.
3. **Name** — the persona reports to "the Operator" by default. Put your name
   in `SOUL.md` if you want it addressed personally (note: profile updates
   replace SOUL.md — redo after updates or keep a patch).
4. **Reviewer model** — you'll be asked on the first real build. Your agent
   will list what your provider serves and recommend a model from a different
   family than your implementer; you decide, and the choice is remembered.

Then try:

```
ptah, build me a small CLI that dedupes CSVs by email column, with tests
```

### Skills environment

Ptah runs on the **Hermes-bundled dev skills** — nothing external is required
or shipped. On first launch Hermes seeds its built-in software-development
surface (TDD, systematic-debugging, requesting-code-review, codebase
inspection, simplify-code, spike, dogfood QA, debugger skills, the agent CLIs,
and the `github` category). All of it is enabled by default; to trim, use
`hermes -p ptah skills config`.

### Updates

```bash
hermes profile update ptah
```

Pulls new versions, keeps your memories, sessions, and `.env` untouched.
`config.yaml` is preserved too (you tuned it); pass `--force-config` to reset
to shipped defaults.

## Files

- `SOUL.md` — identity and character (the one place to personalize)
- `AGENTS.md` — operating doctrine, iron laws
- `skills/ptah-pipeline/` — the executable job description
- `config.yaml` — clean starting config; you set model/provider/workspace

## License

MIT — see [LICENSE](LICENSE).
