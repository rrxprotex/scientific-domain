# Physics worked example — simple pendulum

**Research question:** How does the length of a pendulum affect its oscillation
period?

This pack is the first cross-domain reference pack for scientific-domain: a
complete end-to-end worked example from a measurement file to a validated
record store and rendered brief. It exists to show the engine working on
physics material, not just lyrics: measurement, mathematical model, theory and
physical mechanism stay separated, and the refusal behaviour is part of the
example.

> **DATA STATUS: SYNTHETIC.** `measurements.csv` is generated demo data
> (fixed seed), not collected from a real experiment. Every observation record
> says so in its `claim_limit`. Producing invented measurements and presenting
> them as experimental results is exactly the failure this project exists to
> prevent — so the synthetic status is stated in the file header, the records,
> and here.

## Files

| File | Content |
|---|---|
| `ontology.physics.json` | 10 canonical terms, 3 theories, 9 relations |
| `measurements.csv` | SYNTHETIC trial data: length, mass, angle, cycles, elapsed time, period ± uncertainty |
| `records.jsonl` | 14 layered records (7 observation, 3 term, 3 theory, 1 mechanism) |
| `sources.md` | every source with exactly what was verified and how |
| `expected-brief.md` | output of `domain.py brief` for this store |
| `rejection-cases.json` | 7 deliberately wrong claims, each labelled with the gate that must catch it |

## Reproduce

```bash
python domain.py check --ontology physics --file examples/physics-pendulum/records.jsonl --strict
python domain.py brief  --ontology physics --file examples/physics-pendulum/records.jsonl
python tests.py         # includes the pack tests and the rejection-case loop
```

## What the example demonstrates

| Layer | Record | Epistemic point |
|---|---|---|
| Observation | PHY-001..004 | real measurement rows only, each with ± uncertainty; comparisons, never causal wording |
| Observation | PHY-005..007 | absence records: no large-angle trials, no friction measurement, no independent g |
| Term | PHY-008..010 | classification with rivals + distinguishing tests (simple vs physical pendulum, period vs frequency, small-angle vs anharmonic) |
| Theory | PHY-011 | model link kept INFERRED with an explicit applicability range |
| Theory | PHY-012 | T6 demonstration: the error-analysis theory has no verified source, so the link stays CANDIDATE |
| Theory | PHY-013 | rival frame (damping) named without claiming it was measured |
| Mechanism | PHY-014 | the only mechanism record: a HYPOTHESIS with 2 rivals and a falsifier |

## What the system must refuse (and does)

The review checklist for this domain, mapped to the deterministic gates in
`rejection-cases.json`:

| Requirement | Case | Gate |
|---|---|---|
| Invented term refused | REJ-PHY-002 | T1 |
| Theory recorded as observation refused | REJ-PHY-003 | T5 |
| Correlation-as-causation caught | REJ-PHY-001 | T2 |
| Evidence-free mechanism refused | REJ-PHY-004 | T7 |
| Ungrounded mechanism refused | REJ-PHY-005 | T8 |
| Untested conclusion (mass independence) refused | REJ-PHY-006 | G6 |
| Unverified-source theory cannot be INFERRED | REJ-PHY-007 | T6 |

Additionally: uncertainty is represented (±0.010 s carried through PHY-001/002
and PHY-012), and nothing forces a mechanism record — the store validates with
PHY-014 present as a falsifiable hypothesis or removed entirely. Honest
science sometimes means not writing a mechanism record.

## Scope overreach

"Uzunluk artışı periyodu artırır" as a universal claim is refused at the record
gate (T2) when it enters as an observation. A universal claim that arrives in
prose notes is handled by `domain.py audit`, which nominates unscoped universal
claims for matching against a scoped record. That is a nomination, not a gate —
the example keeps the boundary visible instead of pretending one regex catches
everything.
