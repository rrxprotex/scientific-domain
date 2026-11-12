# Scientific domain — a protocol, not a dictionary

**One sentence:** take what a source actually shows, attach the discipline's
canonical term and established theory at the right epistemic level, and keep
causal claims in a separate, falsifiable mechanism record. Do not call
everything a mechanism.

This is the **canonical instruction file** for the skill. The engine, adapters,
and reference docs (ontology-authoring.md, SKILL.md) describe how it works; this
file describes what you **do** with it. Read this before anything else.

## What the skill is for — and for what it is not

Use it when a task **produces or reviews knowledge claims** about a domain:
analysing a text, lyric, score, paper or dataset; naming or classifying
concepts; relating observations to established terminology and theory; writing
research notes or literature summaries; auditing existing notes for overclaiming.

Do **not** use it for simple factual lookups, greetings, routine code edits,
git operations, or purely creative writing with no knowledge claim. When the
signal is unclear, abstain rather than guess. A skill that fires on every prompt
is worse than one that never fires.

> Most AI failures in domain research are not reasoning errors — they are
> representation errors. A model sees repetition in a lyric and writes
> *"chorus repetition increases memorability"*: one sentence that silently
> promotes a countable pattern, a form classification and an unmeasured
> listener effect into a single "finding".

## The protocol — a step-by-step procedure

Execute these steps **in order**. Each step decides whether the next one
applies. Never jump ahead.

**Step 1 — Is this a knowledge-work task?**
Run `python activate.py --text "<your prompt>"` (or check the activation
decision injected by the hook). If it returns `SKIP` (greeting, factual lookup,
routine edit, creative writing) or `ABSTAIN` (too short, no signal), this skill
is off the table for this prompt. Stop.

**Step 2 — Ask the user which expertise domain they work in, then confirm it.**
First, score what the task attends to:

```bash
python domain.py attention --text "<your prompt>" --dir <working directory>
```

`attention` ranks candidate domains with **explainable deterministic weights**
(keyword hits, material file NAMES, store continuity) and returns the matched
evidence per domain — it is not a neural model and never a verdict. Then run
`python domain.py route --text "<your prompt>"` — it only **proposes** a
vocabulary (`MATCHED / NO_MATCH / ABSTAIN`). The choice of expertise domain is
a human decision:

```bash
python domain.py use --ontology <domain-or-ontology-path>
```

- The confirmation is recorded in `domain.config.json`. Ask for it once per
  project; do not re-ask on every record.
- Until a domain is confirmed, the vocabulary-free `generic` ontology applies:
  observation records are allowed, and every term/theory/mechanism link is
  refused instead of invented (T9). **Do not manufacture a domain vocabulary.**
- `NO_MATCH` or `ABSTAIN` from `route` → generic until the user supplies a
  sourced ontology. Do not guess a domain to make a link possible.

**Step 3 — Observation pass. One record per distinct finding.**
For every countable, verifiable thing the material actually shows:
- `layer: observation`, `evidence_status: OBSERVED`, `representation: PRESENT`
- Scope must name the inspected material; every observation carries at least one
  `artifact_site` evidence row with a locator (`ornek.cho`, "L10-L14").
