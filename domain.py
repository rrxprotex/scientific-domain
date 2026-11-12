#!/usr/bin/env python3
"""Scientific-domain record tool: link material to canonical terms and theories.

Four layers, kept apart on purpose:
  observation  what the material shows
  term         which canonical concept it instantiates
  theory       which established theoretical frame interprets it
  mechanism    a causal proposal (rivals + falsifier + intervention)

A mechanism is NOT a default noun for a finding. Calling everything a mechanism
is the failure this tool exists to prevent.

The ontology is domain DATA, never engine code: point --ontology at another
domain file and the same validator works there. Pure Python 3.10+ stdlib, no
network, no API key. The validator refuses; it never repairs a record.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LAYERS = ("observation", "term", "theory", "mechanism")
STATUSES = (
    "OBSERVED", "CANDIDATE", "INFERRED", "HYPOTHESIS",
    "UNVERIFIED_CLAIM", "DOCUMENTED_CLAIM",
)
REPRESENTATIONS = ("PRESENT", "UNDER_IMPLEMENTED", "NOT_REPRESENTED", "UNKNOWN")
EVIDENCE_CLASSES = (
    "ARTIFACT", "SOURCE", "MEASUREMENT", "EXTERNAL_SUBJECT",
    "INTERPRETIVE", "CONVENTION", "COUNTERFACTUAL",
)
EVIDENCE_KINDS = (
    "artifact_site", "source_mention", "measurement",
    "external_subject", "interpretation", "intervention",
)
LOCATOR_REQUIRED = ("artifact_site", "source_mention", "measurement", "intervention")
SOURCE_KINDS = ("PRIMARY", "SECONDARY", "REFERENCE", "TERTIARY")
CITATION_STATUS = ("VERIFIED_BIBLIOGRAPHIC", "PARTIAL", "UNVERIFIED")
RELATION_KINDS = ("interpreted_by", "instantiates", "competes_with", "confused_with")
RELATION_STATUS = ("CANDIDATE", "CONTESTED", "SUPPORTED")
PROFILES = ("strict", "research", "lite")

CLASS_SUPPORT = {
    "ARTIFACT": ("artifact_site", "measurement"),
    "SOURCE": ("source_mention",),
    "MEASUREMENT": ("measurement",),
    "EXTERNAL_SUBJECT": ("external_subject",),
    "INTERPRETIVE": (),
    "CONVENTION": ("artifact_site", "measurement"),
    "COUNTERFACTUAL": ("intervention",),
}

CAUSE_RE = re.compile(
    r"\b(causes?|because|leads?\s+to|results?\s+in|drives?|determines?|"
    r"produces?|increases?|improves?|guarantees?|proves?|ensures?|"
    r"reduces?|decreases?|inhibits?|suppresses?|attenuates?|diminishes?|"
    r"prevents?|triggers?|mediates?)\b|"
    r"neden\s+ol|nedeniyle|nedensellik\s+göster|mekanizma|artırır|arttırır|"
    r"sağlar|yol\s+açar|etkisidir|sonucunda|sayesinde|azalt|baskılar|"
    r"baskılan|inhibe|önler|düşürür|giderir|tetikler|aracı olur",
    re.I,
)

# Stage 2a: negation immediately before the trigger ("does not increase").
# "not only" is NOT negation - "not only increases" is a causal claim.
NEGATION_BEFORE_RE = re.compile(
    r"(not(?!\s+only)|no|never|cannot|without|doesn'?t|isn'?t|aren'?t|"
    r"didn'?t|won'?t|değil|yok|olmaz|artmaz|artırmaz|azalmaz|azaltmaz|"
    r"etkilemez)\s+(?:\S+\s+){0,2}$",
    re.I,
)

# Stage 2b: a Turkish negative suffix on the trigger word or the next word
# ("nedensellik gösterilmemiştir" -> -memiş). The suffix must be followed by a
# consonant or the end of the word, so "mazeret" is not read as negation.
TR_NEGATIVE_SUFFIX_RE = re.compile(
    r"(mamış|memiş|maz|mez|madı|medi|mıyor|miyor|muyor|müyor)"
    r"(?=[^aeıioöuüAEIİOÖUÜ]|$)",
    re.I,
)


def is_causal(statement):
    """Causal wording that is NEGATED is not a causal claim.

    Stage 2 of the causality screen (stage 1 is CAUSE_RE candidate matching):
    'Repetition does not increase recall' and 'nedensellik gösterilmemiştir'
    assert no effect and must not be forced into the mechanism layer. The
    screen is deliberately conservative in the SAFE direction: a trailing
    contrastive negation ('increases recall, not the melody') does not defuse,
    so a causal claim can never hide behind one; 'not only increases' is a
    causal claim, not a negation. Hedged modality ('may increase') is still
    causal - it is a hypothesis and belongs in a mechanism record. Negated
    claims quoted from a source belong in DOCUMENTED_CLAIM, which rule T2
    already exempts.
    """
    s = str(statement or "")
    m = CAUSE_RE.search(s)
    if not m:
        return False
    if NEGATION_BEFORE_RE.search(s[:m.start()]):
        return False
    for w in s[m.start():].split()[:2]:
        if TR_NEGATIVE_SUFFIX_RE.search(w):
            return False
    return True
STRONG_RE = re.compile(
    r"\b(always|never|proven|does not exist|certainly|must|all songs|"
    r"scientifically proven)\b|her\s+zaman|her\s+şey|kesinlikle|kanıtlanmış|yoktur|"
    r"mutlaka|asla|bilimsel olarak kanıt",
    re.I,
)
MECHANISM_RE = re.compile(r"\bmechanism(s)?\b|mekanizma", re.I)
SECRET_RE = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
)
VERDICT_KEYS = ("verdict", "passed", "result", "conclusion", "verified", "score", "grade")

GENERIC_ONTOLOGY = "ontology.generic.json"
SELECTION_FILE = "domain.config.json"
DEFAULT_INDEX = Path(__file__).with_name("ontology.index.json")
DEFAULT_FILE = Path("records.jsonl")
GENERIC_DOMAIN = "generic"

# Profile-aware minimum lengths. strict is the default and matches the
# original gate behaviour exactly; research/lite are opt-in and only relax
# field-length minimums. No gate that protects the epistemic ladder is softened.
PROFILE_MIN_LENGTHS = {
    "strict": 15,
    "research": 8,
    "lite": 3,
}


def _minlen(profile):
    return PROFILE_MIN_LENGTHS.get(profile, PROFILE_MIN_LENGTHS["strict"])


# --- ontology registry and routing --------------------------------------------

def load_index():
    """Domain data: domain name -> file + routing keywords. No engine words here."""
    if not DEFAULT_INDEX.is_file():
        return {"ontologies": {}, "generic": GENERIC_DOMAIN}
    return json.loads(DEFAULT_INDEX.read_text(encoding="utf-8"))


def load_selection():
    """The user's confirmed domain choice, if any. Only `use` writes it; routing never does."""
    path = Path.cwd() / SELECTION_FILE
    if not path.is_file():
        return None
    try:
        sel = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value = str(sel.get("ontology") or sel.get("domain") or "").strip()
    return value or None


