---
name: scientific-domain
description: "Use whenever a task produces or reviews KNOWLEDGE CLAIMS about a domain: analysing a text, lyric, score, paper, dataset or other material; naming or classifying concepts; relating observations to established scientific terminology and theory; writing research notes, literature summaries or teaching briefs; or auditing existing notes for overclaiming, invented terms, uncited theories and unsupported causal claims. It separates observation, canonical term, theoretical frame and mechanism hypothesis, and refuses to invent vocabulary or citations. Works in any field of expertise and falls back to an honest no-vocabulary state when no sourced domain ontology is registered. Do NOT use for simple factual lookups, greetings, routine code edits, git operations, or purely creative writing with no knowledge claim; when the signal is unclear, abstain rather than activate. NOTE: PROTOCOL.md is the canonical instruction file with the step-by-step procedure; this file is the legacy reference and is kept for backward compatibility."
license: MIT
metadata:
  category: "knowledge-work"
  version: "0.4.0"
  tags: ["scientific-representation", "ontology", "terminology", "theory-linking", "evidence", "domain-agnostic"]
---

# Scientific domain — connect material to the vocabulary of a discipline

> **Canonical instruction file is now `PROTOCOL.md`.** This file (SKILL.md) is
> the legacy reference kept for backward compatibility. PROTOCOL.md gives the
> step-by-step procedure the model should follow; read it first.

**One sentence:** take what a source actually shows, attach the discipline's
canonical term and established theory at the right epistemic level, and keep
causal claims in a separate, falsifiable mechanism record. Do not call
everything a mechanism.

This file is deliberately harness-agnostic. It works as a Claude Code / OpenCode
skill, as a WorkBuddy skill, or simply as a paste-in system prompt. The engine
is a plain Python CLI; vendor-specific wiring lives in `adapters/`.

## The failure this fixes

A research note usually says: *"Chorus repetition increases memorability."*
That single sentence mixes three things: a countable pattern in the text, a
concept with a name in the discipline, and a causal claim about a listener.
Labelling all three `mechanism` makes it impossible to tell what was observed,
what is a classification, and what is a hypothesis. This skill forces the split.

## Automatic activation — what is and is not promised

Activation is a property of the **host**, not of this file. Nothing in a markdown
file can guarantee that every harness will load it. Three mechanisms are shipped:

| Mechanism | Where | Guarantee |
|---|---|---|
| `description` matching | model-invoked skill harnesses | a model decision, not a deterministic one |
| `UserPromptSubmit` hook | `adapters/claude-code/hooks/hooks.json` | deterministic; silent unless it fires |
| always-loaded instruction line | `adapters/generic/SYSTEM-PROMPT.md`, `adapters/opencode/AGENTS.snippet.md` | depends on the harness reading that file |

`activate.py` is a deterministic, model-free classifier returning
`ACTIVATE / SKIP / ABSTAIN` with a reason and a `claim_limit`. **ABSTAIN is a
first-class result**: an unclear prompt is not a prompt to guess. Negative
triggers (greetings, factual lookups, routine edits, git commands, pure creative
writing) prevent over-triggering — a skill that fires on every prompt is worse
than one that never fires.

Activation decisions are heuristic nominations. `evals/run.py` grades 30 static
cases; a live dual-arm model comparison is reported as `NOT_RUN` in
`eval-results.json`. A perfect static score is not proof that a model follows
these instructions or produces better research.

## Four layers — never collapse them

| Layer | Does | May claim | Requires |
|---|---|---|---|
| `observation` | what the material shows | `OBSERVED` / `PRESENT`, within a declared scope | file + locator + scope |
| `term` | which canonical concept it instantiates | `INFERRED` / `CANDIDATE` classification | `term_id` from the ontology, a declared rival, a distinguishing test |
| `theory` | which established frame interprets it | `INFERRED` / `HYPOTHESIS` / `CANDIDATE` — **never `OBSERVED`** | `theory_id`, verified citation, what it explains here and what it does not |
| `mechanism` | a causal chain proposal | `HYPOTHESIS` (or `OBSERVED` with a named intervention) | rival explanation + falsifier + at least one term/theory anchor |

