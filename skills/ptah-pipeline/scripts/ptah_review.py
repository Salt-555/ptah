#!/usr/bin/env python3
"""Ptah bare-completion reviewer — cross-lineage review via Nous Portal.

Dispatch pattern for spec/quality/adversarial reviews:
a review is a BARE COMPLETION, not an agent. No tools = provably read-only
and costs ~2-3 cents per review.

Reviewer: qwen/qwen3.8-max (Alibaba lineage), decorrelated from the
implementer lineage per the Hermes 4 rule (arXiv:2508.18255 §2.1.2): judge
weights must differ from generator weights to prevent self-preference.
(Do NOT cite DHH's two-model workflow here — that is an interaction-speed
pattern, not decorrelation.)

Usage (from the ptah profile):
    python3 <profile>/skills/ptah-pipeline/scripts/ptah_review.py <review_type> <payload_file>
      review_type: spec | quality | adversarial-user | adversarial-abuser
      payload_file: JSON {"verdict_contract": "...", "context": "...",
                          "evidence": "..."}

Writes verdict JSON to stdout; exits 2 on ANY failure — transport, missing
auth, unreadable payload (fail-closed: an unavailable reviewer is never an
approval). Data-egress note: the payload (which contains code diffs) is sent
to https://inference-api.nousresearch.com and processed by a third-party-lineage
model. Do not review proprietary code you would not send to an external API.
"""
import json
import os
import sys
import urllib.request

MODELS = {
    "spec": "qwen/qwen3.8-max",
    "quality": "qwen/qwen3.8-max",
    "adversarial-user": "qwen/qwen3.8-max",
    "adversarial-abuser": "qwen/qwen3.8-max",
}

BASE = "https://inference-api.nousresearch.com/v1/chat/completions"


def load_token():
    auth = json.load(open(os.path.expanduser("~/.hermes/auth.json")))

    def find_nous(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "nous":
                    yield v
                yield from find_nous(v)
        elif isinstance(d, list):
            for v in d:
                yield from find_nous(v)

    for v in find_nous(auth):
        if isinstance(v, list):
            v = v[0] if v else None
        if isinstance(v, dict):
            tok = v.get("access_token")
            if tok:
                return tok
    raise RuntimeError("no nous token in auth.json")


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
    }
    return (
        f"{contracts[review_type]}\n\n"
        f"OUTPUT CONTRACT: return ONLY valid JSON: "
        f'{{"verdict": "APPROVED" | "REJECTED" | "NEEDS_CONTEXT", '
        f'"findings": [{{"severity": "critical"|"high"|"medium"|"low", '
        f'"location": "file:line or endpoint", "issue": "...", "evidence": "..."}}], '
        f'"summary": "one sentence"}}\n\n'
        f"<payload>\n{json.dumps(payload, indent=1)}\n</payload>"
    )


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    review_type, payload_path = sys.argv[1], sys.argv[2]
    if review_type not in MODELS:
        print(f"unknown review_type {review_type}; choices: {list(MODELS)}")
        return 1

    def fail_closed(e):
        # fail-closed: ANY failure — transport, auth, payload — is never an approval
        print(json.dumps({"verdict": "NEEDS_CONTEXT",
                          "findings": [{"severity": "critical",
                                        "location": "transport",
                                        "issue": f"reviewer unavailable: {e}"}],
                          "summary": "review failed - fail-closed"}))
        return 2

    try:
        payload = json.load(open(payload_path))
    except Exception as e:
        return fail_closed(e)

    try:
        token = load_token()
    except Exception as e:
        return fail_closed(e)

    body = json.dumps({
        "model": MODELS[review_type],
        "messages": [{"role": "user", "content": build_prompt(review_type, payload)}],
        "temperature": 0.1,
        "max_tokens": 4000,  # reasoning model: thinking tokens count against this
    }).encode()

    req = urllib.request.Request(
        BASE, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "ptah-review/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
        msg = data["choices"][0]["message"]
        content = msg.get("content")
        if not content:  # reasoning model burned tokens thinking; force non-thinking retry
            body2 = json.dumps({
                "model": MODELS[review_type],
                "messages": [{"role": "user", "content": build_prompt(review_type, payload)
                              + "\n\nIMPORTANT: respond with the JSON only. No thinking."}],
                "temperature": 0.1,
                "max_tokens": 8000,
            }).encode()
            req2 = urllib.request.Request(
                BASE, data=body2, method="POST",
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req2, timeout=120) as resp2:
                data = json.load(resp2)
            content = data["choices"][0]["message"].get("content") or ""
            if not content:
                raise RuntimeError("model returned only reasoning, no content")
        # extract JSON from response (tolerate fences)
        m = content.find("{")
        end = content.rfind("}") + 1
        if m == -1 or end <= m:
            print(json.dumps({"verdict": "NEEDS_CONTEXT",
                              "findings": [], "summary": "unparseable review response",
                              "raw": content[:500]}))
            return 2
        print(content[m:end])
        return 0
    except Exception as e:  # fail-closed: transport errors are NEVER approvals
        print(json.dumps({"verdict": "NEEDS_CONTEXT",
                          "findings": [{"severity": "critical",
                                        "location": "transport",
                                        "issue": f"reviewer unavailable: {e}"}],
                          "summary": "review transport failed - fail-closed"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
