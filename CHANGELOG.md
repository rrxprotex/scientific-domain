# Changelog

## [0.7.0] - 2026-11-12

Adversarial scientific evaluation + the dual-arm instrument. Directly answers
the "prove the gates hold under attack" and "prove the skill helps" gaps.

### Added
- `evals/adversarial.py` + `evals/adversarial.json`: 24 labelled cases written
  before the runner - 15 attack records that must be REFUSED with the named
  gate (fabricated term/theory, unverified-citation promotion, hidden
  causality, ungrounded mechanism, theory-as-observed, scope-less absence,
  credential string, verdict-smuggling, listener-claim-as-observed, T9
  vocabulary forgery, rival-less term, source-less DOCUMENTED_CLAIM, smuggled
  link), 4 control records that must be ACCEPTED, and 5 attack prompts
  (greeting disguise, prompt injection, shouting/emoji, word repetition,
  causal-question phrasing). Writes `adversarial-results.json`.
- `evals/dualarm.py`: the dual-arm benchmark instrument behind
  `liveModelDualArm`. Without a model command it reports NOT_RUN (the shipped
  state); with `--on`/`--off` arms and a `--judge` it grades artifacts on the
  fixed rubric R1-R5 and reports the DELTA between arms.
- CI runs the adversarial suite.

### Fixed
- Activation: a knowledge task prefixed by a greeting ("merhaba, bu şarkıyı
  analiz et") was wrongly SKIPped. Greetings now only win when no knowledge-work
  signal is present. Found by the adversarial probe (ADVP-001), proving the
  method earns its place.

## [0.6.1] - 2026-11-12

Packaging fix, no code change. The `v0.6.0` commit tree accidentally carried
both layouts: the moved `examples/` reference packs AND their stale root copies
(the staging happened before the move). This release removes the five stale
root copies so the shipped tree has exactly one layout. History is not
rewritten; this entry records what happened, as the honesty boundary requires.

## [0.6.0] - 2026-11-12

Domain attention: a system that determines which expertise domain a task
attends to - with evidence, and without ever deciding.

### Added
- `attention.py` + `python domain.py attention --text [--dir] [--file]`:
  deterministic weighted scoring over registry data. Three signal families per
  candidate domain: keyword hits (longer keywords weigh more), material-type
  FILE NAMES in the working directory (`material_hints` per domain in
  `ontology.index.json`; contents are never read), and store continuity
  (domains already present in the record store). Returns ranked `attention`
  shares, the matched `evidence`, a `confidence` band (gap-based), and
  `user_confirmation_required: true` - it is a proposal engine, not a neural
  model and not a verdict.
- `route` output now embeds the attention scores as an explanation overlay.
- `material_hints` data field in `ontology.index.json` (per domain).
- 5 unit tests (ranking, tie -> ABSTAIN, no-signal -> NO_MATCH, material-name
  evidence, store continuity) and 1 eval contract case (CON-011): 84 unit
  tests, 30 static cases.

## [0.5.0] - 2026-11-12

Consent-based domain selection. The skill ships **no domain knowledge as a
default**: the expertise domain is a user decision, recorded explicitly.

### Added
- `python domain.py use --ontology <domain>`: the consent step. Records the
  user's confirmed domain in `domain.config.json` (written only by this command;
  routing never writes it). Resolution order: explicit `--ontology` >
  user-confirmed selection > `generic`.
- `route` output now carries `user_confirmation_required: true` and states that
  a MATCHED result is a proposal, never a verdict.
- 4 unit tests (consent flow) and 2 eval contract cases (CON-009: a term link is
  refused before the domain is confirmed (T9); CON-010: `use` records the choice
  and `add` then works without a flag): 79 unit tests, 29 static cases.

### Changed
- **No shipped default domain.** `DEFAULT_ONTOLOGY` (a domain word in engine
  code) is gone; without confirmation the vocabulary-free `generic` ontology
  applies and every term/theory/mechanism link is refused (T9). This makes the
  "engine contains no domain words" claim fully true.
- Example vocabularies and the worked example moved to `examples/` as **opt-in
  reference packs** (`examples/ontology.songwriting.json`,
  `examples/ontology.literary-rhetoric.json`, `examples/ornek.*`). They teach
  the record format and power the test suite; they are never auto-loaded.
- `build.py` builders default to `domain_name="generic"`.
- Docs (PROTOCOL step 2, SKILL, README, quick-reference, ontology-authoring,
  CI) updated to the consent flow; test/eval counts reconciled (79 / 29).

## [0.4.0] - 2026-11-12

Public prestige release: multilingual reach, documented rejections, clean
package. All decisions recorded in `SCOPE.md`.

### Added
- Multilingual activation and routing surface forms: knowledge-work signals in
  EN, TR, DE, ES/PT/IT/FR and RU, plus multilingual greetings and negative
  triggers in `activate.py`; routing keywords for `songwriting` and
  `literary-rhetoric` in Spanish, French, German, Italian/Portuguese and
  Russian (`ontology.index.json`). Five new graded activation cases (ACT-015 to
  ACT-019): 19 activation + 8 contract = 27 static cases.
- `docs/quick-reference.md`: one-page pocket card (layer decision tree,
  epistemic ladder, gates, commands).
- `docs/rejection-examples.md`: the five refusals a new user hits first, with
  the gate tag and the fix.

