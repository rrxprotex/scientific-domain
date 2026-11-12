# Scientific Domain

**Connect what a source actually shows to the vocabulary and theories of a discipline — at the correct epistemic level, without inventing anything.**

A harness-agnostic agent skill + a dependency-free Python engine. It separates
**observation**, **canonical term**, **theoretical frame** and **mechanism
hypothesis**, and refuses the two failure modes that make research notes
untrustworthy: calling everything a "mechanism", and freely naming concepts or
citing theories that were never sourced.

> **`PROTOCOL.md` is the canonical instruction file.** It gives the model a
> step-by-step procedure (9 steps, in order) instead of a schema reference.
> Start there. `SKILL.md` remains for backward compatibility. New here?
> `docs/quick-reference.md` is the pocket card; `docs/rejection-examples.md`
> covers the five refusals you will hit first.

## Scientific Domain in Practice

The engine's domain-independence is not an argument — it is demonstrated on
worked research examples across disciplines, each with its own measurement
data, sources, expected brief and labelled rejection cases:

| Discipline | Example | Status | Journey |
|---|---|---|---|
| **Physics** | [simple pendulum](examples/physics-pendulum/) | **Worked example** | measurement → physical concept → theoretical model → mechanism hypothesis |
| **Psychology** | [Stroop effect](examples/psychology-stroop/) | **Worked example** | experimental data → cognitive concept → theory → causal hypothesis (incl. DOCUMENTED_CLAIM handling) |
| **Biology** | enzyme kinetics (Michaelis–Menten) | Planned | measurement → kinetic model → biological mechanism |

Every pack ships SYNTHETIC data that is labelled as synthetic everywhere it
appears, verified-vs-unverified source records, and rejection cases where each
deliberately wrong claim is paired with the gate that must catch it.

## The protocol in seven lines

1. Is this a knowledge-work task? (`activate.py`) If SKIP/ABSTAIN — stop.
2. Ask the user which expertise domain; `route` only proposes, `use` confirms.
   No domain is loaded until a human chooses one.
3. Observation pass: one neutral, located record per distinct finding.
4. Term links: canonical `term_id` + declared rival + distinguishing test.
5. Theory links: never OBSERVED; citation status caps the grade (T6).
6. Mechanism: only genuinely causal wording; rivals + falsifier mandatory.
7. `check --strict` before you call it done; zero findings = coverage, not success.

> Most AI failures in domain research are not reasoning errors — they are
> representation errors. A model sees repetition in a lyric and writes
> *"chorus repetition increases memorability"*: one sentence that silently
> promotes a countable pattern, a form classification and an unmeasured
> listener effect into a single "finding".

## Why it is different

| Common output | This skill |
|---|---|
| "the mechanism is repetition-with-variation" | `TERM-INCREMENTAL-REPETITION` with a declared rival (`TERM-ANAPHORA`) and a distinguishing test |
| "processing fluency explains this" | `THEORY-PROCESSING-FLUENCY` with a verified bibliographic record, what it explains here, and what it cannot explain |
| "repetition improves recall" | a separate `mechanism` hypothesis with rivals, a falsifier, and `HYPOTHESIS` status |
| "no bridge exists" | `NOT_REPRESENTED` **with declared scope** — absence in one file, not in a discipline |
| an invented term or a plausible citation | refused by code (T1, T6, T9) |

`mechanism` is not the default noun for a finding. Gate T7 refuses a mechanism
record without causal wording, rivals and a falsifier; gate T2 refuses to hide a
causal claim inside an observation.

## Requirements

Python **3.10+**, standard library only. No pip install, no API key, no network,
no account. Works on Windows, macOS and Linux, in any shell or agent harness.
The activation gate recognises knowledge-work signals in EN, TR, DE, ES/PT/IT/FR
and RU surface forms (heuristic nomination; graded in `evals/cases.json`).

## Two-minute quickstart

Read `PROTOCOL.md` first — it is the instruction surface for the skill. The
skill works for **any** expertise area and ships **no default domain**: until
the user confirms one, the generic vocabulary applies (observation-only).
Then:

