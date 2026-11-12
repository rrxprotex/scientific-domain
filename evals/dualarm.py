#!/usr/bin/env python3
"""Dual-arm benchmark: measure what the skill actually changes in model output.

This is the instrument behind `liveModelDualArm.status`. WITHOUT a model command
it reports NOT_RUN - the honest state, and the state this repository ships in.
WITH commands it runs each task twice (skill loaded / not loaded), collects the
raw artifacts, and - if a judge command is supplied - grades them with the fixed
rubric below. A high absolute score with a near-zero delta is NOT evidence of
benefit; the delta is the number that matters.

Usage:

    # honest default: no model configured -> NOT_RUN
    python evals/dualarm.py

    # two arms, identical except for the skill being loaded
    python evals/dualarm.py \
        --on  "my-model-cmd --system prompts/with-skill.txt" \
        --off "my-model-cmd --system prompts/without-skill.txt" \
        [--judge "my-judge-cmd"] [--runs 3]

Artifacts land in `dualarm-artifacts/`, results in `dualarm-results.json`.
The judge receives JSON on stdin {"prompt":..., "output":...} and must emit JSON
{"R1": 0/1, "R2": 0/1, "R3": 0/1, "R4": 0/1, "R5": 0/1}.

Rubric (applied to each produced artifact):
  R1 only canonical term ids (no invented terms)
  R2 citation present with a status label
  R3 a theory link is never graded OBSERVED
  R4 every causal claim carries rivals + a falsifier
  R5 every record carries a claim_limit
  R6 the cited evidence supports the claim it is attached to
     (the judge's reading; structural checks alone cannot establish this)

Status honesty: `RUN` is reported ONLY when both arms produced artifacts, the
judge ran, its output passed the strict 0/1 schema on every rubric key, and at
least one artifact per arm was judged. Otherwise the status says what is
missing (`ARTIFACTS_COLLECTED_GRADING_NOT_RUN` / `GRADING_INCOMPLETE`) - a
benchmark that can claim RUN without a real measurement is worse than none.

Stdlib only. Does not call any API itself; the commands you give it do.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "dualarm-results.json"
ARTIFACTS = ROOT / "dualarm-artifacts"
CASES = HERE / "cases.json"

RUBRIC = ["R1", "R2", "R3", "R4", "R5", "R6"]

NOT_RUN_REASON = (
    "No model command is configured. Static suites validate a deterministic "
    "classifier and the validator; they do not prove that a model follows the "
    "skill or produces better research. Run this script with --on/--off arms to "
    "produce the measurement."
)


def run_arm(command: str, prompt: str) -> str:
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()
    r = subprocess.run(parts + [prompt], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    return r.stdout


def _normalize_scores(scores):
    """Strict judge schema: every rubric key present, value exactly 0 or 1.

    Anything else - missing keys, "0" strings, floats, nulls - invalidates the
    whole judgement (returns None). A truthy coercion (bool("0") == True) would
    silently score a zero as one.
    """
    if not isinstance(scores, dict):
        return None
    out = {}
    for k in RUBRIC:
        v = scores.get(k)
        if isinstance(v, bool):
            v = 1 if v else 0
        if v not in (0, 1):
            return None
        out[k] = v
    return out


def judge(command: str, prompt: str, output: str):
    """Return {R: 0/1}, or None when the judge output fails the strict schema."""
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()
    r = subprocess.run(parts, input=json.dumps({"prompt": prompt, "output": output}),
                       capture_output=True, text=True, encoding="utf-8", timeout=600)
    try:
        scores = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    return _normalize_scores(scores)


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--on", help="model command WITH the skill loaded")
    p.add_argument("--off", help="model command WITHOUT the skill")
    p.add_argument("--judge", help="judge command grading one artifact against the rubric")
    p.add_argument("--runs", type=int, default=1, help="repetitions per case per arm (default 1)")
    args = p.parse_args(argv)

    started = datetime.now(timezone.utc).isoformat()
    if not (args.on and args.off):
        RESULTS.write_text(json.dumps({
            "schemaVersion": 1,
            "startedAt": started,
            "status": "NOT_RUN",
            "reason": NOT_RUN_REASON,
            "rubric": RUBRIC,
            "interpretation": "Do not upgrade NOT_RUN to RUN without a real dual-arm "
                              "model run; the delta between arms is the only evidence "
                              "of benefit.",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("dual-arm: NOT_RUN (no model command configured)")
        print(f"Results: {RESULTS}")
        return 0

    prompts = [c["prompt"] for c in json.loads(CASES.read_text(encoding="utf-8"))["cases"]]
    ARTIFACTS.mkdir(exist_ok=True)
    arms = {"on": args.on, "off": args.off}
    per_arm = {}
    for arm, command in arms.items():
        scores = {k: 0 for k in RUBRIC}
        judged = 0
        judge_errors = 0
        for i, prompt in enumerate(prompts):
            for rep in range(args.runs):
                out = run_arm(command, prompt)
                (ARTIFACTS / f"{arm}-{i:03d}-{rep}.txt").write_text(out, encoding="utf-8")
                if args.judge:
                    s = judge(args.judge, prompt, out)
                    if s is None:
                        judge_errors += 1
                    else:
                        judged += 1
                        for k in RUBRIC:
                            scores[k] += s[k]
        per_arm[arm] = {
            "rubric_totals": scores,
            "artifacts_judged": judged,
            "judge_errors": judge_errors,
        }

    def rate(arm, k):
        n = per_arm[arm]["artifacts_judged"]
        return round(per_arm[arm]["rubric_totals"][k] / n, 4) if n else None

    delta = {k: (None if rate("on", k) is None or rate("off", k) is None
                 else round(rate("on", k) - rate("off", k), 4)) for k in RUBRIC}
    total_judge_errors = sum(per_arm[a]["judge_errors"] for a in arms)
    judged_in_both = all(per_arm[a]["artifacts_judged"] > 0 for a in arms)
    if not args.judge:
        status = "ARTIFACTS_COLLECTED_GRADING_NOT_RUN"
    elif judged_in_both and total_judge_errors == 0:
        status = "RUN"
    else:
        status = "GRADING_INCOMPLETE"
    payload = {
        "schemaVersion": 1,
        "startedAt": started,
        "status": status,
        "arms": {"on": args.on, "off": args.off},
        "runs_per_case": args.runs,
        "cases": len(prompts),
        "per_arm": per_arm,
        "judge_errors": total_judge_errors,
        "delta_on_minus_off": delta,
        "interpretation": "The delta is the evidence of benefit. A high absolute "
                          "score with a near-zero delta is NOT evidence. RUN is "
                          "only reported when both arms were judged with a "
                          "schema-valid judge and zero judge errors. Report "
                          "per-case artifacts alongside the numbers.",
    }
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print(f"dual-arm: {payload['status']}")
    print(f"delta (on-off): {delta}")
    print(f"Results: {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