def effective_ontology(explicit):
    """Explicit --ontology > user-confirmed domain.config.json > generic fallback.

    There is NO shipped default domain. Until the user confirms a domain, the
    vocabulary-free generic ontology applies and every term/theory/mechanism
    link is refused (T9) instead of guessed.
    """
    return str(explicit) if explicit else (load_selection() or GENERIC_ONTOLOGY)


def resolve_ontology_path(value):
    """Accept a file path or a registered domain name. Reference packs live in examples/."""
    p = Path(str(value))
    if p.is_file():
        return p
    pkg = Path(__file__).resolve().parent
    for candidate in (pkg / str(value), pkg / p.name):
        if candidate.is_file():
            return candidate
    entry = load_index().get("ontologies", {}).get(str(value))
    if not entry:
        raise ValueError(f"unknown ontology '{value}'. Registered: "
                         f"{sorted(load_index().get('ontologies', {}))}")
    resolved = pkg / entry["file"]
    if not resolved.is_file():
        raise ValueError(f"ontology file missing for '{value}': {entry['file']}")
    return resolved


def route_text(text):
    """Heuristic domain nomination. NO_MATCH/ABSTAIN are honest states, not failures."""
    idx = load_index()
    ontologies = idx.get("ontologies", {})
    low = str(text or "").lower()
    generic_file = ontologies.get(GENERIC_DOMAIN, {}).get("file", "ontology.generic.json")
    hits = {}
    for domain, entry in ontologies.items():
        if domain == GENERIC_DOMAIN:
            continue
        matched = [kw for kw in entry.get("keywords", []) if kw.lower() in low]
        if matched:
            hits[domain] = matched
    if not hits:
        return {
            "status": "NO_MATCH", "domain": GENERIC_DOMAIN, "ontology": generic_file,
            "matched_keywords": [], "candidates": [], "user_confirmation_required": True,
            "reason": "no registered domain vocabulary matched the text",
            "claim_limit": "No domain vocabulary matched. Use observation-only records; do not invent canonical terms.",
        }
    best = max(len(v) for v in hits.values())
    tied = sorted(d for d, v in hits.items() if len(v) == best)
    if len(tied) > 1:
        return {
            "status": "ABSTAIN", "domain": GENERIC_DOMAIN, "ontology": generic_file,
            "matched_keywords": [], "candidates": tied, "user_confirmation_required": True,
            "reason": f"ambiguous domain signal across {tied}; a human or a sourced ontology must choose",
            "claim_limit": "Routing abstained. Do not guess a domain to make a link possible.",
        }
    chosen = tied[0]
    return {
        "status": "MATCHED", "domain": chosen,
        "ontology": ontologies[chosen]["file"],
        "matched_keywords": hits[chosen], "candidates": [chosen],
        "user_confirmation_required": True,
        "reason": f"matched domain keywords: {', '.join(hits[chosen])}",
        "claim_limit": "Routing is a heuristic proposal, never a verdict. The user confirms "
                       "the domain (`python domain.py use --ontology ...`); until then only "
                       "the generic vocabulary applies.",
    }


def load_ontology(path):
    p = resolve_ontology_path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def _check_sources(entry_id, entry, problems, allow_unverified_empty_locator=True):
    sources = entry.get("sources")
    if not isinstance(sources, list) or not sources:
        problems.append(f"{entry_id}: 'sources' must be a non-empty list")
        return
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            problems.append(f"{entry_id}: sources[{i}] is not an object")
            continue
        for key in ("ref", "kind", "citation_status", "access_note"):
            if not str(src.get(key) or "").strip():
                problems.append(f"{entry_id}: sources[{i}].{key} is required")
        if src.get("kind") not in SOURCE_KINDS:
            problems.append(f"{entry_id}: sources[{i}].kind must be one of {SOURCE_KINDS}")
        if src.get("citation_status") not in CITATION_STATUS:
            problems.append(f"{entry_id}: sources[{i}].citation_status must be one of {CITATION_STATUS}")
        locator = str(src.get("locator") or "").strip()
        if not locator:
            allowed = allow_unverified_empty_locator and src.get("citation_status") == "UNVERIFIED"
            if not allowed:
                problems.append(f"{entry_id}: sources[{i}].locator is required")


