#!/usr/bin/env python3
"""Adversarial scientific evaluation: attack the validator and the classifier.

For every attack record the suite demands REFUSAL with the named gate(s); for
every control record it demands ACCEPTANCE; for every attack prompt it demands
the honest activation state. Labels in adversarial.json were written before this
runner existed.

What a pass means: the gate held against THIS attack. What it does not mean:
anything about a language model's behaviour. The live dual-arm measurement
(`dualarm.py`) is the only instrument that speaks to that question.

Stdlib only. Writes adversarial-results.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = HERE / "adversarial.json"
RESULTS = ROOT / "adversarial-results.json"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


domain = _load("domain", ROOT / "domain.py")
activate = _load("activate", ROOT / "activate.py")


def record_rows(cases):
    rows = []
    for case in cases:
        onto = domain.load_ontology(case.get("ontology", "songwriting"))
        problems = domain.validate(case["record"], onto, case.get("profile", "strict"))
        failed = []
        if case["expect"] == "refused":
            if not problems:
                failed.append("ATTACK ACCEPTED - the gate did not hold")
            for gate in case.get("expect_gates", []):
                if not any(gate in p for p in problems):
                    failed.append(f"expected gate {gate} did not fire (got: {problems[:3]})")
        else:
            if problems:
                failed.append(f"control record refused: {problems[:3]}")
        rows.append({"id": case["id"], "kind": "record", "description": case["description"],
                     "expected": case["expect"], "observed": "refused" if problems else "accepted",
                     "passed": not failed, "problems": failed})
    return rows


def prompt_rows(cases):
    rows = []
    for case in cases:
        got = activate.classify(case["prompt"])
        failed = []
        if got["decision"] != case["expect"]:
            failed.append(f"decision {got['decision']} != {case['expect']}")
        if case.get("expect_domain") is not None and got.get("domain") != case["expect_domain"]:
            failed.append(f"domain {got.get('domain')} != {case['expect_domain']}")
        rows.append({"id": case["id"], "kind": "prompt", "description": case["description"],
                     "expected": case["expect"], "observed": got["decision"],
                     "passed": not failed, "problems": failed})
    return rows


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    data = json.loads(CASES.read_text(encoding="utf-8"))
    rows = record_rows(data["record_cases"]) + prompt_rows(data["prompt_cases"])
    passed = sum(1 for r in rows if r["passed"])
    payload = {
        "schemaVersion": 1,
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "runner": "adversarial, static, model-free, stdlib only",
        "casesTotal": len(rows),
        "casesPassed": passed,
        "score": round(passed / len(rows), 4) if rows else 0.0,
        "cases": rows,
        "interpretation": "A pass means the named gate held against this attack. "
                          "It is not evidence about any language model's adherence; "
                          "see dualarm.py for the measurement that would speak to that.",
    }
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print("=== ADVERSARIAL EVAL COMPLETE ===")
    print(f"Cases: {len(rows)}  Passed: {passed}  Score: {payload['score']}")
    for r in rows:
        if not r["passed"]:
            print(f"  FAIL {r['id']}: {r['problems']}")
    print(f"Results: {RESULTS}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
