# Ptah

Master agentic engineer and build foreman for [Hermes Agent](https://hermes-agent.nousresearch.com/docs).
Takes a vague, fuzzy product idea and ships merged-quality code through ephemeral
specialist subagents — no slab code, no self-review, no "should pass."

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

Gates G0-G5: plan → per-task implement/spec/quality loop → integration smoke →
adversarial batch → clean pass → ship with live verification.

**Cross-lineage review:** implementers and reviewers run on *different model
families* (decorrelated failure modes). Reviewers are bare completions — no
tools, provably read-only, ~2-3 cents per review — via the bundled
`ptah_review.py` (defaults: qwen3.8-max reviewers vs a GLM-lineage implementer;
one-line swap in `MODELS` to change reviewer lineage).

## Install

```bash
hermes profile install github.com/Salt-555/ptah
```

## License

MIT
