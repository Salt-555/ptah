# Ptah

Master agentic engineer and build foreman for [Hermes Agent](https://hermes-agent.nousresearch.com/docs).
Takes a vague, fuzzy product idea and ships merged-quality code through ephemeral
specialist subagents — no slab code (big unreviewed AI dumps), no self-review,
no "should pass."

## What it is

One orchestrator + constructed-per-dispatch delegate personas:

| Persona | Brief kernel |
|---|---|
| architect | Opinionated senior designer. Writes the plan. |
| implementer | Terse TDD zealot. No code without a failing test. |
| spec-reviewer | Paranoid auditor. Code vs spec, line by line. Missing AND extra = fail. |
| quality-reviewer | Perfectionist gate. Critical/Important/Minor findings. |
| adversarial | Professional attacker. Buyer/user/abuser lenses. Verdict demanded. |
| fixer | Surgeon. Fixes ONLY listed findings. No refactors. |
| ops | Calm operator. Dry-run, verify live, restore zero-state. |

A **gate** is a hard checkpoint: if it fails, work stops and loops until it
passes. The pipeline: G0 plan/thesis → G1 per-task implement/review loop →
G2 integration smoke (orchestrator personally) → G3 adversarial batch →
G4 polish → G5 ship with live verification. Small tasks (1-2 files, ~an hour,
clear spec) use a bypass: one implementer, one review, done — the full
pipeline is for real builds.

**Cross-lineage review** (from the Hermes 4 technical report, arXiv:2508.18255):
reviewers run on a *different model family* than the implementer — judges with
different weights than the generator don't share its self-preference. Ptah
ships **no reviewer model**: on the first review it asks you which model to
use, examining what your own configured provider serves, and recommends a
cross-lineage pick. Reviewers are bare completions (no tools, no injected
context, read-only by construction) via the bundled `ptah_review.py`, running
through your own Hermes CLI — your provider, your credentials, nothing
hardcoded.

**Bounded repair** (also Hermes 4): max 2 fix loops per task, then throw away
the worktree and resample a fresh implementer — generating a new attempt is
often cheaper than patching a broken one. A twice-failed resample means the
*task* was wrong, not the workers.

## Trust & safety — read before installing

This profile ships **executable doctrine**: on install, the agent can spawn
subagents, create git worktrees, and run terminal commands. Before first run,
read:

- `AGENTS.md` — the operating doctrine and iron laws
- `skills/ptah-pipeline/SKILL.md` — the pipeline the agent will execute
- `skills/ptah-pipeline/scripts/ptah_review.py` — the one subprocess-spawning script

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
- `skills/ptah-pipeline/` — the executable job description + reviewer script
- `config.yaml` — clean starting config; you set model/provider/workspace

## License

MIT — see [LICENSE](LICENSE).
