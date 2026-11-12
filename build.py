#!/usr/bin/env python3
"""Layer-first record builders for the scientific-domain engine.

These helpers construct canonical records with the correct layer defaults
(evidence_status / representation / evidence_class per layer) and refuse to
return a record that would fail `domain.validate()` for structural reasons
(missing scope, missing claim_limit, missing locator). They never invent
content: statement, claim_limit, evidence and links are always caller-supplied.

Usage:

    from build import observation, term, theory, mechanism

    rec = observation(
        rid="LNK-001",
        statement="The chorus repeats the same line three times.",
        domain_name="songwriting",
        scope={"declared": True, "sources": ["ornek.cho"]},
        evidence=[{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L10-L14"}],
        claim_limit="Only this file's repetition count; nothing about listener recall.",
    )

Every builder raises ValueError listing the structural problems when required
input is missing; it never fills in a placeholder that would silently pass a
gate. Callers may pass **overrides to customize any field after the defaults.
"""
from __future__ import annotations

import json
from pathlib import Path

import domain

LOCATOR_REQUIRED = ("artifact_site", "source_mention", "measurement", "intervention")

LAYER_DEFAULTS = {
    "observation": ("OBSERVED", "PRESENT", "ARTIFACT"),
    "term": ("INFERRED", "UNDER_IMPLEMENTED", "ARTIFACT"),
    "theory": ("INFERRED", "UNDER_IMPLEMENTED", "INTERPRETIVE"),
    "mechanism": ("HYPOTHESIS", "UNKNOWN", "COUNTERFACTUAL"),
}


def _skeleton(layer: str, rid: str, statement: str, domain_name: str) -> dict:
    ep, rep, ec = LAYER_DEFAULTS[layer]
    return {
        "id": rid,
        "layer": layer,
        "statement": statement,
        "domain": domain_name,
        "scope": {"declared": False, "sources": []},
        "evidence": [],
        "evidence_class": ec,
        "representation": rep,
        "evidence_status": ep,
        "term_id": None,
        "theory_ids": [],
        "rival_term_ids": [],
        "distinguishing_test": "",
        "theory_link_note": "",
        "mechanism": {},
        "claim_limit": "",
    }


def _structural_problems(rec: dict) -> list:
    """Structural checks mirroring G0/G2/G4/G5. Content gates stay in domain.validate."""
    rid = rec.get("id") or "<no id>"
    problems = []
    for key in ("id", "statement"):
        if not str(rec.get(key) or "").strip():
            problems.append(f"{key} is required")
    scope = rec.get("scope") if isinstance(rec.get("scope"), dict) else {}
    if not scope.get("sources"):
        problems.append("scope.sources must name the inspected material")
    if len(str(rec.get("claim_limit") or "").strip()) < 15:
        problems.append("claim_limit must state what this record may NOT assert (15+ chars)")
    evidence = rec.get("evidence") if isinstance(rec.get("evidence"), list) else []
    for i, ev in enumerate(evidence):
        if not isinstance(ev, dict):
            problems.append(f"evidence[{i}] is not an object")
            continue
        if not str(ev.get("ref") or "").strip():
            problems.append(f"evidence[{i}].ref is required")
        if ev.get("kind") in LOCATOR_REQUIRED and not str(ev.get("locator") or "").strip():
            problems.append(f"evidence[{i}].locator is required for kind {ev.get('kind')}")
    return problems


def _finish(rec: dict, problems: list, overrides: dict) -> dict:
    rec.update(overrides)
    if problems:
        raise ValueError("; ".join(problems))
    return rec


def observation(rid: str, statement: str, domain_name: str = "generic",
                *, scope=None, evidence=None, claim_limit=None, **overrides) -> dict:
    """Build a canonical observation record (OBSERVED / PRESENT / ARTIFACT)."""
    rec = _skeleton("observation", rid, statement, domain_name)
    if scope is not None:
        rec["scope"] = scope
    if evidence is not None:
        rec["evidence"] = evidence
    if claim_limit is not None:
        rec["claim_limit"] = claim_limit
    problems = _structural_problems(rec)
    kinds = [e.get("kind") for e in rec["evidence"] if isinstance(e, dict)]
    if rec["representation"] == "PRESENT" and not any(
            k in ("artifact_site", "measurement") for k in kinds):
        problems.append("PRESENT needs an artifact_site/measurement evidence row "
                        "with a locator")
    return _finish(rec, problems, overrides)


