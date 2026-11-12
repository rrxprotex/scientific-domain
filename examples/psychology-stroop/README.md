# Psychology worked example — Stroop effect

**Research question:** When a word's meaning conflicts with its ink colour,
does colour-naming time change?

The second cross-domain reference pack. Psychology is the harder test of the
engine: the measured behaviour, the concept used to describe it, and the
explanation of it are three different things, and the gaps between them are
where overclaiming lives. This pack shows the epistemic ladder working on
human-behaviour material — including the DOCUMENTED_CLAIM case the review
asked for: a finding reported by a source is recorded as the source's claim,
not as our own OBSERVED result.

> **DATA STATUS: SYNTHETIC.** `measurements.csv` is generated demo data
> (fixed seed) with **no human subjects involved**. Every observation record
> says so in its `claim_limit`. A synthetic response time is not participant
> data, and this pack never pretends otherwise.

## Files

| File | Content |
|---|---|
| `ontology.psychology.json` | 7 canonical terms, 3 theories, 7 relations |
| `measurements.csv` | SYNTHETIC trial data: participant id, condition, stimulus word/ink, response time, correctness |
| `records.jsonl` | 12 layered records (6 observation incl. 1 DOCUMENTED_CLAIM, 2 term, 3 theory, 1 mechanism) |
| `sources.md` | every source with exactly what was verified and how |
| `expected-brief.md` | output of `domain.py brief` for this store |
| `rejection-cases.json` | 7 deliberately wrong claims, each labelled with the gate that must catch it |

## Reproduce

```bash
python domain.py check --ontology psychology --file examples/psychology-stroop/records.jsonl --strict
python domain.py brief  --ontology psychology --file examples/psychology-stroop/records.jsonl
python tests.py
```

## What the example demonstrates

| Record | Epistemic point |
|---|---|
| PSY-001..003 | condition statistics as observations; the between-condition comparison is stated without causal wording |
| PSY-004, PSY-012 | absence records: no demographics; no manipulation that could separate the rival accounts |
| PSY-005 | **DOCUMENTED_CLAIM**: Stroop (1935)'s reported finding is recorded as the source's claim (G8: source_mention, not PRESENT) |
| PSY-006, PSY-007 | term classification with rivals: interference vs facilitation (needs the neutral baseline), reaction time vs accuracy |
| PSY-008 | theory interpretation kept INFERRED — a reading of the group difference, not a mechanism finding |
| PSY-009, PSY-010 | rival theories kept CANDIDATE (T6 for the unverified one; honesty for the other) |
| PSY-011 | the only mechanism record: a HYPOTHESIS with 2 named rivals and a falsifier |

## What the system must refuse (and does)

| Requirement | Case | Gate |
|---|---|---|
| Correlation-as-causation caught | REJ-PSY-001 | T2 |
| Invented term refused | REJ-PSY-002 | T1 |
| Theory existence ≠ mechanism proof | REJ-PSY-003 | T5 |
| Evidence-free mechanism refused | REJ-PSY-004 | T7 |
| Individual claim without subject data refused | REJ-PSY-005 | G6 |
| Ungrounded mechanism refused | REJ-PSY-006 | T8 |
| Unverified-source theory cannot be INFERRED | REJ-PSY-007 | T6 |

The review's remaining checklist items map elsewhere, deliberately:

- **Generalising one experiment to all humans** has no record-level gate — a
  regex cannot see scope in prose. It is covered by `domain.py audit`, which
  nominates unscoped universal claims, and tested there.
- **Uncertainty representation** is demonstrated by the ±-carrying observation
  records and the rival-account records that say what the data cannot decide.
- **No forced mechanism**: the store validates with PSY-011 removed. Where the
  data cannot separate accounts, the honest output is a CANDIDATE theory link
  and an absence record, not a mechanism.
