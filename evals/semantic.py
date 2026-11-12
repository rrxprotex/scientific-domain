#!/usr/bin/env python3
"""Structural grader for multi-record outputs.

This grader is DETERMINISTIC and model-free. It checks the STRUCTURE of a
record store (a model's output for a task) against seven fixed rules. It does
not judge prose quality and does not prove that a language model followed
PROTOCOL.md; it proves that a store does or does not have the required shape.

The shipped cases in semantic.json are a self-test: cases labelled "good" must
pass every rule, and each case labelled "bad" must violate exactly the named
rule. That way the grader is verified, not just run.

Rules:
  claim_limit_present          every record states what it may NOT assert (15+ chars)
  observation_no_causal        no causal wording inside an observation record
  term_has_rival_and_test      a term record names a rival and a distinguishing test
  theory_never_observed        a theory link is never graded OBSERVED
  mechanism_has_rivals_falsifier  a mechanism names >=1 rival and a falsifier
  mechanism_grounded           a mechanism is anchored in a term_id or theory_id
  observation_has_locator      an observation's artifact_site/measurement has a locator
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

CAUSE_RE = re.compile(
    r"\b(causes?|because|leads?\s+to|results?\s+in|drives?|determines?|"
    r"produces?|increases?|improves?|guarantees?|proves?|ensures?)\b|"
    r"neden|mekanizma|artırır|arttırır|sağlar|yol\s+açar|etkisidir|"
    r"sonucunda|sayesinde",
    re.I,
)
LOCATOR_REQUIRED = ("artifact_site", "source_mention", "measurement", "intervention")


def _evidence(rec):
    ev = rec.get("evidence")
    return ev if isinstance(ev, list) else []


def rule_claim_limit_present(rec):
    return len(str(rec.get("claim_limit") or "").strip()) >= 15


def rule_observation_no_causal(rec):
    if rec.get("layer") != "observation":
        return True
    if rec.get("evidence_status") == "DOCUMENTED_CLAIM":
        return True
    return not CAUSE_RE.search(str(rec.get("statement") or ""))


def rule_term_has_rival_and_test(rec):
    if rec.get("layer") != "term":
        return True
    rivals = rec.get("rival_term_ids")
    has_rival = isinstance(rivals, list) and len(rivals) >= 1
    has_test = len(str(rec.get("distinguishing_test") or "").strip()) >= 15
    return has_rival and has_test


def rule_theory_never_observed(rec):
    if rec.get("layer") != "theory":
        return True
    return rec.get("evidence_status") != "OBSERVED"


def rule_mechanism_has_rivals_falsifier(rec):
    if rec.get("layer") != "mechanism":
        return True
    mech = rec.get("mechanism") if isinstance(rec.get("mechanism"), dict) else {}
    rivals = mech.get("rivals")
    has_rivals = isinstance(rivals, list) and len(rivals) >= 1
    has_falsifier = len(str(mech.get("falsifier") or "").strip()) >= 1
    return has_rivals and has_falsifier


def rule_mechanism_grounded(rec):
    if rec.get("layer") != "mechanism":
        return True
    return bool(rec.get("term_id")) or bool(rec.get("theory_ids"))


def rule_observation_has_locator(rec):
    if rec.get("layer") != "observation":
        return True
    for ev in _evidence(rec):
        if isinstance(ev, dict) and ev.get("kind") in LOCATOR_REQUIRED:
            if not str(ev.get("locator") or "").strip():
                return False
    return True


RULES = {
    "claim_limit_present": rule_claim_limit_present,
    "observation_no_causal": rule_observation_no_causal,
    "term_has_rival_and_test": rule_term_has_rival_and_test,
    "theory_never_observed": rule_theory_never_observed,
    "mechanism_has_rivals_falsifier": rule_mechanism_has_rivals_falsifier,
    "mechanism_grounded": rule_mechanism_grounded,
    "observation_has_locator": rule_observation_has_locator,
}


def grade_store(records, rules=None):
    """Return {rule: bool} for a store. A rule passes only if every record obeys it."""
    rules = rules or list(RULES)
    out = {}
    for name in rules:
        fn = RULES[name]
        out[name] = all(fn(rec) for rec in records if isinstance(rec, dict))
    return out


def main() -> int:
    data = json.loads((HERE / "semantic.json").read_text(encoding="utf-8"))
    rows = []
    for case in data["cases"]:
        got = grade_store(case["records"], data["rules"])
        problems = []
        if case["label"] == "good":
            for rule, ok in got.items():
                if not ok:
                    problems.append(f"good store failed rule {rule}")
        else:
            named = case["violates"]
            if got.get(named, True):
                problems.append(f"bad store did not violate {named}")
        rows.append({"id": case["id"], "label": case["label"],
                     "passed": not problems, "problems": problems})

    passed = sum(1 for r in rows if r["passed"])
    print("=== SEMANTIC GRADER SELF-TEST ===")
    print(f"Cases: {len(rows)}  Passed: {passed}  Score: "
          f"{round(passed / len(rows), 4) if rows else 0.0}")
    for r in rows:
        if not r["passed"]:
            print(f"  FAIL {r['id']}: {r['problems']}")
    print("This grades the STRUCTURE of a record store, not a model's reasoning.")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
