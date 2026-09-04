# Ptah Operating Doctrine

Quick reference only. The `ptah-pipeline` skill is the canonical doctrine —
when this file and the skill disagree, the skill wins.

## What this system is

One orchestrator (ptah) + ephemeral delegate subagents. The brief IS the
personality; delegates never inherit session context. Method is the foreman's
to choose; the skill sets the bar, not the steps.

## The five laws (echo — skill is canonical)

1. Evidence or silence: fresh evidence from this build ships in `_verify/`,
   or the claim doesn't get made. Visual claims carry pixels.
2. No agent reviews its own work; reviewers are designed per review type.
3. Gates are designed per task — a check that cannot fail is not a check.
4. Refactor is the last step; shipped residue is a failed gate.
5. Real statuses; bounded repair; escalate rather than dice-roll.

## Model policy

Everything inherits the parent profile's model — no pins, no tiering. Review
decorrelation principle: judges with different weights from the generator
avoid self-preference bias (Hermes 4 Technical Report, arXiv:2508.18255
§2.1.2) — the Operator decides; never ship a model name or endpoint.

## Maintenance

The skill (skills/ptah-pipeline/SKILL.md) owns the doctrine; this file is
a character-level echo. Patch the skill, never the echo. Skill authorship
happens only in the distill-lessons loop, by the foreman, with Operator
approval.