def check_ontology(onto):
    """Validate the ontology itself. A bad vocabulary cannot ground anything."""
    if not isinstance(onto, dict):
        return ["ontology is not a JSON object"]
    problems = []
    for key in ("domain", "version", "verification_policy", "terms", "theories", "relations"):
        if key not in onto:
            problems.append(f"ontology: '{key}' is required")
    terms = onto.get("terms")
    theories = onto.get("theories")
    if not isinstance(terms, dict) or not isinstance(theories, dict):
        return problems + ["ontology: 'terms' and 'theories' must be objects"]
    all_ids = set(terms) | set(theories)

    for section, entries, text_key in (("terms", terms, "definition"),
                                      ("theories", theories, "statement")):
        for eid, entry in entries.items():
            if not isinstance(entry, dict):
                problems.append(f"{section}.{eid}: entry is not an object")
                continue
            for key in ("label", text_key, "evidence_class", "claim_limit"):
                if not str(entry.get(key) or "").strip():
                    problems.append(f"{section}.{eid}: '{key}' is required")
            if entry.get("evidence_class") not in EVIDENCE_CLASSES:
                problems.append(f"{section}.{eid}: invalid evidence_class")
            _check_sources(f"{section}.{eid}", entry, problems)
            if section == "terms":
                rivals = entry.get("rival_terms", [])
                if not isinstance(rivals, list):
                    problems.append(f"terms.{eid}: rival_terms must be a list")
                else:
                    for rival in rivals:
                        if rival not in terms:
                            problems.append(f"terms.{eid}: rival '{rival}' is not a declared term")
                if not str(entry.get("distinguishing_test") or "").strip():
                    problems.append(f"terms.{eid}: distinguishing_test is required")
            else:
                for key in ("explains", "does_not_explain"):
                    if not isinstance(entry.get(key), list) or not entry[key]:
                        problems.append(f"theories.{eid}: '{key}' must be a non-empty list")

    relations = onto.get("relations", [])
    if not isinstance(relations, list):
        problems.append("ontology: relations must be a list")
    else:
        for i, rel in enumerate(relations):
            if not isinstance(rel, dict):
                problems.append(f"relations[{i}]: not an object")
                continue
            for end in ("from", "to"):
                if rel.get(end) not in all_ids:
                    problems.append(f"relations[{i}]: '{end}' references an undeclared id: {rel.get(end)}")
            if rel.get("relation") not in RELATION_KINDS:
                problems.append(f"relations[{i}]: invalid relation kind")
            if rel.get("status") not in RELATION_STATUS:
                problems.append(f"relations[{i}]: invalid relation status")
    return problems


def max_citation_status(theory):
    statuses = [s.get("citation_status") for s in theory.get("sources", [])
                if isinstance(s, dict)]
    if "VERIFIED_BIBLIOGRAPHIC" in statuses:
        return "VERIFIED_BIBLIOGRAPHIC"
    if "PARTIAL" in statuses:
        return "PARTIAL"
    return "UNVERIFIED"


# --- records ------------------------------------------------------------------

def _kinds(evidence):
    return [e.get("kind") for e in evidence if isinstance(e, dict)]