**Rule:** `mechanism` is not the default noun for a finding. A record without
causal wording cannot be a mechanism (T7); a causal statement cannot hide in an
`observation` or `term` record (T2). That is the structural fix for
"everything is a mechanism".

**Term ≠ theory ≠ mechanism.** A term *defines* (refrain), a theory *interprets*
(processing fluency), a mechanism *proposes a cause* (repetition → fluency →
recall). Three records, three statuses, three claim limits.

## Two axes plus an evidence class

- `representation`: `PRESENT` · `UNDER_IMPLEMENTED` · `NOT_REPRESENTED` · `UNKNOWN`
- `evidence_status`: `OBSERVED` · `CANDIDATE` · `INFERRED` · `HYPOTHESIS` · `UNVERIFIED_CLAIM` · `DOCUMENTED_CLAIM`
- `evidence_class`: `ARTIFACT` · `SOURCE` · `MEASUREMENT` · `EXTERNAL_SUBJECT` · `INTERPRETIVE` · `CONVENTION` · `COUNTERFACTUAL`

The class declares what evidence could ever make a claim `OBSERVED`. An
`EXTERNAL_SUBJECT` claim (listener, reader, user) cannot be observed from a
document alone; `INTERPRETIVE` can never be `OBSERVED` at all.

## Record shape

```json
{
  "id": "LNK-001",
  "layer": "observation",
  "statement": "The chorus repeats the same line three times.",
  "domain": "songwriting",
  "scope": {"declared": true, "sources": ["ornek.cho"]},
  "evidence": [{"kind": "artifact_site", "ref": "ornek.cho", "locator": "L10-L14"}],
  "evidence_class": "ARTIFACT",
  "representation": "PRESENT",
  "evidence_status": "OBSERVED",
  "term_id": null, "theory_ids": [], "rival_term_ids": [],
  "distinguishing_test": "", "theory_link_note": "", "mechanism": {},
  "claim_limit": "Only this file's repetition count; it says nothing about listener recall."
}
```

`term` adds `term_id` + `rival_term_ids` + `distinguishing_test`. `theory` adds
`theory_ids` + `theory_link_note`. `mechanism` adds `mechanism.rivals` +
`mechanism.falsifier` (+ `intervention` when `OBSERVED`). Every record carries a
`claim_limit` stating what it may NOT be used to assert.

## Gates (enforced in code)

`G0–G11` cover required fields, scope, claim limits, evidence kinds, observed
promotion, absence, documented claims and credential-shaped strings. `T1–T9`
cover the scientific layer: no invented term/theory id, no interpretation
smuggled into an observation, class/rival/distinguishing-test requirements,
theory never observed, citation status capping status, mechanism rivals and
falsifiers, ontology grounding, and **T9: a vocabulary-free domain refuses all
term/theory/mechanism links instead of inventing them**.

The validator **refuses, never repairs**. A tool that silently upgrades or
downgrades a claim is how a guess becomes a fact.

## Commands

```bash
# 0) nominate a domain from the task text (heuristic, never a verdict)
python domain.py route --text "Analyze this lyric and relate it to theory"
python activate.py --text "Analyze this lyric and relate it to theory"

# 0b) SCORE THE DOMAIN ATTENTION (deterministic weights, evidence, never a verdict)
python domain.py attention --text "..." --dir .

# 0c) CONSENT STEP: the user confirms the expertise domain (attention/route only propose)
python domain.py use --ontology songwriting   # or your own ontology file path

# 1) validate the vocabularies and read them before naming anything
python domain.py ontology-check --all
python domain.py terms --kind all
python domain.py --ontology literary-rhetoric terms --kind terms

# 2) production: validate a record BEFORE it reaches the store
python domain.py add --json @record.json --file records.jsonl

# 3) post-hoc: re-validate, nominate overclaims, render the scientific brief
python domain.py check --file records.jsonl --strict
python domain.py audit --notes research-notes.md --file records.jsonl
python domain.py brief --file records.jsonl

# 4) evaluate the activation gate (static; live dual-arm is NOT_RUN)
python evals/run.py
```