- Statement is neutral prose. No causal wording, no classification, no theory.
- **Claim limit states what this record may NOT assert** (e.g. "only this file's
  repetition count; it says nothing about listener recall").

Rule T2: a causal statement may never hide in an observation. If the sentence
says "X increases Y", this is not step 3 — it belongs in step 6 or nowhere.

**Step 4 — Term links. Only when a canonical concept applies.**
A record is a term only if you can name the exact canonical term from the
nominated ontology:
- `layer: term`, `evidence_status` is `INFERRED`/`CANDIDATE` (never `OBSERVED`),
  `representation: UNDER_IMPLEMENTED`.
- `term_id` must point to a declared term (T1: invented terms are refused).
- **You must name at least one declared rival** (`rival_term_ids`) and state a
  **distinguishing test** — the observation that would choose this term over the
  rival (T4).
- Example: the recurring section becomes `TERM-CHORUS`, not `TERM-REFRAIN`,
  because a separate section boundary is marked; the test is "is the repeating
  material its own section between verses, or a returning line inside a stanza?"

A term defines; it does not interpret and it does not cause.

**Step 5 — Theory links. Only as interpretation.**
A record is a theory only when an established frame interprets what you observed:
- `layer: theory`, `theory_ids: [...]`, `theory_link_note` explaining what the
  theory explains **here** (T5).
- **A theory can never be `OBSERVED`** — it interprets, it does not measure (T5).
- Citation status caps the grade: any theory whose sources are not
  `VERIFIED_BIBLIOGRAPHIC` is capped at `CANDIDATE` (T6). A verified record
  means the citation exists; **full texts were not read and findings were not
  reproduced**.
- Example: "the repetition may be read through processing fluency" →
  `THEORY-PROCESSING-FLUENCY`, capped at CANDIDATE because this file contains no
  listener measurement.

**Step 6 — Mechanism. Only if the sentence is genuinely causal.**
A mechanism is a **causal hypothesis**, not a finding. Create one only when the
statement contains causal wording ("X increases Y", "leads to", "because"):
- `layer: mechanism`, `evidence_status: HYPOTHESIS`, causal wording present (T7).
- `mechanism.rivals`: at least one rival explanation ("the same recall could
  come from melodic contour alone").
- `mechanism.falsifier`: the observation that would kill it ("if a non-repeated
  chorus is recalled equally often, the mechanism fails").
- **Grounded in a canonical term or theory**, not a coined name (T8).
- `OBSERVED` mechanisms need a named intervention and an intervention evidence
  row (T7).

If the statement is not causal — if it is a classification or an interpretation
— it is **not a mechanism**. Use term or theory instead. If there is no causal
claim at all, there is no step 6.

**Step 7 — Claim limits bind the whole record.**
Every record carries a `claim_limit`. The strength of your conclusion is the
strength of its weakest record. An `EXTERNAL_SUBJECT` record (listener, reader,
user) can never be `OBSERVED` from a document alone.

**Step 8 — Validate before you call it done.**
Run `python domain.py check --file <store>.jsonl --strict`. The validator
refuses; it never repairs. Fix the problems it lists (they carry gate tags like
`G2`, `T4`, `T7` so you know which rule fired). `brief` is refused on an invalid
store — if `brief` runs, your store validates.

**Step 9 — Zero findings is a coverage statement, not success.**
No record is a finding. `NOT_REPRESENTED` with declared scope is a real result
("this file has no bridge section"; it does not mean the discipline lacks bridges).

## The record shape — the six columns that matter

All optional fields are listed at the end; nothing below may be empty:

| Field | What it holds | Example |
|---|---|---|
| `id` | stable identifier | `"LNK-001"` |
| `layer` | **what epistemic job the record does** | `"observation"` |
| `statement` | neutral description of the finding | `"The chorus repeats the same line three times."` |
| `scope.sources` | what was inspected | `["ornek.cho"]` |
| `evidence_status` | epistemic grade | `"OBSERVED"` |
| `claim_limit` | what the record may NOT assert | `"Only this file's repetition count..."` |

Optional but usually required by layer: `evidence_class`, `representation`,
`term_id`, `rival_term_ids`, `distinguishing_test`, `theory_ids`,
`theory_link_note`, `mechanism.{rivals,falsifier,intervention}`. Build records
with the layer builders (`build.observation()`, `build.term()`,
`build.theory()`, `build.mechanism()`) — they set the defaults and required
fields for you.

## The epistemic ladder

```
OBSERVED    — measured/seen in the material (artifact_site or measurement)
CANDIDATE   — plausible link, citation not VERIFIED_BIBLIOGRAPHIC
INFERRED    — a reading that follows from the observation
HYPOTHESIS  — a causal proposal (mechanism only, unless the class admits it)
DOCUMENTED_CLAIM — the material says it itself (source_mention)
UNVERIFIED_CLAIM — asserted but uncertain; needs uncertainty_reason
```

A theory link lives at `CANDIDATE`/`INFERRED`/`HYPOTHESIS` — never at `OBSERVED`.
An audience claim lives at `CANDIDATE`/`HYPOTHESIS` from a document — never at
`OBSERVED`.

## Worked example — the reference pack `examples/ornek.cho`

Material: a short Turkish lyric with two verses, two identical choruses, "Dön
geri" repeated three times per chorus, and one changed third line in verse 2.
Nine records are shipped in `examples/ornek.jsonl`. Here is the decision trace for three
of them:

**The repetition, three times per chorus.** Step 3: count it, neutral wording,
`artifact_site` evidence with locator "L10-L14", `OBSERVED`, `ARTIFACT`. Claim
limit: nothing about memorability. (This is **one** record.)

**Is that a chorus or a refrain?** Step 4: `layer: term`, `TERM-CHORUS` because
the source marks a separate section boundary; rival `TERM-REFRAIN`; distinguishing
test: "is there a separate section boundary, or only a returning line inside a
verse?". If the answer were "a returning line only", the label would be
`TERM-REFRAIN`. (This is a **second** record.)

**"Repetition increases memorability."** Step 6: causal wording → this needs a
mechanism. But Step 5 says listener data is `EXTERNAL_SUBJECT` and cannot be
`OBSERVED` from this file; Step 5 also says linking to literature is an
interpretation, not evidence. So the causal claim becomes a separate mechanism
record: `HYPOTHESIS`, rivals ("melodic contour alone could explain the same
recall"), falsifier ("non-repeated chorus recalled equally often → mechanism
fails"), grounded in `TERM-CHORUS` and `THEORY-PROCESSING-FLUENCY`. If you
cannot state the rivals and falsifier, the causal claim is not a finding — it
drops out.

The repetition is `OBSERVED`; calling it a hook requires listener data; linking
it to literature is an interpretation; asserting a cause is a separate hypothesis.
**Four epistemic grades, four records.**

## Opt-in features (clearly marked)

These are **not** the default behavior; they change rigor or output shape and
must be requested explicitly:

- `--profile research` — loosens a few requirements (shorter distinguishing
  test, one rival accepted) for faster note-taking. Documented in domain.py;
  profiles never soften a refusal that protects the epistemic ladder.
- `brief --layered` — two-pass report: records needing work first, then approved.
- `--render <file>` — write the brief to a file.
- `--jsonschema` — emit the record schema as JSON Schema for external tooling.

When in doubt, use the defaults. The defaults are the rigorous path.

## When to abstain — the honest answers

- No registered domain matches → generic ontology, observations only.
- The vocabulary you need has unsourced terms → do not fabricate it. A small
  honest vocabulary is better than a large plausible one. An unsourced
  vocabulary is worse than no vocabulary.
- You want to say "X causes Y" but have no rivals, no falsifier, no measurement
  → that is not a finding. Say what you observed, and nothing stronger.
- The prompt is a greeting, a factual lookup, a code edit, or pure creative
  writing → this skill is not the right tool.

## Commands at a glance

```bash
python activate.py --text "Analyze this lyric and relate it to theory"  # Step 1
python domain.py route --text "..."                                     # Step 2: proposal only
python domain.py attention --text "..." --dir .                          # Step 2: ranked candidates + evidence
python domain.py use --ontology songwriting                             # Step 2: user confirms
python domain.py --ontology songwriting terms --kind all                # Step 2/4 vocab
python domain.py add --json @record.json --file records.jsonl           # Steps 3–6
python domain.py check --file records.jsonl --strict                    # Step 8
python domain.py audit --notes notes.md --file records.jsonl            # post-hoc
python domain.py brief --file records.jsonl                             # Step 8 (renders)
python tests.py                                                         # 112 unit tests
python evals/run.py                                                     # static activation + CLI suite
python evals/semantic.py                                                # structural grader self-test
```

The engine is a plain Python CLI; vendor-specific wiring lives in `adapters/`.
Nothing in these instructions can guarantee that every harness loads the skill —
automatic activation is a host capability, not a property of a markdown file.