def validate(rec, onto, profile="strict"):
    """Return problems. Empty means the record may be stored.

    `profile` is one of "strict" (default), "research" or "lite". Profiles only
    relax field-length minimums (distinguishing test, theory link note); no
    gate that protects the epistemic ladder (T1, T5, T6, T7, T8, T9) is softened.
    """
    if not isinstance(rec, dict):
        return ["record is not a JSON object"]
    rid = str(rec.get("id") or "<no id>")
    problems = []

    for key in ("id", "layer", "statement", "domain", "evidence_class",
                "representation", "evidence_status", "claim_limit"):
        if not str(rec.get(key) or "").strip():
            problems.append(f"{rid}: '{key}' is required (G0)")
    for key in ("scope", "evidence"):
        if key not in rec:
            problems.append(f"{rid}: '{key}' is required (G0)")
    if problems:
        return problems

    layer, cls = rec["layer"], rec["evidence_class"]
    rep, status = rec["representation"], rec["evidence_status"]
    statement = str(rec["statement"])
    minlen = _minlen(profile)

    for key, allowed in (("layer", LAYERS), ("evidence_class", EVIDENCE_CLASSES),
                         ("representation", REPRESENTATIONS), ("evidence_status", STATUSES)):
        if rec[key] not in allowed:
            problems.append(f"{rid}: {key} must be one of {allowed} (G1)")
    if problems:
        return problems

    # G2 - every record names the material and its scope.
    scope = rec["scope"]
    if not isinstance(scope, dict):
        problems.append(f"{rid}: scope must be an object (G2)")
    else:
        sources = scope.get("sources")
        if not isinstance(sources, list) or not sources:
            problems.append(f"{rid}: scope.sources must name the inspected material (G2)")
        if rep == "NOT_REPRESENTED" and scope.get("declared") is not True:
            problems.append(f"{rid}: absence needs scope.declared=true (G3)")

    # G4 - claim limit is a sentence, not a checkbox.
    if len(str(rec["claim_limit"]).strip()) < 15:
        problems.append(f"{rid}: claim_limit must state what this record may NOT assert (G4)")

    # G10 - never persist a credential-shaped string.
    if SECRET_RE.search(json.dumps(rec, ensure_ascii=False)):
        problems.append(f"{rid}: credential-shaped string refused (G10)")

    # G11 - records must use the ontology of the domain they name.
    # The vocabulary-free generic fallback is the one exception: it accepts any
    # domain label because it deliberately owns no domain words at all.
    generic = bool(onto and onto.get("allow_term_links") is False)
    if onto and not generic and str(rec["domain"]) != str(onto.get("domain")):
        problems.append(f"{rid}: domain '{rec['domain']}' does not match loaded ontology "
                        f"'{onto.get('domain')}' - load the right --ontology (G11)")

    evidence = rec["evidence"]
    if not isinstance(evidence, list):
        problems.append(f"{rid}: evidence must be a list (G5)")
        evidence = []
    for i, ev in enumerate(evidence):
        if not isinstance(ev, dict):
            problems.append(f"{rid}: evidence[{i}] is not an object (G5)")
            continue
        if ev.get("kind") not in EVIDENCE_KINDS:
            problems.append(f"{rid}: evidence[{i}].kind must be one of {EVIDENCE_KINDS} (G5)")
        if not str(ev.get("ref") or "").strip():
            problems.append(f"{rid}: evidence[{i}].ref is required (G5)")
        if ev.get("kind") in LOCATOR_REQUIRED and not str(ev.get("locator") or "").strip():
            problems.append(f"{rid}: evidence[{i}].locator is required (G5)")

    kinds = _kinds(evidence)

    # G6 - OBSERVED is earned only by evidence the class admits.
    supported = CLASS_SUPPORT.get(cls, ())
    if status == "OBSERVED":
        if not supported:
            problems.append(f"{rid}: {cls} can never be OBSERVED - a reading is capped "
                            f"at INFERRED (G6)")
        elif not any(k in supported for k in kinds):
            problems.append(f"{rid}: OBSERVED needs evidence of kind {supported}; "
                            f"got {kinds or 'none'} (G6)")
        if cls == "CONVENTION":
            refs = {e.get("ref") for e in evidence if isinstance(e, dict)}
            if len(refs) < 2:
                problems.append(f"{rid}: CONVENTION needs >=2 independent refs (G6b)")

    # G7 - PRESENT means measured at a site.
    if rep == "PRESENT" and not any(k in ("artifact_site", "measurement") for k in kinds):
        problems.append(f"{rid}: PRESENT needs an artifact_site/measurement; "
                        f"prose-only is capped at UNDER_IMPLEMENTED (G7)")

    if status == "DOCUMENTED_CLAIM":
        if "source_mention" not in kinds:
            problems.append(f"{rid}: DOCUMENTED_CLAIM needs a source_mention (G8)")
        if rep == "PRESENT":
            problems.append(f"{rid}: a source statement is not a measured site (G8)")
    if status == "UNVERIFIED_CLAIM" and not str(rec.get("uncertainty_reason") or "").strip():
        problems.append(f"{rid}: UNVERIFIED_CLAIM needs uncertainty_reason (G9)")
    if status == "CANDIDATE":
        found = [k for k in VERDICT_KEYS if k in rec]
        if found:
            problems.append(f"{rid}: CANDIDATE carries verdict key(s) {found} (G9)")

    terms = onto.get("terms", {}) if onto else {}
    theories = onto.get("theories", {}) if onto else {}
    term_id = rec.get("term_id")
    theory_ids = rec.get("theory_ids", [])
    mech = rec.get("mechanism", {})

    if not isinstance(theory_ids, list):
        problems.append(f"{rid}: theory_ids must be a list")
        theory_ids = []
    if not isinstance(mech, dict):
        problems.append(f"{rid}: mechanism must be an object")
        mech = {}

    # No invented vocabulary.
    if term_id and onto and term_id not in terms:
        problems.append(f"{rid}: term_id '{term_id}' is not a canonical term (T1)")
    if term_id and str(rec.get("term_label") or "").strip():
        if rec["term_label"] != terms.get(term_id, {}).get("label"):
            problems.append(f"{rid}: term_label does not match the canonical label (T1)")
    for tid in theory_ids:
        if onto and tid not in theories:
            problems.append(f"{rid}: theory_id '{tid}' is not a declared theory (T1)")

    # T9 - a vocabulary-free ontology must not be used to invent terminology.
    if generic and layer in ("term", "theory", "mechanism"):
        problems.append(f"{rid}: no sourced vocabulary for this domain; only "
                        f"layer=observation is allowed - add an ontology before linking (T9)")

    causal = is_causal(statement)

    if layer == "observation":
        # T2 - a pure observation may not smuggle an interpretation.
        if term_id or theory_ids or mech:
            problems.append(f"{rid}: observation layer must not carry term/theory/mechanism "
                            f"links - use a separate record (T2)")
        if causal and status != "DOCUMENTED_CLAIM":
            problems.append(f"{rid}: causal wording requires layer=mechanism (T2)")

    elif layer == "term":
        if onto and not term_id:
            problems.append(f"{rid}: term layer requires a canonical term_id (T3)")
        if onto and term_id in terms:
            want = terms[term_id].get("evidence_class")
            if want and cls != want:
                problems.append(f"{rid}: term '{term_id}' is {want}, record says {cls} (T3)")
            declared_rivals = terms[term_id].get("rival_terms", [])
            rivals = rec.get("rival_term_ids", [])
            if not isinstance(rivals, list):
                problems.append(f"{rid}: rival_term_ids must be a list (T4)")
                rivals = []
            for rival in rivals:
                if rival not in terms:
                    problems.append(f"{rid}: rival '{rival}' is not a declared term (T4)")
            if declared_rivals and not set(rivals) & set(declared_rivals):
                problems.append(f"{rid}: name at least one declared rival of '{term_id}' "
                                f"({declared_rivals}) (T4)")
        if len(str(rec.get("distinguishing_test") or "").strip()) < minlen:
            problems.append(f"{rid}: a term link needs a distinguishing test (T4)")
        if theory_ids or mech:
            problems.append(f"{rid}: term layer may not carry theory/mechanism links (T2)")
        if causal and status != "DOCUMENTED_CLAIM":
            problems.append(f"{rid}: causal wording requires layer=mechanism (T2)")

    elif layer == "theory":
        # T5 - a theory interprets; it is never observed.
        if not theory_ids:
            problems.append(f"{rid}: theory layer requires >=1 theory_id (T5)")
        if status == "OBSERVED":
            problems.append(f"{rid}: a theory link can never be OBSERVED - it interprets (T5)")
        if len(str(rec.get("theory_link_note") or "").strip()) < minlen:
            problems.append(f"{rid}: state what the theory explains HERE (T5)")
        if onto:
            for tid in theory_ids:
                if tid in theories and max_citation_status(theories[tid]) != "VERIFIED_BIBLIOGRAPHIC":
                    if status != "CANDIDATE":
                        problems.append(f"{rid}: theory '{tid}' has no VERIFIED_BIBLIOGRAPHIC "
                                        f"source; status is capped at CANDIDATE (T6)")
        if term_id and onto and term_id not in terms:
            problems.append(f"{rid}: term_id '{term_id}' is not declared (T1)")
        if mech:
            problems.append(f"{rid}: theory layer may not carry a mechanism object (T2)")

    elif layer == "mechanism":
        # T7 - the anti-"everything is a mechanism" gate.
        if not causal:
            problems.append(f"{rid}: mechanism layer requires causal wording; otherwise "
                            f"use layer=term or layer=theory (T7)")
        rivals = mech.get("rivals", [])
        if not isinstance(rivals, list) or len(rivals) < 1:
            problems.append(f"{rid}: a mechanism needs >=1 rival explanation (T7)")
        if not str(mech.get("falsifier") or "").strip():
            problems.append(f"{rid}: a mechanism needs a falsifier (T7)")
        if not theory_ids and not term_id:
            problems.append(f"{rid}: a mechanism must be grounded in a canonical term "
                            f"or theory, not a coined name (T8)")
        if status == "OBSERVED":
            if not str(mech.get("intervention") or "").strip():
                problems.append(f"{rid}: an OBSERVED mechanism must name the intervention (T7)")
            if "intervention" not in kinds:
                problems.append(f"{rid}: an OBSERVED mechanism needs an intervention evidence row (T7)")

    return problems


