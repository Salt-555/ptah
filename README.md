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
G4 polish → G5 ship with live verification.

**Cross-lineage review** (from the Hermes 4 technical report, arXiv:2508.18255):
reviewers run on a *different model family* than the implementer — judges with
different weights than the generator don't share its self-preference. Reviewers
are bare completions (no tools, provably read-only) via the bundled
`ptah_review.py`; any two different-family models work, the defaults are just
ours.

**Bounded repair** (also Hermes 4): max 2 fix loops per task, then throw away
the worktree and resample a fresh implementer — generating a new attempt is
often cheaper than patching a broken one. A twice-failed resample means the
*task* was wrong, not the workers.

## Trust & safety — read before installing

This profile ships **executable doctrine**: on install, the agent can spawn
subagents, create git worktrees, run terminal commands, and (only if you
authorize deploys) touch live infrastructure. Before first run, read:

- `AGENTS.md` — the operating doctrine and iron laws
- `skills/ptah-pipeline/SKILL.md` — the pipeline the agent will execute
- `skills/ptah-pipeline/scripts/ptah_review.py` — the one networked script

**Data egress:** review payloads contain your code diffs and are sent to
Nous's inference API (`inference-api.nousresearch.com`) for judgment by a
third-party-lineage model. Do not point Ptah at proprietary code you would
not send to an external API. The documented fallback (delegate reviewers,
same lineage, no external calls) is in the skill.

## Install

Prerequisites: [Hermes Agent](https://hermes-agent.nousresearch.com/docs) >= 0.12.0, git, a Nous Portal account.

```bash
hermes profile install github.com/Salt-555/ptah
hermes login --provider nous    # reviewer auth rides your own auth.json
hermes -p ptah
```

Recipients bring their own credentials — `auth.json` and `.env` are never
shipped. Point `model.default` in the installed `config.yaml` at whatever
provider/model you want Ptah and its delegates to run on; everything inherits
the parent model by design.

### First run

Customize three lines: `model.default` (config.yaml), `terminal.cwd`
(config.yaml), and your name in `SOUL.md` (the persona reports to "Salt" —
that's us, make it you). Then try:

```
ptah, build me a small CLI that dedupes CSVs by email column, with tests
```

## Files

- `SOUL.md` — identity and character
- `AGENTS.md` — operating doctrine, roster, gates, iron laws
- `skills/ptah-pipeline/` — the executable job description + reviewer script
- `config.yaml` — clean starting config (no personal endpoints, no channel IDs)

## License

MIT — see [LICENSE](LICENSE).