```bash
cd scientific-domain

python domain.py route --text "Analyze this lyric and relate it to theory"  # proposal only
python domain.py attention --text "Analyze this lyric" --dir .   # ranked domains + evidence
python domain.py use --ontology songwriting        # CONSENT STEP: the user confirms the domain
python domain.py ontology-check --all
python domain.py terms --kind all

python activate.py --text "Analyze this lyric and relate it to theory"
python domain.py check --ontology songwriting --file examples/ornek.jsonl --strict
python domain.py brief --ontology songwriting --file examples/ornek.jsonl
```

Then validate the shipped reference pack end to end:

```bash
python domain.py check --ontology songwriting --file examples/ornek.jsonl --strict
python domain.py brief --ontology songwriting --file examples/ornek.jsonl
python tests.py             # 112 unit tests
python evals/run.py         # 32 static eval cases
python evals/semantic.py    # 8 structural grader cases
python evals/adversarial.py # 28 adversarial cases (attacks + controls)
python evals/dualarm.py     # dual-arm instrument -> NOT_RUN until a model is configured
```

`examples/ornek.cho` is a short original Turkish lyric (reference pack);
`examples/ornek.jsonl` holds nine validated records; `examples/ornek-brief.md`
is the rendered scientific brief. Read `SKILL.md` for the full record schema
and gate list.

## Install per harness

| Harness | Adapter | Mechanism |
|---|---|---|
| Claude Code | `adapters/claude-code/` | `UserPromptSubmit` hook + `description`; plugin + marketplace manifests |
| WorkBuddy | `adapters/workbuddy/` | skill package upload; explicit invocation recommended |
| OpenCode | `adapters/opencode/` | `AGENTS.md` instruction snippet |
| Any CLI / custom agent | `adapters/generic/` | paste-in system prompt |

**Automatic activation is a host capability, not a property of a markdown
file.** `activate.py` is the shared deterministic gate returning
`ACTIVATE / SKIP / ABSTAIN` with a reason, a nominated domain and a
`claim_limit`. It stays silent in hook mode unless it fires. WorkBuddy's public
Skills docs do not document description-based auto-invocation or hooks; the
relevant adapter says so explicitly instead of pretending.

See `adapters/README.md` for the full honesty boundary.

## Domains — chosen by the user, never guessed by the skill

`ontology.index.json` registers vocabularies as **data**. The engine contains
no domain words and **ships no default domain**: until the user confirms one
(`python domain.py use --ontology ...`), the vocabulary-free `generic` ontology
applies and every term/theory/mechanism link is refused (T9). `route` only
proposes a vocabulary (`MATCHED / NO_MATCH / ABSTAIN`); it never decides.

The example domains are **opt-in reference packs** under `examples/`. They
teach the record format and power the test suite; they are not knowledge the
skill asserts about your material.

| Domain | Terms | Theories | Note |
|---|---|---|---|
| `songwriting` | 11 | 9 | reference pack / worked example; verified bibliographic records |
| `literary-rhetoric` | 4 | 1 | second domain proving the engine is domain-agnostic |
| `physics` | 10 | 3 | worked example: simple pendulum (measurement + model + mechanism) |
| `psychology` | 7 | 3 | worked example: Stroop effect (human-behaviour material) |
| `generic` | 0 | 0 | honest default; observation-only, all links refused (T9) |

```bash
python domain.py use --ontology songwriting          # user confirms; recorded in domain.config.json
python domain.py use --ontology literary-rhetoric
python domain.py use --ontology /path/to/ontology.biology.json   # bring your own domain
python domain.py route --text "biomedical paper claims"   # -> NO_MATCH / generic
```

Adding a domain means adding one JSON file plus one index entry — no engine
changes. See `docs/ontology-authoring.md`.

## Commands