def check_contradictions(records):
    """Strict mode: the same statement may not carry conflicting epistemic labels."""
    problems, groups = [], {}
    for n, rec in enumerate(records, 1):
        if not isinstance(rec, dict):
            continue
        key = re.sub(r"\W+", " ", str(rec.get("statement") or "").lower()).strip()
        if key:
            groups.setdefault(key, []).append((n, rec))
    for rows in groups.values():
        if len(rows) < 2:
            continue
        labels = {(r.get("evidence_status"), r.get("representation")) for _, r in rows}
        if len(labels) > 1:
            ids = ", ".join(f"{r.get('id')}(line {n})" for n, r in rows)
            problems.append(f"CONTESTED: same statement with conflicting labels: {ids}")
    return problems


def read_records(path):
    records, problems = [], []
    p = Path(path)
    if not p.is_file():
        return records, [f"records file not found: {path}"]
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            problems.append(f"line {n}: unreadable JSON ({exc.msg}) - row cannot verify anything")
    return records, problems


def check_records(records, onto, profile="strict"):
    problems, seen = [], set()
    for n, rec in enumerate(records, 1):
        rid = rec.get("id") if isinstance(rec, dict) else None
        if rid in seen:
            problems.append(f"line {n}: duplicate id '{rid}'")
        seen.add(rid)
        problems.extend(f"line {n}: {p}" for p in validate(rec, onto, profile))
    return problems


# --- commands -----------------------------------------------------------------

def cmd_ontology_check(args) -> int:
    if args.all:
        idx = load_index()
        names = sorted(idx.get("ontologies", {}))
        if not names:
            print("ERROR: ontology.index.json registers no ontologies")
            return 1
        problems = []
        for name in names:
            try:
                onto = load_ontology(name)
            except (ValueError, json.JSONDecodeError) as exc:
                problems.append(f"{name}: {exc}")
                continue
            for p in check_ontology(onto):
                problems.append(f"{name}: {p}")
            print(f"  {name:20s} {len(onto['terms']):2d} terms, "
                  f"{len(onto['theories']):2d} theories, "
                  f"{len(onto.get('relations', []))} relations")
        if problems:
            print(f"ERROR: {len(problems)} problem(s) across {len(names)} ontologies:")
            for p in problems:
                print(f"  - {p}")
            return 1
        print(f"OK {len(names)} registered ontologies validate")
        return 0
    try:
        onto = load_ontology(effective_ontology(args.ontology))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    problems = check_ontology(onto)
    if problems:
        print(f"ERROR: ontology has {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK ontology '{onto['domain']}' v{onto['version']}: "
          f"{len(onto['terms'])} terms, {len(onto['theories'])} theories, "
          f"{len(onto.get('relations', []))} relations")
    unverified = [eid for section in ("terms", "theories")
                  for eid, e in onto[section].items()
                  if max_citation_status(e) == "UNVERIFIED"]
    if unverified:
        print(f"NOTE: {len(unverified)} entr(ies) have UNVERIFIED sources and may only back "
              f"CANDIDATE links: {', '.join(unverified)}")
    return 0


