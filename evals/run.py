#!/usr/bin/env python3
"""Static eval runner: activation decisions + CLI contract cases.

This runner is deliberately model-free and dependency-free. It grades a
deterministic classifier and the artifacts the CLI writes. It does NOT prove
that a language model follows the SKILL.md instructions in a live session;
that requires a separate dual-arm run, reported below as NOT_RUN.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).with_name("cases.json")
RESULTS = ROOT / "eval-results.json"
DOMAIN = ROOT / "domain.py"
ACTIVATE = ROOT / "activate.py"


def run(argv, **kw):
    kw.setdefault("cwd", ROOT)
    return subprocess.run([sys.executable] + [str(a) for a in argv],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def base_record(**kw):
    rec = {
        "id": "EVAL-001",
        "layer": "observation",
        "statement": "The chorus repeats the same line three times.",
        "domain": "songwriting",
        "scope": {"declared": True, "sources": ["ornek.cho"]},
        "evidence": [{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L10-L14"}],
        "evidence_class": "ARTIFACT",
        "representation": "PRESENT",
        "evidence_status": "OBSERVED",
        "term_id": None, "theory_ids": [], "rival_term_ids": [],
        "distinguishing_test": "", "theory_link_note": "", "mechanism": {},
        "claim_limit": "Only this file's repetition count; says nothing about listener recall.",
    }
    rec.update(kw)
    return rec


def activation_cases():
    data = json.loads(CASES.read_text(encoding="utf-8"))
    rows = []
    for case in data["cases"]:
        r = run([ACTIVATE, "--text", case["prompt"]])
        problems = []
        got = {}
        if r.returncode != 0:
            problems.append(f"classifier exited {r.returncode}")
        else:
            try:
                got = json.loads(r.stdout)
            except json.JSONDecodeError as exc:
                problems.append(f"unreadable classifier output: {exc.msg}")
        if got:
            if got.get("decision") != case["expect"]:
                problems.append(f"decision {got.get('decision')} != {case['expect']}")
            if case["expect_domain"] is not None and got.get("domain") != case["expect_domain"]:
                problems.append(f"domain {got.get('domain')} != {case['expect_domain']}")
            if not got.get("claim_limit"):
                problems.append("missing claim_limit on the activation decision")
        rows.append({"id": case["id"], "kind": "activation", "prompt": case["prompt"],
                     "expected": case["expect"], "observed": got.get("decision"),
                     "domain": got.get("domain"), "passed": not problems,
                     "problems": problems})
    return rows


def contract_cases():
    rows = []

    def add_case(cid, label, result, expect_exit, expect_text=None, extra=None):
        problems = []
        if result.returncode != expect_exit:
            problems.append(f"exit {result.returncode} != {expect_exit}")
        if expect_text and expect_text not in result.stdout:
            problems.append(f"output does not contain {expect_text!r}")
        if extra:
            problems.extend(extra)
        rows.append({"id": cid, "kind": "contract", "prompt": label,
                     "expected": f"exit {expect_exit}", "observed": f"exit {result.returncode}",
                     "passed": not problems, "problems": problems})

    # Was "OK 3 registered ontologies" - exact-count pin extended for the two
    # registered worked-example domains (physics, psychology); no looser.
    add_case("CON-001", "ontology-check --all validates every registered vocabulary",
             run([DOMAIN, "ontology-check", "--all"]), 0, "OK 5 registered ontologies")
    add_case("CON-002", "check --strict on the shipped 9-record example (reference pack)",
             run([DOMAIN, "check", "--ontology", "songwriting",
                  "--file", "examples/ornek.jsonl", "--strict"]), 0, "OK 9 record(s)")
    add_case("CON-012", "check --strict on the physics worked example (14 records)",
             run([DOMAIN, "check", "--ontology", "physics",
                  "--file", "examples/physics-pendulum/records.jsonl", "--strict"]), 0,
             "OK 14 record(s)")
    add_case("CON-013", "check --strict on the psychology worked example (12 records)",
             run([DOMAIN, "check", "--ontology", "psychology",
                  "--file", "examples/psychology-stroop/records.jsonl", "--strict"]), 0,
             "OK 12 record(s)")

    r = run([DOMAIN, "route", "--text", "an unregistered expertise area with no keywords"])
    problems = []
    try:
        d = json.loads(r.stdout)
        if d.get("status") != "NO_MATCH" or d.get("domain") != "generic":
            problems.append(f"unexpected routing decision: {d.get('status')}/{d.get('domain')}")
    except json.JSONDecodeError:
        problems.append("route did not emit JSON")
    rows.append({"id": "CON-003", "kind": "contract", "prompt": "unknown domain routes to NO_MATCH/generic",
                 "expected": "NO_MATCH/generic", "observed": "see problems",
                 "passed": not problems, "problems": problems})

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "r.jsonl"
        invented = base_record(
            layer="term", term_id="TERM-INVENTED", rival_term_ids=["TERM-REFRAIN"],
            distinguishing_test="A separate section boundary is marked in the source file.",
            representation="UNDER_IMPLEMENTED", evidence_status="INFERRED")
        r = run([DOMAIN, "add", "--ontology", "songwriting",
                 "--json", json.dumps(invented), "--file", out])
        extra = ["a refused record was still written"] if out.exists() else []
        add_case("CON-004", "invented canonical term is refused before any write",
                 r, 2, "T1", extra)

        mech = base_record(
            layer="mechanism", statement="Chorus repetition increases listener recall.",
            representation="UNKNOWN", evidence_status="HYPOTHESIS",
            evidence_class="COUNTERFACTUAL", evidence=[],
            theory_ids=["THEORY-PROCESSING-FLUENCY"],
            mechanism={"rivals": ["melodic contour alone"], "falsifier": ""},
            claim_limit="Only a hypothesis; no listener data was collected in this file.")
        r = run([DOMAIN, "add", "--ontology", "songwriting",
                 "--json", json.dumps(mech), "--file", out])
        add_case("CON-005", "mechanism without a falsifier is refused", r, 2, "T7")

        generic_term = dict(invented, domain="biomedicine", layer="term", term_id=None)
        r = run([DOMAIN, "--ontology", "generic", "add", "--json",
                 json.dumps(generic_term), "--file", out])
        add_case("CON-006", "vocabulary-free generic ontology refuses a term link (T9)",
                 r, 2, "T9")

        # Consent flow: generic is the default until a human confirms a domain.
        out2 = Path(tmp) / "consent.jsonl"
        r = run([DOMAIN, "add", "--json", json.dumps(invented), "--file", out2], cwd=tmp)
        extra = ["a record was written before the domain was confirmed"] if out2.exists() else []
        add_case("CON-009", "no confirmed domain: a term link is refused by default (T9)",
                 r, 2, "T9", extra)

        r = run([DOMAIN, "use", "--ontology", "songwriting"], cwd=tmp)
        problems = [] if r.returncode == 0 else ["use did not record the choice"]
        sel = Path(tmp) / "domain.config.json"
        if not sel.exists():
            problems.append("domain.config.json was not written")
        valid_term = base_record(
            layer="term", term_id="TERM-CHORUS", rival_term_ids=["TERM-REFRAIN"],
            distinguishing_test="A separate section boundary is marked; a refrain would be a returning line inside the verse.",
            representation="UNDER_IMPLEMENTED", evidence_status="INFERRED")
        r = run([DOMAIN, "add", "--json", json.dumps(valid_term), "--file", out2], cwd=tmp)
        if r.returncode != 0:
            problems.append("add failed after the user confirmed the domain")
        if not out2.exists():
            problems.append("nothing was written after confirmation")
        rows.append({"id": "CON-010", "kind": "contract",
                     "prompt": "use records a user-confirmed domain; add then works without a flag",
                     "expected": "exit 0 after use", "observed": f"exit {r.returncode}",
                     "passed": not problems, "problems": problems})

    r = run([ACTIVATE, "--hook"], input=json.dumps({"prompt": "fix a typo in the readme"}))
    problems = [] if r.stdout.strip() == "" else ["hook was not silent on SKIP"]
    rows.append({"id": "CON-007", "kind": "contract", "prompt": "hook stays silent on SKIP",
                 "expected": "empty stdout", "observed": repr(r.stdout[:60]),
                 "passed": not problems, "problems": problems})

    r = run([ACTIVATE, "--hook"],
            input=json.dumps({"prompt": "Analyze this lyric and relate it to theory"}))
    problems = [] if "additionalContext" in r.stdout else ["hook did not inject context on ACTIVATE"]
    rows.append({"id": "CON-008", "kind": "contract", "prompt": "hook injects context on ACTIVATE",
                 "expected": "additionalContext", "observed": "see problems",
                 "passed": not problems, "problems": problems})

    r = run([DOMAIN, "attention", "--text",
             "Analyze this lyric and relate the repetition to songwriting theory"])
    problems = []
    try:
        d = json.loads(r.stdout)
        if d.get("status") != "MATCHED" or d.get("domain") != "songwriting":
            problems.append(f"attention ranked {d.get('status')}/{d.get('domain')}")
        if not d.get("user_confirmation_required"):
            problems.append("attention output must still require user confirmation")
        if "evidence" not in d or "attention" not in d:
            problems.append("attention output must carry explainable scores and evidence")
    except json.JSONDecodeError:
        problems.append("attention did not emit JSON")
    rows.append({"id": "CON-011", "kind": "contract",
                 "prompt": "attention ranks the domain with evidence but never decides",
                 "expected": "MATCHED/songwriting + user_confirmation_required",
                 "observed": "see problems", "passed": not problems, "problems": problems})
    return rows


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rows = activation_cases() + contract_cases()
    passed = sum(1 for r in rows if r["passed"])
    payload = {
        "schemaVersion": 1,
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "runner": "static, model-free, stdlib only",
        "casesTotal": len(rows),
        "casesPassed": passed,
        "score": round(passed / len(rows), 4) if rows else 0.0,
        "cases": rows,
        "liveModelDualArm": {
            "status": "NOT_RUN",
            "reason": "No live model runner or API credential is configured. Static checks validate the classifier and CLI artifacts; they do not prove that a model reads SKILL.md, activates automatically, or produces better research records.",
            "how_to_run": "Run the same prompts in two arms (skill installed / not installed), grade the resulting artifacts, and report the delta. A high static score with near-zero delta is not evidence of benefit."
        },
        "interpretation": "A score of 1.00 means these deterministic checks passed. It is not a claim about semantic reasoning quality or model adherence."
    }
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print(f"=== EVAL COMPLETE ===")
    print(f"Cases: {len(rows)}  Passed: {passed}  Score: {payload['score']}")
    for r in rows:
        if not r["passed"]:
            print(f"  FAIL {r['id']}: {r['problems']}")
    print(f"Live-model dual-arm eval: NOT_RUN")
    print(f"Results: {RESULTS}")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