def term(rid: str, statement: str, term_id: str, rival_term_ids: list,
         distinguishing_test: str, domain_name: str = "generic",
         *, scope=None, evidence=None, claim_limit=None, **overrides) -> dict:
    """Build a canonical term record (INFERRED / UNDER_IMPLEMENTED / ARTIFACT)."""
    rec = _skeleton("term", rid, statement, domain_name)
    rec["term_id"] = term_id
    rec["rival_term_ids"] = rival_term_ids
    rec["distinguishing_test"] = distinguishing_test
    if scope is not None:
        rec["scope"] = scope
    if evidence is not None:
        rec["evidence"] = evidence
    if claim_limit is not None:
        rec["claim_limit"] = claim_limit
    problems = _structural_problems(rec)
    if not term_id:
        problems.append("term_id is required (T3)")
    if not rival_term_ids:
        problems.append("at least one rival_term_id is required (T4)")
    if len(str(distinguishing_test or "").strip()) < 15:
        problems.append("a distinguishing test of 15+ chars is required (T4)")
    return _finish(rec, problems, overrides)


def theory(rid: str, statement: str, theory_ids: list, theory_link_note: str,
           domain_name: str = "generic",
           *, scope=None, evidence=None, claim_limit=None, **overrides) -> dict:
    """Build a canonical theory record (INFERRED / UNDER_IMPLEMENTED / INTERPRETIVE)."""
    rec = _skeleton("theory", rid, statement, domain_name)
    rec["theory_ids"] = theory_ids
    rec["theory_link_note"] = theory_link_note
    if scope is not None:
        rec["scope"] = scope
    if evidence is not None:
        rec["evidence"] = evidence
    if claim_limit is not None:
        rec["claim_limit"] = claim_limit
    problems = _structural_problems(rec)
    if not theory_ids:
        problems.append("at least one theory_id is required (T5)")
    if len(str(theory_link_note or "").strip()) < 15:
        problems.append("a theory_link_note of 15+ chars is required (T5)")
    if rec["evidence_status"] == "OBSERVED":
        problems.append("a theory link can never be OBSERVED (T5)")
    return _finish(rec, problems, overrides)


def mechanism(rid: str, statement: str, rivals: list, falsifier: str,
              domain_name: str = "generic",
              *, term_id=None, theory_ids=None, intervention=None,
              scope=None, evidence=None, claim_limit=None, **overrides) -> dict:
    """Build a canonical mechanism record (HYPOTHESIS / UNKNOWN / COUNTERFACTUAL)."""
    if not domain.CAUSE_RE.search(statement or ""):
        raise ValueError("mechanism statement requires causal wording "
                         "(e.g. 'increases', 'leads to', 'because', 'artırır', 'neden')")
    rec = _skeleton("mechanism", rid, statement, domain_name)
    rec["mechanism"] = {"rivals": rivals, "falsifier": falsifier}
    if intervention is not None:
        rec["mechanism"]["intervention"] = intervention
    if term_id is not None:
        rec["term_id"] = term_id
    if theory_ids is not None:
        rec["theory_ids"] = theory_ids
    if scope is not None:
        rec["scope"] = scope
    if evidence is not None:
        rec["evidence"] = evidence
    if claim_limit is not None:
        rec["claim_limit"] = claim_limit
    problems = _structural_problems(rec)
    if not rivals:
        problems.append("at least one rival explanation is required (T7)")
    if len(str(falsifier or "").strip()) < 15:
        problems.append("a falsifier of 15+ chars is required (T7)")
    if not theory_ids and not term_id:
        problems.append("a mechanism must be grounded in a term_id or theory_id (T8)")
    if rec["evidence_status"] == "OBSERVED" and not intervention:
        problems.append("an OBSERVED mechanism must name the intervention (T7)")
    return _finish(rec, problems, overrides)


def to_jsonl(records: list) -> str:
    """Serialize records (dicts) to JSONL text, sorted keys, non-ASCII preserved."""
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                   for r in records)


def append(records: list, path) -> None:
    """Append records to a JSONL file. Dicts are serialized; validation stays
    the caller's job (use domain.add or domain.validate first)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