def cmd_attention(args) -> int:
    """Score which expertise domain the task attends to. A proposal with evidence."""
    import attention as attention_mod
    text = sys.stdin.read() if args.stdin else (args.text or "")
    result = attention_mod.attend(text=text, directory=args.dir, store=args.file)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_route(args) -> int:
    text = sys.stdin.read() if args.stdin else (args.text or "")
    decision = route_text(text)
    if not str(text).strip():
        decision = dict(decision, status="ABSTAIN", domain=GENERIC_DOMAIN,
                        candidates=[], reason="empty task text",
                        claim_limit="No task text; routing cannot nominate a domain.")
    try:
        import attention as attention_mod
        decision["attention"] = attention_mod.attend(text=text)["attention"]
    except Exception:
        pass  # attention is an explanation overlay; routing must never break on it
    print(json.dumps(decision, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_terms(args) -> int:
    try:
        onto = load_ontology(effective_ontology(args.ontology))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    problems = check_ontology(onto)
    if problems:
        print("ERROR: refusing to list terms from an invalid ontology:")
        for p in problems[:6]:
            print(f"  - {p}")
        return 1
    print(f"# Canonical vocabulary: {onto['domain']} (v{onto['version']})\n")
    print("VERIFICATION: bibliographic records only. Full texts were not read.\n")
    for kind, title in (("terms", "Terms"), ("theories", "Theories")):
        if args.kind != "all" and args.kind != kind:
            continue
        print(f"## {title}\n")
        for eid, entry in onto[kind].items():
            if args.id and args.id != eid:
                continue
            print(f"### {eid} - {entry['label']}")
            print(f"- class: {entry['evidence_class']}")
            print(f"- {entry.get('definition') or entry.get('statement')}")
            if kind == "terms":
                print(f"- rivals: {', '.join(entry.get('rival_terms', [])) or '(none declared)'}")
                print(f"- distinguishing test: {entry['distinguishing_test']}")
            else:
                print(f"- explains: {'; '.join(entry['explains'])}")
                print(f"- does NOT explain: {'; '.join(entry['does_not_explain'])}")
            print(f"- sources ({max_citation_status(entry)}):")
            for src in entry["sources"]:
                print(f"    - [{src['kind']}/{src['citation_status']}] {src['ref']}")
                print(f"      locator: {src['locator'] or '(none)'}")
                print(f"      access: {src['access_note']}")
            print(f"- claim limit: {entry['claim_limit']}\n")
    return 0


def cmd_add(args) -> int:
    raw = args.json
    if raw.startswith("@"):
        try:
            raw = Path(raw[1:]).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: cannot read record file: {exc}")
            return 2
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: record is not valid JSON: {exc.msg}")
        return 2
    try:
        onto = load_ontology(effective_ontology(args.ontology))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    onto_problems = check_ontology(onto)
    if onto_problems:
        print("ERROR: ontology does not validate; refusing to write:")
        for p in onto_problems[:6]:
            print(f"  - {p}")
        return 2
    problems = validate(rec, onto, getattr(args, "profile", "strict"))
    if problems:
        print("ERROR: record refused (nothing was written):")
        for p in problems:
            print(f"  - {p}")
        return 2
    path = Path(args.file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"OK {rec['id']} [{rec['layer']}] -> {path}")
    return 0


def cmd_check(args) -> int:
    try:
        onto = load_ontology(effective_ontology(args.ontology))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    records, problems = read_records(Path(args.file))
    problems.extend(check_ontology(onto))
    problems.extend(check_records(records, onto, getattr(args, "profile", "strict")))
    if args.strict:
        problems.extend(check_contradictions(records))
    if problems:
        print(f"ERROR: {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK {len(records)} record(s) validate against '{onto['domain']}' v{onto['version']}")
    return 0


def cmd_audit(args) -> int:
    """Post-hoc nominations over free-text notes. Never findings, never verdicts."""
    notes = Path(args.notes)
    if not notes.is_file():
        print(f"ERROR: notes file not found: {notes}")
        return 2
    try:
        onto = load_ontology(effective_ontology(args.ontology))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    records, _ = read_records(Path(args.file))
    ids = {str(r.get("id")) for r in records if isinstance(r, dict) and r.get("id")}
    has_mechanism_record = any(isinstance(r, dict) and r.get("layer") == "mechanism"
                               for r in records)
    text = notes.read_text(encoding="utf-8")
    labels = [e["label"] for section in ("terms", "theories") for e in onto[section].values()]
    found = [label for label in labels if label.lower() in text.lower()]

    print("# Audit nominations (CANDIDATE)\n")
    print("Lexical nominations only. A strong word is not a finding; a missing term is "
          "a coverage fact, not a correction.\n")
    count = 0
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//", "|", ">")):
            continue
        if STRONG_RE.search(stripped) and not any(rid in stripped for rid in ids):
            print(f"- L{n}: {stripped[:200]}")
            print("  nomination: unscoped universal claim; match to a scoped record first")
            count += 1
    if found:
        print(f"\nCanonical labels appearing in notes: {', '.join(found)}")
    else:
        print("\n- COVERAGE: no canonical term or theory label appears in these notes. "
              "The notes are ungrounded in the domain vocabulary; this is a coverage "
              "statement, not a finding.")
        count += 1
    if MECHANISM_RE.search(text) and not has_mechanism_record:
        print("- COVERAGE: the notes use the word 'mechanism/mekanizma' but no "
              "mechanism-layer record exists; a mechanism needs rivals and a falsifier.")
        count += 1
    print(f"\nNominations: {count}. Zero nominations is not a clean bill of health.")
    return 0


def cmd_brief(args) -> int:
    try:
        onto = load_ontology(effective_ontology(args.ontology))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    records, problems = read_records(Path(args.file))
    problems.extend(check_ontology(onto))
    problems.extend(check_records(records, onto))
    if problems:
        print("ERROR: brief refused - the store does not validate:")
        for p in problems:
            print(f"  - {p}")
        return 1

    buckets = {layer: [] for layer in LAYERS}
    for rec in records:
        buckets[rec["layer"]].append(rec)
    titles = {
        "observation": "Observations",
        "term": "Canonical terms",
        "theory": "Theoretical frames",
        "mechanism": "Mechanism hypotheses",
    }
    lines = []
    lines.append(f"# Scientific brief - {onto['domain']}\n")
    lines.append(f"Ontology v{onto['version']} | {len(records)} records | "
                 f"bibliographic verification only; full texts were not read.\n")

    if getattr(args, "layered", False):
        needs_work = [r for r in records
                      if r.get("representation") in ("UNDER_IMPLEMENTED", "UNKNOWN")
                      and r.get("evidence_status") in ("CANDIDATE", "UNVERIFIED_CLAIM")]
        lines.append(f"## Needs work ({len(needs_work)})\n")
        for rec in needs_work:
            lines.append(f"- **{rec['id']}** [{rec['evidence_status']} / "
                         f"{rec['representation']}] {rec['statement']}")
        needs_ids = {r["id"] for r in needs_work}
        approved = [r for r in records if r["id"] not in needs_ids]
        lines.append(f"\n## Approved ({len(approved)})\n")
        for rec in approved:
            lines.append(f"- **{rec['id']}** [{rec['evidence_status']} / "
                         f"{rec['representation']}] {rec['statement']}")

    for layer, title in titles.items():
        lines.append(f"\n## {title} ({len(buckets[layer])})\n")
        for rec in buckets[layer]:
            status = rec["evidence_status"]
            lines.append(f"- **{rec['id']}** [{status} / {rec['representation']} / {rec['evidence_class']}] "
                         f"{rec['statement']}")
            if layer == "term":
                term = onto["terms"][rec["term_id"]]
                lines.append(f"  - term: {term['label']} ({rec['term_id']})")
                lines.append(f"  - rivals: {', '.join(rec.get('rival_term_ids', [])) or '(none stated)'}")
                lines.append(f"  - distinguishing test: {rec['distinguishing_test']}")
            elif layer == "theory":
                for tid in rec["theory_ids"]:
                    theory = onto["theories"][tid]
                    lines.append(f"  - theory: {theory['label']} [{max_citation_status(theory)}] ({tid})")
                    for src in theory["sources"]:
                        lines.append(f"      source: {src['ref']} | locator: {src['locator'] or '(none)'}")
                lines.append(f"  - what it explains here: {rec['theory_link_note']}")
            elif layer == "mechanism":
                lines.append(f"  - rivals: {'; '.join(rec['mechanism']['rivals'])}")
                lines.append(f"  - falsifier: {rec['mechanism']['falsifier']}")
                if rec["mechanism"].get("intervention"):
                    lines.append(f"  - intervention: {rec['mechanism']['intervention']}")
            lines.append(f"  - scope: {', '.join(rec['scope']['sources'])}")
            lines.append(f"  - claim limit: {rec['claim_limit']}\n")

    # Coverage summary only. Every record was already printed in its layer
    # section above; repeating the same statement here would look like a second
    # finding and would double-count what is actually one record.
    unknown = [r for r in records if r["representation"] in ("UNKNOWN", "NOT_REPRESENTED")]
    lines.append(f"## Coverage: unknown / absent under scope ({len(unknown)})\n")
    if unknown:
        ids = ", ".join(f"{r['id']} [{r['representation']}]" for r in unknown)
        lines.append(f"Listed above with their claim limits: {ids}.")
    else:
        lines.append("(none recorded)")
    lines.append("\nA zero-finding section is a coverage statement, not success. Every link above "
                 "is CANDIDATE/INFERRED/HYPOTHESIS unless its own evidence says otherwise.")
    output = "\n".join(lines)
    if getattr(args, "render", None):
        out_path = Path(args.render)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
        print(f"OK brief written to {out_path}")
    else:
        print(output)
    return 0


def cmd_schema(args) -> int:
    """Emit the record schema as JSON Schema for external tooling."""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "scientific-domain record",
        "type": "object",
        "required": ["id", "layer", "statement", "domain", "scope", "evidence",
                     "evidence_class", "representation", "evidence_status", "claim_limit"],
        "properties": {
            "id": {"type": "string", "pattern": "^[A-Z]+-[0-9]+$"},
            "layer": {"enum": list(LAYERS)},
            "statement": {"type": "string", "minLength": 1},
            "domain": {"type": "string"},
            "scope": {
                "type": "object",
                "required": ["sources"],
                "properties": {
                    "declared": {"type": "boolean"},
                    "sources": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                },
            },
            "evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["kind", "ref"],
                    "properties": {
                        "kind": {"enum": list(EVIDENCE_KINDS)},
                        "ref": {"type": "string"},
                        "locator": {"type": "string"},
                    },
                },
            },
            "evidence_class": {"enum": list(EVIDENCE_CLASSES)},
            "representation": {"enum": list(REPRESENTATIONS)},
            "evidence_status": {"enum": list(STATUSES)},
            "term_id": {"type": ["string", "null"]},
            "term_label": {"type": "string"},
            "rival_term_ids": {"type": "array", "items": {"type": "string"}},
            "distinguishing_test": {"type": "string"},
            "theory_ids": {"type": "array", "items": {"type": "string"}},
            "theory_link_note": {"type": "string"},
            "mechanism": {
                "type": "object",
                "properties": {
                    "rivals": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "falsifier": {"type": "string"},
                    "intervention": {"type": "string"},
                },
            },
            "claim_limit": {"type": "string", "minLength": 15},
        },
        "allOf": [
            {"if": {"properties": {"layer": {"const": "term"}}},
             "then": {"required": ["term_id", "rival_term_ids", "distinguishing_test"]}},
            {"if": {"properties": {"layer": {"const": "theory"}}},
             "then": {"required": ["theory_ids", "theory_link_note"]}},
            {"if": {"properties": {"layer": {"const": "mechanism"}}},
             "then": {"required": ["mechanism"]}},
        ],
    }
    print(json.dumps(schema, ensure_ascii=False, indent=2))
    return 0


