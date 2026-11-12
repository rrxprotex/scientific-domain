# Authoring a domain vocabulary

A vocabulary is **data**, never engine code. `domain.py` contains no domain
words; adding a field requires adding one JSON file and one index entry.

## 1. Minimum file

`ontology.<domain>.json` (convention: `examples/ontology.<domain>.json` for
shipped reference packs):

```json
{
  "domain": "your-domain",
  "version": "0.1.0",
  "verification_policy": "How the sources below were checked. State plainly that full texts were not read if they were not.",
  "terms": {},
  "theories": {},
  "relations": []
}
```

Register it in `ontology.index.json`:

```json
"your-domain": {
  "file": "examples/ontology.your-domain.json",
  "keywords": ["keyword1", "anahtar1"],
  "citation_status": "MIXED",
  "note": "what this vocabulary covers"
}
```

The `file` path resolves relative to the package directory. Shipped example
vocabularies live under `examples/` as **opt-in reference packs**: nothing is
loaded until the user confirms a domain (`python domain.py use --ontology ...`)
or passes `--ontology` explicitly. Registering a domain never makes it a
default.

Then run `python domain.py ontology-check --all`. Routing keywords are matched
as lower-cased substrings; choose specific words, avoid short tokens. Two
domains tying on the same number of hits produce `ABSTAIN` rather than a guess.

## 2. Term entry

```json
"TERM-EXAMPLE": {
  "label": "canonical name",
  "definition": "what the term denotes",
  "evidence_class": "ARTIFACT",
  "indicators": ["observable signal in the material"],
  "rival_terms": ["TERM-OTHER"],
  "distinguishing_test": "what observation would choose this term over its rival",
  "sources": [
    {
      "ref": "Author (Year), 'Title', Journal, vol(issue), pages",
      "locator": "https://doi.org/... or a precise page/section",
      "kind": "PRIMARY",
      "citation_status": "VERIFIED_BIBLIOGRAPHIC",
      "access_note": "bibliographic record confirmed from a publisher page on DATE; full text not read"
    }
  ],
  "claim_limit": "what this term may NOT be used to assert"
}
```

Required: `label`, `definition`, `evidence_class`, `distinguishing_test`,
`sources` (at least one), `claim_limit`. `rival_terms` must reference declared
term ids. `indicators` are a convenience for the reader, not evidence.

`evidence_class` is one of `ARTIFACT`, `SOURCE`, `MEASUREMENT`,
`EXTERNAL_SUBJECT`, `INTERPRETIVE`, `CONVENTION`, `COUNTERFACTUAL`. It declares
what could ever make a claim `OBSERVED`: `INTERPRETIVE` can never be observed,
`EXTERNAL_SUBJECT` needs subject-level data, `COUNTERFACTUAL` needs a named
intervention.

## 3. Theory entry

```json
"THEORY-EXAMPLE": {
  "label": "established theory name",
  "statement": "the theory's claim, in one sentence",
  "explains": ["what it can interpret"],
  "does_not_explain": ["what it cannot establish for a specific material"],
  "evidence_class": "EXTERNAL_SUBJECT",
  "sources": [ ... ],
  "claim_limit": "population-level findings cannot certify an effect in one artifact"
}
```

`explains` and `does_not_explain` are both non-empty lists. The second is
load-bearing: it stops a theory name from being used as proof.

## 4. Source status — do not overstate

| `citation_status` | Meaning | Effect |
|---|---|---|
| `VERIFIED_BIBLIOGRAPHIC` | citation record confirmed; **full text not read**, findings not reproduced | can back `INFERRED` / `HYPOTHESIS` |
| `PARTIAL` | some metadata missing (editors, page range, publisher) | caps a theory link at `CANDIDATE` (T6) |
| `UNVERIFIED` | no locator verified; empty locator allowed | caps a theory link at `CANDIDATE` (T6) |

Every source needs `ref`, `kind` (`PRIMARY` / `SECONDARY` / `REFERENCE` /
`TERTIARY`), `citation_status` and `access_note`. A non-`UNVERIFIED` source
needs a non-empty `locator`. Never mark a source `VERIFIED_BIBLIOGRAPHIC`
because it "sounds right"; record where the citation was actually seen.

## 5. Relations

```json
{"from": "TERM-EXAMPLE", "to": "THEORY-EXAMPLE",
 "relation": "interpreted_by", "status": "CANDIDATE",
 "note": "why these two are connected"}
```

`relation` is one of `interpreted_by`, `instantiates`, `competes_with`,
`confused_with`; `status` is `CANDIDATE`, `CONTESTED` or `SUPPORTED`. Both ends
must be declared ids. Relations are annotations for readers, not shortcuts that
promote a claim — the gate still checks the record itself.

## 6. When you have no sourced vocabulary

Do **not** fabricate one. Use `ontology.generic.json`: zero terms, zero
theories, `allow_term_links: false`. Against it, `domain.py` permits
observation-only records from any domain and refuses every term / theory /
mechanism link (T9). That is a coverage fact, not a failure. A small honest
vocabulary is better than a large plausible one.

## 7. Profiles and the builder helpers

When emitting records, prefer the layer-first builders in `build.py`
(`observation`, `term`, `theory`, `mechanism`) over hand-writing JSON: they set
the correct per-layer defaults and refuse structurally invalid records instead
of producing placeholder content.

The CLI accepts an opt-in `--profile` flag (`strict` by default). `research` and
`lite` only relax field-length minimums (distinguishing test, theory link note);
they never soften the epistemic gates, so an unsourced term is still refused
under any profile.

## 8. Verify

```bash
python domain.py ontology-check --all
python domain.py --ontology your-domain terms --kind all
python domain.py route --text "a task in your domain"
python tests.py
python evals/run.py
```

Add at least one test that shows an invented term is refused in the new domain,
and one that shows a sourced term link validates. Do not edit an existing
assertion to make the addition pass.
