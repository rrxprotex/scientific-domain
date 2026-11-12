# Scope — scientific-domain v1.0

Status: DRAFT for review. This document defines what "professional scope" means
for this project: who it serves, what ships, what is explicitly out of scope,
and what evidence we require before claiming it works.

## 1. Problem and positioning

**Problem.** AI agents produce knowledge claims (analyses, research notes,
literature summaries) that silently mix observation, classification,
interpretation and causation into one "finding". The result sounds rigorous and
is untrustworthy.

**Positioning.** scientific-domain is the **epistemic representation layer** for
AI knowledge work: a harness-agnostic skill + a dependency-free validator that
forces every claim onto the right rung of an evidence ladder, refuses invented
vocabulary and citations, and stamps every record with a claim limit.

One line: *"The rigor gate between what a source shows and what a discipline
calls it."*

## 2. Target users

| Priority | User | Job to be done |
|---|---|---|
| P0 | Individual researchers / analysts using agent harnesses | trustworthy research notes, literature-grounded analyses |
| P0 | Domain experts reviewing AI output | audit notes for overclaiming; a record format they can check |
| P1 | Teams (research groups, editorial, QA) | shared vocabulary + shared claim standard across members |
| P2 | Harness/marketplace users (Claude Code, WorkBuddy, OpenCode) | one-click install, deterministic activation |

## 3. In scope

1. **Core engine** (`domain.py`): gates G0–G11 / T1–T9, `--profile`, `schema`.
2. **Instruction protocol** (`PROTOCOL.md`): the 9-step procedure models follow.
3. **Ontology registry**: vocabularies as data; `generic` honest fallback (T9).
   v1.0 ships `songwriting` and `literary-rhetoric` as **opt-in reference packs
   under `examples/`** and the authoring guide for adding more. There is **no
   default domain**: the user confirms one (`use`), or generic applies.
4. **Activation gate** (`activate.py`): deterministic ACTIVATE/SKIP/ABSTAIN.
5. **Adapters**: Claude Code, WorkBuddy, OpenCode, generic prompt.
6. **Evaluation**: static suite (activation + contract + structural grader) and
   the honest reporting format (`NOT_RUN` until the dual-arm measurement exists).
7. **Worked example** (`ornek.*`) end-to-end validated.

## 4. Out of scope (v1.0)

- NLP/ML models, embeddings, semantic similarity of statements.
- Network calls, reference-manager integrations, DOI resolution.
- A hosted service or web UI. (Candidate for v2.)
- Claiming empirical listener/reader effects — the skill never measures; it
  grades what the material supports.
- Auto-repair of invalid records. Refusal is a feature.

## 5. Milestones

### M0 — Package hygiene (DONE, 2026-11-12)
- `domain_new.py` deleted after review: the draft dropped the G9 verdict-key
  gate, narrowed G6–G9 to the observation layer and raised NameError — see
  CHANGELOG 0.4.0. The tested monolithic `validate()` stays.
- Test-count references reconciled with reality (75 unit tests; 27 static
  eval cases).
- Debug leftover `.claude/settings.local.json` removed; `eval-results.json`
  documented as a regenerated, untracked snapshot (already in `.gitignore`).
- `git init` + initial commit + tag `v0.4.0`.

### M1 — Professional release surface (v1.0-rc)
- Single "first 10 minutes" path: install → activate → one record → brief.
- Versioned record schema (`schema` output) with a documented compatibility
  policy (what may change in a minor version).
- Two extra onboarding artifacts: (a) a 1-page quick-reference of the four
  layers + gates, (b) 5 common rejection examples with fixes (the errors real
  users will hit).
- CI badge + release checklist in CONTRIBUTING.

### M2 — Evidence of value (the missing measurement)
- Instrument READY: `evals/dualarm.py` runs the two arms (skill on / off),
  collects artifacts and grades them on rubric R1–R5, reporting the delta.
  Status stays `NOT_RUN` until someone configures a model command and runs it.
- Publish per-case artifacts and the delta, including a null result.
- Adversarial evaluation (DONE): `evals/adversarial.py`, 24 labelled attacks
  and controls; the suite already caught one real bug (greeting-disguised
  knowledge tasks were skipped).

### M3 — Growth (post-1.0, demand-driven)
- Third domain ontology authored by someone who is not the engine author
  (proves `docs/ontology-authoring.md` works).
- Team features: corpus merge rules, `CONTESTED` workflow, export formats.
- Hosted/API variant only if adoption justifies it.

## 6. Quality bar (release gates)

- All unit tests, ontology checks, strict example validation green on 3 OS ×
  Python 3.10–3.13 (already in CI).
- Honesty markers intact: `NOT_RUN` not silently upgraded; citation statuses
  never relaxed to pass a case (CI `honesty-gate` job).
- Every documented number (test counts, case counts) matches reality.
- No unsourced term in a shipped ontology.

## 7. Success metrics

| Metric | Target | How measured |
|---|---|---|
| Static suites | 100% pass | CI |
| Dual-arm delta (M2) | measured, honestly reported — not necessarily positive | dual-arm run |
| External ontology adoption | ≥ 1 domain authored outside core | registry |
| Rejection usefulness | common user errors covered by documented examples | issue tracker |

## 8. Risks

- **Over-activation**: a skill that fires on everything is ignored. Mitigated by
  negative triggers + ABSTAIN; keep grading this in `cases.json`.
- **Rigor theater**: gates that look strict but measure nothing. Mitigated by
  the dual-arm eval and the honesty gate.
- **Ontology drift**: vocabularies grow unsourced. Mitigated by `ontology-check`
  and the authoring rule: "an unsourced vocabulary is worse than none".
- **Harness churn**: adapters break when hosts change contracts. Keep adapters
  thin; the engine is the product.

## 9. Decisions (RESOLVED 2026-11-12)

| # | Decision | Resolution |
|---|---|---|
| D1 | Product form | **Public open-source skill**: MIT, adapter-shipped for every harness (Claude Code, WorkBuddy, OpenCode, generic prompt) |
| D2 | Primary user | **Everyone in knowledge work**: researcher-first docs, plus `docs/quick-reference.md` for experts and `docs/rejection-examples.md` for practitioners |
| D3 | Languages | **Multilingual reach**: English docs; activation + routing signals in EN, TR, DE, ES/PT/IT/FR, RU (graded in `evals/cases.json`); example material may be any language |
| D4 | Domain strategy | **Domain-agnostic core with 2 worked domains + honest `generic` fallback**; new domains added as data, demand-driven |
| D5 | Dual-arm eval | **Committed before any benefit claim** (M2); until it runs, `NOT_RUN` stays visible |
| D6 | `domain_new.py` | **Deleted** — review found dropped gates (G9) and NameErrors; differs from the proposed default because merging would have weakened the epistemic ladder |
| D7 | Who chooses the expertise domain? | **The user, explicitly** (2026-11-12). Routing only proposes; `use` records the confirmation; no domain data ships as a default — example ontologies are opt-in reference packs under `examples/` |
| D8 | "Attention mechanism" for domain determination | **Deterministic weighted attention** (`attention.py`, 2026-11-12), not neural: explainable weights over keywords, material file NAMES and store continuity; ranked proposals with evidence; `user_confirmation_required` always true. Chosen because the project forbids ML dependencies and an unexplainable scorer would break the honesty boundary |