def cmd_use(args) -> int:
    """Record the user's explicit domain choice. This is the consent step.

    `route` only proposes. Nothing moves off the vocabulary-free generic
    default until a human confirms a domain here; `--ontology` still overrides.
    """
    target = str(getattr(args, "ontology", "") or "").strip()
    if not target:
        print("ERROR: name the domain to confirm, e.g. "
              "`python domain.py use --ontology songwriting` (or your own ontology file)")
        return 2
    try:
        onto = load_ontology(target)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    problems = check_ontology(onto)
    if problems:
        print("ERROR: ontology does not validate; refusing to confirm it:")
        for p in problems[:6]:
            print(f"  - {p}")
        return 2
    selection = {
        "domain": onto["domain"],
        "ontology": target,
        "confirmed_by": "user",
        "confirmed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (Path.cwd() / SELECTION_FILE).write_text(
        json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK domain '{onto['domain']}' confirmed -> {SELECTION_FILE}")
    print("This choice was made by a human, not guessed by routing. It applies to "
          "add/check/audit/brief in this directory.")
    return 0


def _utf8_stdio():
    """Deterministic UTF-8 output on every platform.

    On Windows a piped child writes locale-encoded bytes (cp1254/cp1252) while
    readers expect UTF-8, so Turkish/Spanish characters crash the pipe. The
    tool's output encoding must not depend on the host locale.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv=None) -> int:
    _utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ontology", default=None,
                        help="domain vocabulary: a registered name or a file path "
                             "(default: your confirmed domain.config.json, else generic)")
    parser.add_argument("--profile", choices=PROFILES, default="strict",
                        help="rigor profile: strict (default), research or lite - "
                             "relaxes field-length minimums only, never the epistemic gates")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ontology-check", help="validate one or all domain vocabularies")
    p.add_argument("--all", action="store_true", help="validate every ontology in ontology.index.json")
    p.set_defaults(func=cmd_ontology_check)

    p = sub.add_parser("route", help="nominate a domain vocabulary for a task (heuristic, never a verdict)")
    p.add_argument("--text", help="task text to route")
    p.add_argument("--stdin", action="store_true", help="read task text from stdin")
    p.set_defaults(func=cmd_route)

    p = sub.add_parser("terms", help="list canonical terms and theories with their sources")
    p.add_argument("--kind", choices=("all", "terms", "theories"), default="all")
    p.add_argument("--id", help="show only this term/theory id")
    p.set_defaults(func=cmd_terms)

    p = sub.add_parser("add", help="validate then append one record (production mode)")
    p.add_argument("--json", required=True, help="inline JSON or @path to a JSON file")
    p.add_argument("--file", default=str(DEFAULT_FILE))
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("check", help="re-validate a records corpus (post-hoc)")
    p.add_argument("--file", default=str(DEFAULT_FILE))
    p.add_argument("--strict", action="store_true", help="also detect contradictory labels for the same statement")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("audit", help="nominate ungrounded notes (post-hoc)")
    p.add_argument("--notes", required=True)
    p.add_argument("--file", default=str(DEFAULT_FILE))
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("brief", help="render the scientific-format brief")
    p.add_argument("--file", default=str(DEFAULT_FILE))
    p.add_argument("--layered", action="store_true",
                   help="two-pass report: records needing work first, then approved")
    p.add_argument("--render", help="write the brief to this file instead of stdout")
    p.set_defaults(func=cmd_brief)

    p = sub.add_parser("attention", help="score which expertise domain the task attends to "
                                        "(deterministic weights, evidence, never a verdict)")
    p.add_argument("--text", help="task text")
    p.add_argument("--stdin", action="store_true", help="read task text from stdin")
    p.add_argument("--dir", help="working directory: FILE NAMES are material-type evidence "
                                "(contents are never read)")
    p.add_argument("--file", default=str(DEFAULT_FILE),
                   help="record store for continuity evidence (default: records.jsonl)")
    p.set_defaults(func=cmd_attention)

    p = sub.add_parser("use", help="confirm the expertise domain explicitly (the consent step)")
    p.set_defaults(func=cmd_use)

    p = sub.add_parser("schema", help="emit the record schema as JSON Schema for external tooling")
    p.set_defaults(func=cmd_schema)

    # Accept --ontology and --profile both before and after the subcommand, without
    # the subparser's default overwriting the parent parser's value.
    for sp in sub.choices.values():
        sp.add_argument("--ontology", dest="ontology", default=argparse.SUPPRESS,
                        help="domain vocabulary (default: confirmed domain.config.json, else generic)")
        sp.add_argument("--profile", dest="profile", choices=PROFILES,
                        default=argparse.SUPPRESS,
                        help="strict (default), research or lite")

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