| Command | Purpose |
|---|---|
| `route --text` | **propose** a domain vocabulary (`MATCHED / NO_MATCH / ABSTAIN`); never decides |
| `attention --text [--dir] [--file]` | rank candidate domains with explainable weights (keywords, file NAMES, store continuity) — deterministic scoring, not a neural model |
| `use --ontology` | consent step: record the user's confirmed domain in `domain.config.json` |
| `activate.py --text` / `--hook` | deterministic activation gate |
| `ontology-check [--all]` | validate one or every registered vocabulary |
| `terms [--kind] [--id]` | list canonical terms/theories with sources and claim limits |
| `add --json [--profile P]` | validate then append one record (refuses, never repairs) |
| `check [--strict] [--profile P]` | re-validate a corpus; strict mode detects contradictory labels |
| `audit --notes` | nominate ungrounded notes (CANDIDATE, never findings) |
| `brief [--layered] [--render FILE]` | render the brief; `--layered` puts records needing work first |
| `schema` | emit the record schema as JSON Schema for external tooling |
| `evals/run.py` | static activation + CLI contract suite |

`--profile strict` (default) matches the original gate behaviour exactly.
`--profile research` / `--profile lite` are opt-in and only relax field-length
minimums (distinguishing test, theory link note); they never soften a gate that
protects the epistemic ladder (T1, T5, T6, T7, T8, T9).

## Citation honesty

Every source carries `ref`, `locator`, `kind`, `citation_status` and
`access_note`.

- `VERIFIED_BIBLIOGRAPHIC` — **the citation record was confirmed; the full text
  was not read and its findings were not reproduced here.**
- `PARTIAL` — incomplete bibliographic metadata (missing editors, page range…).
- `UNVERIFIED` — no locator verified; may only back a `CANDIDATE` link.

Theories without a `VERIFIED_BIBLIOGRAPHIC` source cap a link at `CANDIDATE`
(T6). Three shipped terms are `UNVERIFIED` and are labelled as such. Naming a
theory is an interpretation, not evidence that its effect occurred in the
material at hand.

## Quality boundary — what this project does not claim

- The unit tests validate the **validator**; the static eval suite validates a
  deterministic classifier and CLI artifacts. Neither proves a language model
  follows `SKILL.md` or produces better research.
- `eval-results.json` reports the live dual-arm (skill on/off) comparison as
  **`NOT_RUN`** until someone runs it. See `evals/README.md` for the protocol.
  The file is regenerated by every `evals/run.py` run and is not tracked.
- No full text of a cited source was read. No network call is made.
- Zero findings is a coverage statement, not success.

This honesty boundary is deliberate: it is the difference between a tool that
merely sounds rigorous and one whose claims can be checked.

## Project layout

```
PROTOCOL.md                  canonical instruction file: the 9-step procedure (start here)
SKILL.md                     legacy instruction file; kept for backward compatibility
build.py                     layer-first record builders (observation/term/theory/mechanism)
domain.py                    engine: gates G0-G11 / T1-T9, commands + --profile / --layered / schema
attention.py                 deterministic domain attention: ranked proposals with evidence
activate.py                  deterministic activation gate (+ hook mode)
ontology.index.json          domain registry (maps names to vocabulary files)
ontology.generic.json        vocabulary-free DEFAULT (until the user confirms a domain)
examples/                    OPT-IN reference packs:
                             ontology.songwriting.json, ontology.literary-rhetoric.json,
                             ornek.* worked example
examples/physics-pendulum/   worked example: simple pendulum (ontology, SYNTHETIC
                             measurements, records, sources, expected brief,
                             rejection cases)
examples/psychology-stroop/  worked example: Stroop effect (same pack layout)
tests.py                     112 unit tests
evals/                       19 activation + 13 contract + 28 adversarial cases,
                             structural grader, dual-arm instrument
adapters/                    Claude Code / WorkBuddy / OpenCode / generic
docs/ontology-authoring.md   how to add a domain
docs/quick-reference.md      one-page pocket card: layers, gates, commands
docs/rejection-examples.md   five common refusals and their fixes
```

## Contributing / security / license

`CONTRIBUTING.md`, `SECURITY.md`, MIT (`LICENSE`). Please keep the honesty
boundary intact: do not weaken a gate to make a case pass, do not add an
unsourced term, and do not upgrade `NOT_RUN` to a claim.
