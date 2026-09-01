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

Then:

```bash
hermes login --provider nous    # reviewer script reads your own auth.json
hermes -p ptah
```

Recipients bring their own credentials — `auth.json` and `.env` are never
shipped. Point `model.default` in the installed `config.yaml` at whatever
provider/model you want Ptah and its delegates to run on; everything inherits
the parent model by design.

## Files

- `SOUL.md` — identity and character
- `AGENTS.md` — operating doctrine, roster, gates, iron laws
- `skills/ptah-pipeline/` — the executable job description + reviewer script
- `config.yaml` — clean starting config (no personal endpoints, no channel IDs)

## License

MIT