### Changed
- Test and case counts in README, PROTOCOL.md, SKILL.md, CONTRIBUTING.md and
  evals/README.md reconciled with reality (75 unit tests; 27 static cases).
  Five unit tests shipped late in 0.3.0 were unlogged until now.
- `eval-results.json` documented as a regenerated, untracked snapshot.
- SKILL.md version metadata aligned with the changelog.

### Removed
- `domain_new.py`, an unmerged and untested draft of a layered `validate()`
  refactor. Review showed it drops the G9 verdict-key gate, narrows G6-G9 to
  the observation layer, and raises NameError on undefined `terms`/`theories`.
  The tested monolithic `validate()` in `domain.py` is the supported engine.
- Debug leftover `.claude/settings.local.json`.

## [0.3.0] - 2026-11-11

### Added
- `PROTOCOL.md`: canonical instruction file giving the model a 9-step,
  procedural protocol (route → observation → term → theory → mechanism →
  claim limits → validate → coverage) with a full worked example, instead of
  a schema reference. `SKILL.md` is kept for backward compatibility and now
  points to PROTOCOL.md.
- `build.py`: layer-first record builders (`observation`, `term`, `theory`,
  `mechanism`) that set correct per-layer defaults and refuse structurally
  invalid records instead of inventing placeholder content.
- `--profile strict|research|lite` on `add`/`check`: opt-in profiles that only
  relax field-length minimums (distinguishing test, theory link note). The
  default `strict` profile matches the previous gate behaviour exactly; no
  epistemic gate (T1, T5, T6, T7, T8, T9) is ever softened.
- `brief --layered`: two-pass report listing records needing work before the
  approved ones. `brief --render FILE`: write the brief to a file.
- `schema` command: emits the record schema as JSON Schema for external tooling.
- 10 new unit tests (builders + profiles): 70 total.

All notable changes are documented here. Format follows Keep a Changelog;
versions follow Semantic Versioning.

## [0.2.0] - 2026-11-09

Public-package readiness release. 59 unit tests, 22 static eval cases.

### Added — portable packaging and automatic activation

- `SKILL.md` rewritten with a universal, English `description` containing broad
  positive and explicit negative triggers. Vendor-specific Claude Code fields
  were removed from the instruction file and moved into `adapters/`.
- `adapters/`: Claude Code (`plugin.json`, `marketplace.json`, `hooks.json`),
  WorkBuddy, OpenCode and plain system-prompt adapters. `adapters/README.md`
  states plainly which hosts document automatic invocation and which do not.
- `activate.py`: deterministic, model-free `ACTIVATE / SKIP / ABSTAIN` gate with
  a reason, nominated domain and `claim_limit`. Hook mode reads
  `{"prompt": ...}` from stdin and stays silent unless it fires.
- `evals/`: 14 hand-labelled activation cases + 8 CLI contract cases, a
  dependency-free runner and `eval-results.json`. The live dual-arm model
  comparison is explicitly `NOT_RUN`.
- `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`, `SECURITY.md`,
  `docs/ontology-authoring.md`, `.gitignore`, and a CI workflow running
  tests + ontology checks + evals across 3 operating systems and
  Python 3.10–3.13.

### Added — domain registry (the "any expertise" fix)

- `ontology.index.json` maps domain keywords → vocabulary files. `--ontology`
  now accepts a registered domain name as well as a file path.
- `route --text` nominates a domain with `MATCHED / NO_MATCH / ABSTAIN`. An
  ambiguous signal abstains instead of guessing.
- `ontology.generic.json`: zero terms, zero theories — the honest fallback.
  Gate **T9** refuses all term/theory/mechanism links against it, while
  observation-only records from any domain remain valid.
- `ontology.literary-rhetoric.json`: a second, small domain with 4 terms and 1
  theory, proving the engine contains no domain-specific words.
- `ontology-check --all` validates every registered vocabulary.

### Added — consistency

- `check --strict` detects `CONTESTED` records: the same statement carrying
  conflicting `evidence_status` / `representation` labels.
- `tests.py` grew from 36 to 59 tests, covering routing, the generic fallback,
  activation decisions, hook behaviour and strict consistency.

### Changed

- Default ontology remains `songwriting` for backward compatibility: the
  shipped nine-record example still validates unchanged.
- Activation and routing decisions now always carry a `claim_limit` stating
  they are heuristic nominations, not verdicts.

### Fixed

- `brief` printed `UNKNOWN` / `NOT_REPRESENTED` records a second time in an
  "Unknown / absent" section, so one record looked like two findings. That
  section is now a coverage summary listing only ids; a regression test asserts
  every statement appears exactly once. Test count 59 → 60; evals remain 22/22.

### Not changed / deliberately absent

- No full text of any cited source was read; `VERIFIED_BIBLIOGRAPHIC` still
  means "citation record confirmed, findings not reproduced".
- No network call, no API key, no third-party dependency.
- No proof of live-model benefit. `NOT_RUN` is not upgraded to a claim.

## [0.1.0] - 2026-11-09

First working version: the four-layer record model (observation / term /
theory / mechanism), gates G0–G11 and T1–T8, the songwriting ontology with 11
terms and 9 theories, 36 unit tests, and a nine-record worked example on an
original Turkish lyric. Domain vocabulary was hardcoded to songwriting and the
skill had no activation mechanism — both fixed in 0.2.0.
