#!/usr/bin/env python3
"""Ptah bare-completion reviewer — runs on the recipient's own Hermes agent.

No auth, no endpoints, no provider or model pins in this file. The reviewer
session runs through the recipient's installed `hermes` CLI with THEIR
config, THEIR provider, THEIR credentials (the documented programmatic path:
`hermes chat --oneshot -Q --query-file`). This script only:
  1. builds the review prompt for the requested lens,
  2. invokes hermes with NO toolsets (read-only by construction),
  3. validates the verdict object — fail-closed on ANY error.

The reviewer MODEL is a decision the recipient makes (the ptah-pipeline skill
asks them which model their provider serves for reviews). This script never
picks one: without --model it inherits the recipient's configured default.
Cross-lineage doctrine (Hermes 4 rule, arXiv:2508.18255 §2.1.2 — judge
weights must differ from generator weights) lives in the skill, which passes
--model when the user chose a reviewer model.

Usage:
    ptah_review.py <review_type> <payload_file> [--model MODEL_ID] [--timeout S]
      review_type: spec | quality | adversarial-user | adversarial-abuser | adversarial-buyer
      payload_file: JSON {"verdict_contract": "...", "context": "...",
                          "evidence": "..."}

Writes verdict JSON to stdout; exits 2 on ANY failure — CLI error, transport,
unreadable payload, or a model response that is not a valid verdict object
(fail-closed: an unavailable or degraded reviewer is never an approval).
Usage errors exit 1 before anything runs.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

REVIEW_TYPES = ("spec", "quality", "adversarial-user", "adversarial-abuser",
                "adversarial-buyer")

VALID_VERDICTS = {"APPROVED", "REJECTED", "NEEDS_CONTEXT"}


class _ArgParser(argparse.ArgumentParser):
    """Usage errors exit 1 (ptah contract: exit 2 is reserved for fail-closed)."""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        sys.exit(1)


def build_prompt(review_type, payload):
    contracts = {
        "spec": (
            "You are a paranoid spec-compliance reviewer. The implementer's "
            "report may be incomplete or optimistic; verify against the "
            "evidence only. Findings need file:line evidence. Do NOT trust "
            "the report. Missing requirements AND unrequested extras both fail."
        ),
        "quality": (
            "You are a code-quality reviewer. Fair but unsoftened. Check: "
            "single responsibility, error handling on I/O, no magic numbers, "
            "no debug prints, tests assert invariants not snapshots, security "
            "smells. Report Strengths / Issues (Critical/Important/Minor) / "
            "Assessment (Ready or Not yet)."
        ),
        "adversarial-user": (
            "You are an adversarial USER. Follow the documented behavior "
            "LITERALLY and verify every claim against the evidence. Find "
            "doc-vs-reality contradictions. Verdict demanded, not vibes."
        ),
        "adversarial-abuser": (
            "You are an adversarial ABUSER. Attack money/security paths: "
            "races, double-spend, injection, auth bypass, secret leaks, "
            "input validation gaps. Severity-ranked findings with evidence."
        ),
        "adversarial-buyer": (
            "You are an adversarial BUYER. Try to lose money or be misled: "
            "refund logic, consent, point-of-payment honesty, misleading "
            "claims. Severity-ranked findings with evidence."
        ),
    }
    return (
        f"{contracts[review_type]}\n\n"
        "OUTPUT CONTRACT: return ONLY valid JSON, nothing else:\n"
        '{"verdict": "APPROVED" | "REJECTED" | "NEEDS_CONTEXT", '
        '"findings": [{"severity": "critical"|"high"|"medium"|"low", '
        '"location": "file:line or endpoint", "issue": "...", "evidence": "..."}], '
        '"summary": "one sentence"}\n\n'
        f"<payload>\n{json.dumps(payload, indent=1)}\n</payload>"
    )


def extract_json(content):
    """Pull the outermost JSON object out of a possibly-fenced response."""
    m = content.find("{")
    end = content.rfind("}") + 1
    if m == -1 or end <= m:
        return None
    try:
        return json.loads(content[m:end])
    except (json.JSONDecodeError, ValueError):
        return None


def validate_verdict(obj):
    """Fail-closed gate: a response is a verdict only if fully well-formed."""
    if not isinstance(obj, dict):
        return False
    if obj.get("verdict") not in VALID_VERDICTS:
        return False
    if not isinstance(obj.get("findings", []), list):
        return False
    if not isinstance(obj.get("summary"), str):
        return False
    return True


def run_reviewer_cli(prompt, model, timeout):
    """Invoke the recipient's own hermes CLI as a context-free reviewer.

    Read-only by construction: toolsets resolve to none, rules/memory/skills
    are not injected (--ignore-rules), and the run is tagged as tool-source so
    review sessions stay out of the user's session lists.
    """
    fd, prompt_path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(prompt)
        cmd = [
            "hermes", "chat", "--oneshot", "-Q",
            "--query-file", prompt_path,
            "--ignore-rules",      # no AGENTS.md/memory/skill injection: no shared context
            "-t", "none",          # not a valid toolset name -> zero tools resolve
            "--source", "tool",    # documented non-pollution tag for integrations
        ]
        if model:
            cmd += ["-m", model]
        # Strip HERMES_* inheritance: a parent session's env must not re-arm
        # toolsets or leak run context into the reviewer.
        env = {k: v for k, v in os.environ.items() if not k.startswith("HERMES_")}
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=env)
    finally:
        os.unlink(prompt_path)


def main():
    ap = _ArgParser()
    ap.add_argument("review_type", choices=REVIEW_TYPES)
    ap.add_argument("payload_file")
    ap.add_argument("--model", default=None,
                    help="reviewer model id served by the recipient's provider "
                         "(chosen by the user; omit to inherit their configured default)")
    ap.add_argument("--timeout", type=int, default=600,
                    help="seconds to wait for the reviewer session (default 600)")
    args = ap.parse_args()

    def fail_closed(e):
        # fail-closed: ANY failure — transport, CLI, payload — is never an approval
        print(json.dumps({"verdict": "NEEDS_CONTEXT",
                          "findings": [{"severity": "critical",
                                        "location": "transport",
                                        "issue": f"reviewer unavailable: {e}"}],
                          "summary": "review failed - fail-closed"}))
        return 2

    try:
        with open(args.payload_file) as f:
            payload = json.load(f)
    except Exception as e:
        return fail_closed(e)

    try:
        proc = run_reviewer_cli(build_prompt(args.review_type, payload),
                                args.model, args.timeout)
    except Exception as e:
        return fail_closed(e)

    if proc.returncode != 0:
        return fail_closed(f"hermes chat exited {proc.returncode}: "
                           f"{(proc.stderr or proc.stdout)[:300]}")

    # "-Q" prints the final response; the outermost JSON object is the verdict.
    parsed = extract_json(proc.stdout)
    if parsed is None:
        return fail_closed(f"unparseable review response: {proc.stdout[:300]}")
    if not validate_verdict(parsed):
        return fail_closed("response lacked a valid "
                           "APPROVED/REJECTED/NEEDS_CONTEXT verdict")
    print(json.dumps(parsed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
