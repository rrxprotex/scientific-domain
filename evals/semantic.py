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
                               (negated causality is not a causal claim; the
                               screen is domain.is_causal, shared with the validator)
  term_has_rival_and_test      a term record names a rival and a distinguishing test
  theory_never_observed        a theory link is never graded OBSERVED
  mechanism_has_rivals_falsifier  a mechanism names >=1 rival and a falsifier
  mechanism_grounded           a mechanism is anchored in a term_id or theory_id
  observation_has_locator      a PRESENT/OBSERVED observation carries a located
                               artifact_site/measurement; every locator-requiring
                               evidence row has a non-empty locator
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

_spec = importlib.util.spec_from_file_location("domain", ROOT / "domain.py")
domain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(domain)

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
    return not domain.is_causal(str(rec.get("statement") or ""))


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
    """An observation is only as good as its located evidence.

    A PRESENT/OBSERVED observation must carry at least one artifact_site or
    measurement row - an evidence-free observation is not a located finding.
    Every locator-requiring evidence row must carry a non-empty locator.
    NOT_REPRESENTED / UNKNOWN observations may carry no evidence rows (absence
    under declared scope is a real result); their guard is G3 in the validator.
    """
    if rec.get("layer") != "observation":
        return True
    evidence = _evidence(rec)
    kinds = [ev.get("kind") for ev in evidence if isinstance(ev, dict)]
    if rec.get("representation") == "PRESENT" or rec.get("evidence_status") == "OBSERVED":
        if not any(k in ("artifact_site", "measurement") for k in kinds):
            return False
    for ev in evidence:
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


LAYERS = ("observation", "term", "theory", "mechanism")
RECORD_REQUIRED_FIELDS = ("id", "layer", "statement")


def record_shape_ok(rec):
    """Structural integrity of one record: parses to a dict carrying the
    expected fields with usable values.

    A dict is not enough - `isinstance(rec, dict)` accepted `{}` and a record
    missing its statement. Only a record with a non-empty id, a known layer and
    a non-empty statement is gradable; anything else is malformed.
    """
    if not isinstance(rec, dict):
        return False
    if not str(rec.get("id") or "").strip():
        return False
    if rec.get("layer") not in LAYERS:
        return False
    if not str(rec.get("statement") or "").strip():
        return False
    return True


def load_jsonl(text):
    """Parse a JSONL store. Returns (records, bad_lines) where bad_lines are
    1-based line numbers that did not parse. Unparseable lines are reported,
    never repaired or silently dropped.
    """
    records, bad_lines = [], []
    for n, line in enumerate(str(text).splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            bad_lines.append(n)
    return records, bad_lines


def grade_jsonl(text, rules=None):
    """Grade a JSONL store fail-closed: any unparseable line fails every rule.

    A store that cannot be parsed cannot be scored - returning partial grades
    over only the lines that survived would turn a parsing failure into a
    cleaner-looking score.
    """
    rules = rules or list(RULES)
    records, bad_lines = load_jsonl(text)
    out = grade_store(records, rules)
    if bad_lines:
        return {name: False for name in rules}
    return out


def grade_store(records, rules=None):
    """Return {rule: bool} for a store. A rule passes only if every record obeys it.

    An empty or malformed store FAILS every rule: `all([])` is vacuously True in
    Python, and a grader that scores an empty store as perfect would contradict
    the project rule that zero findings is a coverage statement, not success.
    Non-dict or structurally incomplete entries are never silently dropped -
    they fail the whole store (see `record_shape_ok`).
    """
    rules = rules or list(RULES)
    valid = [rec for rec in records if record_shape_ok(rec)]
    wellformed = bool(records) and len(valid) == len(records)
    out = {}
    for name in rules:
        fn = RULES[name]
        out[name] = wellformed and all(fn(rec) for rec in valid)
    return out


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
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
    graded = sum(1 for c in data["cases"] for r in c["records"]
                 if record_shape_ok(r))
    malformed = sum(len(c["records"]) for c in data["cases"]) - graded
    print("=== SEMANTIC GRADER SELF-TEST ===")
    print(f"Cases: {len(rows)}  Passed: {passed}  Score: "
          f"{round(passed / len(rows), 4) if rows else 0.0}")
    print(f"Records graded: {graded} ({malformed} malformed)")
    for r in rows:
        if not r["passed"]:
            print(f"  FAIL {r['id']}: {r['problems']}")
    print("This grades the STRUCTURE of a record store, not a model's reasoning.")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
