#!/usr/bin/env python3
"""Deterministic domain attention: score which expertise domain a task attends to.

This is NOT a neural attention mechanism. It is a transparent weighted scorer
over registry data (`ontology.index.json`) - no ML, no dependencies, no network.
Three signal families are weighted and summed per candidate domain:

  keywords      registry keyword hits; longer keywords weigh more (more specific)
  material      FILE NAMES in the working directory matched against per-domain
                `material_hints` (names only - file contents are never read)
  store         continuity: domains already present in the record store

Every score is explainable (the matched signals are returned as `evidence`),
every weight is a declared constant, and the whole thing is unit-testable.

The output is always a PROPOSAL. `user_confirmation_required` is always true:
the domain is only ever applied through `domain.py use` (the consent step).
Routing and attention determine what to ASK, never what is TRUE.
"""
from __future__ import annotations

import json
from fnmatch import fnmatch
from pathlib import Path

import domain as engine  # registry access only; no domain words live here

# --- declared weights (the whole model, in four constants) --------------------
KEYWORD_BASE = 1.0          # per keyword hit
KEYWORD_SPECIFICITY = 1 / 12  # + up to 1.0 for long, specific keywords
MATERIAL_WEIGHT = 2.0       # per matching file name
STORE_WEIGHT = 1.5          # per record already in the store
MATERIAL_CAP = 6.0
STORE_CAP = 4.5

TIE_MARGIN = 0.10           # attention gap below this -> ABSTAIN (a human chooses)
HIGH_MARGIN = 0.25          # gap above this -> confidence "high"

CLAIM_LIMIT = (
    "Deterministic weighted attention over registry data - not a neural model, "
    "not a verdict. The user confirms the domain (`python domain.py use "
    "--ontology ...`); until then only the generic vocabulary applies."
)


def _keyword_hits(text, ontologies, evidence):
    low = str(text or "").lower()
    scores = {}
    for dom, entry in ontologies.items():
        if dom == engine.GENERIC_DOMAIN:
            continue
        hits = [kw for kw in entry.get("keywords", []) if kw.lower() in low]
        if hits:
            scores[dom] = sum(KEYWORD_BASE + min(len(k), 12) * KEYWORD_SPECIFICITY
                              for k in hits)
            evidence.setdefault(dom, {})["keywords"] = hits
    return scores


def _material_hits(directory, ontologies, evidence):
    """Shallow listing of file NAMES as material-type evidence. Never reads contents."""
    if not directory:
        return {}
    p = Path(directory)
    if not p.is_dir():
        return {}
    names = [c.name for c in p.iterdir() if not c.name.startswith(".")]
    scores = {}
    for dom, entry in ontologies.items():
        hints = entry.get("material_hints") or []
        matched = sorted({n for n in names for h in hints if fnmatch(n, h)})
        if matched:
            scores[dom] = min(len(matched) * MATERIAL_WEIGHT, MATERIAL_CAP)
            evidence.setdefault(dom, {})["material_files"] = matched[:8]
    return scores


def _store_hits(store, ontologies, evidence):
    if not store:
        return {}
    p = Path(store)
    if not p.is_file():
        return {}
    counts = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        dom = str(rec.get("domain") or "")
        if dom in ontologies:
            counts[dom] = counts.get(dom, 0) + 1
    for dom, n in counts.items():
        evidence.setdefault(dom, {})["store_records"] = n
    return {dom: min(n * STORE_WEIGHT, STORE_CAP) for dom, n in counts.items()}


def attend(text=None, directory=None, store=None) -> dict:
    """Rank candidate expertise domains with explainable attention weights."""
    idx = engine.load_index()
    ontologies = idx.get("ontologies", {})
    evidence = {}

    kw = _keyword_hits(text, ontologies, evidence)
    mat = _material_hits(directory, ontologies, evidence)
    sto = _store_hits(store, ontologies, evidence)

    totals = {}
    for dom in set(kw) | set(mat) | set(sto):
        totals[dom] = round(kw.get(dom, 0.0) + mat.get(dom, 0.0) + sto.get(dom, 0.0), 3)

    base = {
        "attention": {}, "evidence": evidence, "candidates": sorted(totals),
        "user_confirmation_required": True, "claim_limit": CLAIM_LIMIT,
    }
    if not totals:
        return {"status": "NO_MATCH", "domain": engine.GENERIC_DOMAIN,
                "confidence": "low", "reason": "no registry signal attended to any domain",
                **base}

    total = sum(totals.values())
    base["attention"] = {d: round(s / total, 3) for d, s in sorted(totals.items())}
    ranked = sorted(totals, key=lambda d: (-totals[d], d))
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None
    gap = (totals[top] - totals[second]) / total if second else 1.0

    if second and gap < TIE_MARGIN:
        return {"status": "ABSTAIN", "domain": engine.GENERIC_DOMAIN, "confidence": "low",
                "reason": f"attention too close across {ranked[:3]}; a human must choose",
                **base}
    return {"status": "MATCHED", "domain": top,
            "confidence": "high" if gap >= HIGH_MARGIN else "medium",
            "reason": f"attended to {top} via {', '.join(sorted(evidence.get(top, {})))}",
            **base}
