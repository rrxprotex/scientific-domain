# Five refusals you will hit (and how to fix them)

The validator refuses instead of repairing. Each example shows the refused
record, the gate that fired, and the fix — usually: split the sentence into two
or three records.

## 1. Invented term (T1)

```
refused: term_id "TERM-CATCHINESS" is not a canonical term (T1)
```

```json
{ "layer": "term", "term_id": "TERM-CATCHINESS", ... }        // WRONG
```

**Fix.** Run `python domain.py terms --kind terms` and pick a declared term.
If nothing fits, the honest answer is an `observation` record, or — if you are
sure the discipline has the concept — add a **sourced** ontology entry first
(see `docs/ontology-authoring.md`). An unsourced vocabulary is worse than none.

## 2. Causation hidden in an observation (T2)

```
refused: causal wording requires layer=mechanism (T2)
```

```json
{ "layer": "observation",
  "statement": "Chorus repetition increases memorability.", ... }   // WRONG
```

**Fix.** Two records: the count (`observation`, "the chorus line repeats three
times", `OBSERVED`) and the causal claim (`mechanism`, `HYPOTHESIS`, with
rivals + falsifier). The listener effect is `EXTERNAL_SUBJECT`: it can never be
`OBSERVED` from the document alone.

## 3. Term link without a rival or test (T4)

```
refused: name at least one declared rival of 'TERM-CHORUS' (['TERM-REFRAIN', ...])
refused: a term link needs a distinguishing test (T4)
```

```json
{ "layer": "term", "term_id": "TERM-CHORUS", "rival_term_ids": [], ... }  // WRONG
```

**Fix.** Name the rival you rejected and the observation that decided it:

```json
{ "rival_term_ids": ["TERM-REFRAIN"],
  "distinguishing_test": "A separate {chorus} section boundary is marked; a
   refrain would be a returning line inside a verse." }
```

## 4. Theory graded as observed, or uncited (T5 / T6)

```
refused: a theory link can never be OBSERVED - it interprets (T5)
refused: theory 'THEORY-X' has no VERIFIED_BIBLIOGRAPHIC source; status is
         capped at CANDIDATE (T6)
```

```json
{ "layer": "theory", "theory_ids": ["THEORY-X"],
  "evidence_status": "OBSERVED", ... }                              // WRONG
```

**Fix.** Set `evidence_status: "INFERRED"` (or `CANDIDATE` when the source is
not `VERIFIED_BIBLIOGRAPHIC`) and state what the theory explains *here* in
`theory_link_note`. Naming a theory is an interpretation, not a measurement.

## 5. Mechanism without rivals or falsifier (T7 / T8)

```
refused: a mechanism needs >=1 rival explanation (T7)
refused: a mechanism needs a falsifier (T7)
refused: a mechanism must be grounded in a canonical term or theory (T8)
```

```json
{ "layer": "mechanism",
  "statement": "Repetition drives recall through fluency.",
  "mechanism": {}, ... }                                            // WRONG
```

**Fix.**

```json
{ "mechanism": {
    "rivals": ["melodic contour alone could produce the same recall"],
    "falsifier": "if a non-repeated chorus is recalled equally often, the
                  mechanism fails"
  },
  "theory_ids": ["THEORY-PROCESSING-FLUENCY"] }
```

If you cannot state the rivals and the falsifier, the causal claim is not a
finding — leave it out and report what you observed.

## Bonus: absence without scope (G3)

```
refused: absence needs scope.declared=true (G3)
```

**Fix.** Absence is always about inspected material: `scope: {"declared": true,
"sources": ["the-file.txt"]}` and a claim limit saying this is one file, not
the whole discipline.
