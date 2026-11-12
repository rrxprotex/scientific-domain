# Evaluation suite

Two runners, both **static, model-free, stdlib-only**:

- `python evals/run.py` — activation decisions + CLI contract cases; writes
  `eval-results.json`.
- `python evals/semantic.py` — the structural grader for multi-record outputs
  (see below); a self-test over `semantic.json`.
- `python evals/adversarial.py` — **adversarial scientific evaluation**: 26
  labelled cases written before the runner - 16 attack records (fabricated
  terms/theories, hidden causality, ungrounded mechanisms, scope-less absence,
  credential strings, evidence-free PRESENT observations…) that must be REFUSED
  with the named gate, 5 accepted records (4 controls + 1 negation-screen
  regression), and 5 attack prompts (greeting disguise, prompt injection,
  shouting/emoji, word repetition). Writes `adversarial-results.json`.
- `python evals/dualarm.py` — the **dual-arm benchmark instrument** (see below).

No API key, no network, no language model.

## What is graded

| Group | Count | What it checks |
|---|---|---|
| Activation cases (`cases.json`) | 19 | `ACTIVATE / SKIP / ABSTAIN` and the nominated domain, against labels written before the classifier was run (EN, TR, DE, ES, FR, RU) |
| Contract cases (`run.py`) | 11 | real CLI behaviour: all ontologies validate, strict check on the shipped reference-pack example, `NO_MATCH` routing, invented term refused before any write, mechanism without falsifier refused, generic ontology refusing links (T9), hook silent on SKIP, hook injecting context on ACTIVATE, consent flow (T9 refusal before confirmation; `use` then unblocks `add`), and domain attention ranking with evidence + `user_confirmation_required` |
| Structural cases (`semantic.json` via `semantic.py`) | 8 | the SHAPE of a record store against seven rules: claim_limit present, no causal claim in an observation, term has rival + distinguishing test, theory never OBSERVED, mechanism has rivals + falsifier, mechanism grounded in a term/theory, observation carries a locator. Cases labelled `good` must pass every rule; each `bad` case must violate exactly the named rule — so the grader itself is verified. |

`ABSTAIN` is a first-class outcome. Negative triggers (greetings, factual
lookups, routine edits, git commands, pure creative writing) are graded too:
a skill that fires on every prompt is worse than one that never fires.

## What is NOT graded — read before trusting the score

`eval-results.json` records `liveModelDualArm.status = "NOT_RUN"`. Static checks
validate a deterministic classifier and generated artifacts. They do **not**
prove that:

- a language model reads `SKILL.md`,
- an installed harness activates the skill automatically,
- the model produces better research records with the skill than without it,
- any cited source's findings were reproduced (full texts were not read).

A score of 1.00 means these deterministic checks passed. It is not a claim about
semantic reasoning quality or model adherence.

## Running the missing measurement

`evals/dualarm.py` is the instrument. Without a model command it reports
`NOT_RUN` (the state this repository ships in). With `--on` / `--off` commands
(identical except for the skill being loaded) it runs every case twice,
collects artifacts into `dualarm-artifacts/`, and — with `--judge` — grades each
artifact on the rubric R1–R5 (canonical terms only, citation status labelled,
theory never OBSERVED, causal claims carry rivals + falsifier, claim_limit
present). It reports the **delta between arms**, which is the only evidence of
benefit.

1. Take the 19 prompts from `cases.json` plus 10–20 real domain tasks.
2. Run each twice: skill installed vs not installed, same model, same judge.
3. Grade the produced artifacts with the same rubric (canonical term used,
   citation present and status-labelled, correct epistemic level, claim_limit).
4. Report the delta, per-case artifacts, and the number of runs. A high
   absolute score with a near-zero delta is **not** evidence of benefit.
5. Only then change `liveModelDualArm.status` to `RUN` and record the results.

## Adding a case

Add an entry to `cases.json` with `id`, `prompt`, `expect`, `expect_domain`
(`null` when irrelevant) and `why`. Write the label before running the
classifier. For CLI behaviour, add a `contract_cases()` entry that drives the
real command and grades its exit code and output.