`--ontology` accepts a file path **or a registered domain name** from
`ontology.index.json`. There is **no default domain**: without a confirmed
selection (`use`) or an explicit `--ontology`, the vocabulary-free `generic`
ontology applies and every term/theory/mechanism link is refused (T9).
`check --strict` also reports `CONTESTED` when the same
statement carries conflicting labels. `audit` emits lexical nominations only,
never findings. `brief` refuses to run on a store that does not validate.

## Worked example

Material: `examples/ornek.cho`, a short Turkish lyric with two verses, two identical
choruses, "Dön geri" repeated three times per chorus, and one changed third
line in verse 2. The reference pack `examples/ornek.jsonl` holds nine validated
records and `examples/ornek-brief.md` is the rendered scientific brief.

| Material | Canonical term | Theoretical frame | Mechanism (separate record) |
|---|---|---|---|
| 3× repetition, chorus twice verbatim | `TERM-CHORUS`, rival `TERM-REFRAIN`; test: is there a separate section boundary? | — | — |
| 3 of 4 verse lines identical, third changes | `TERM-INCREMENTAL-REPETITION`, rival `TERM-ANAPHORA` | `THEORY-EXPECTANCY-ITPRA` (Meyer 1956; Huron 2006) — a candidate expectation violation | "the changed line creates tension" → `HYPOTHESIS` + rival + falsifier |
| repeated "Dön geri" | `TERM-HOOK` only as **candidate** (`EXTERNAL_SUBJECT`) | `THEORY-PROCESSING-FLUENCY` (Nunes et al. 2015), `THEORY-MERE-EXPOSURE` (Zajonc 1968) | "repetition → fluency → recall" → `HYPOTHESIS`; rival `THEORY-HABITUATION` (Rankin et al. 2009); falsifier stated |
| the line "Bir nakarat unutulmaz diye" | `TERM-INMI` as a conceptual distinction | `THEORY-INMI` (Jakubowski et al. 2017; Byron & Fowles 2015) | `DOCUMENTED_CLAIM`: the text asserts its own claim; not evidence |
| no `{bridge}` in this file | `NOT_REPRESENTED`, scope = one file | — | — |
| "the writer chose repetition deliberately" | `UNKNOWN` | — | — |

The repetition is `OBSERVED`; calling it a hook requires listener data;
linking it to literature is an interpretation; asserting a cause is a separate
mechanism hypothesis. Four statuses, four records.

## Adding a domain (no engine changes)

`ontology.index.json` maps domain keywords → a JSON vocabulary. Write
`ontology.<domain>.json` with `terms{}`, `theories{}`, `relations[]`; every
term needs `label`, `definition`, `evidence_class`, `rival_terms`,
`distinguishing_test`, `sources`, `claim_limit`; every theory needs `label`,
`statement`, `explains`, `does_not_explain`, `evidence_class`, `sources`,
`claim_limit`. Validate with `ontology-check --all`. See
`docs/ontology-authoring.md`. If no vocabulary matches, `route` returns
`NO_MATCH` → `ontology.generic.json`, which has zero terms and refuses links.
**Registering a domain with unsourced terms is worse than registering none.**

## Citation honesty

Every source carries `ref`, `locator`, `kind`, `citation_status` and
`access_note`. `VERIFIED_BIBLIOGRAPHIC` means **the citation record was
confirmed; the full text was not read and its findings were not reproduced
here**. `PARTIAL` means incomplete metadata. `UNVERIFIED` means no locator yet.
Any theory without a `VERIFIED_BIBLIOGRAPHIC` source caps a link at `CANDIDATE`
(T6). A theory's `does_not_explain` field records what it cannot establish for
this particular material. Zero findings is a coverage statement, not success.

## What this skill refuses to do

Invent a term or a citation · turn a correlation into a cause · say "absent"
without declaring scope · make an `audience` claim `OBSERVED` from a document ·
let a candidate grade itself · treat zero findings as success · pretend an
unread source was read · claim a live-model improvement without a dual-arm run.
