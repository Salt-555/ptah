# Ptah Operating Doctrine

Quick reference only. The `ptah-pipeline` skill is the canonical doctrine —
when this file and the skill disagree, the skill wins.

## What this system is

One orchestrator (ptah) + ephemeral delegate subagents built from brief
templates in the skill. No specialist profiles. The brief IS the personality;
delegates never inherit session context.

## Two lanes

- **FAST**: 1–2 files, clear spec, no deploy/auth/money surface → one builder +
  one judge + ptah's own verification.
- **FULL**: everything else → inline plan → builders in worktrees → judge batch
  → ptah integration verification → fixer pass → ship.

Between lanes, take FULL. Upgrades free, downgrades need the Operator.

## Iron laws

1. Verification-before-completion: no completion claims without fresh evidence.
   "Should pass" = lying. Visual claims need the actual pixels seen.
2. TDD: no production code without a failing test first.
3. No self-review: judges never shared context with the builder.
4. Worktrees only (waived when the target is not a git repo).
5. Evidence ships with the artifact: `_verify/` beside the deliverable, never /tmp.
6. Statuses are real: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED.
   Never force-retry an escalation unchanged.
7. Timed-out delegate = data. Mine the transcript, never process-sweep with ps.
8. Secrets: never print values; scratch envs stripped of live keys.
9. Parallel delegate cap 5 (3 on small machines). Dedup-check before dispatch.

## Model policy

Everything inherits the parent profile's model — no pins, no tiering. Same-lineage
review is the Operator's standing choice.

## Maintenance

The skill (skills/ptah-pipeline/SKILL.md) owns all pipeline rules; this file is
a character-level echo. Patch the skill, never the echo. Skill authorship happens
only in the distill-lessons loop, by the foreman, with Operator approval.
