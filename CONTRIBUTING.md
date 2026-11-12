# Contributing

## Standing rules

1. **Never weaken a gate to make a case pass.** If a change legitimately
   requires editing an assertion, state exactly what the old assertion pinned
   and why the new form is not looser.
2. **Every new gate needs a test that fails without it.** Gate identifiers
   (`G0`–`G11`, `T1`–`T9`) appear in the refusal message so a test can assert
   the specific gate fired.
3. **No invented terminology and no invented citations.** A new term or theory
   must carry `sources` with `ref`, `locator`, `kind`, `citation_status` and
   `access_note`. If only a search excerpt was seen, say so.
4. **Keep the honesty boundary.** Do not change `NOT_RUN` to `RUN`, do not
   describe a bibliographic check as a full-text read, and do not claim a
   live-model improvement without a dual-arm run.
5. **No new dependency.** Python 3.10+ standard library only. No network on
   core paths. No mandatory API key.

## Before opening a PR

```bash
cd scientific-domain
python tests.py                    # 113 tests
python domain.py ontology-check --all
python evals/run.py                # 32 static cases
python evals/semantic.py           # 8 structural grader cases
python domain.py check --ontology songwriting --file examples/ornek.jsonl --strict
python domain.py brief --ontology songwriting --file examples/ornek.jsonl
```

CI runs the same checks on Ubuntu, Windows and macOS with Python 3.10–3.13.

## Adding a domain

1. Write `ontology.<domain>.json` — see `docs/ontology-authoring.md`.
2. Add an entry to `ontology.index.json` with routing keywords and a
   `citation_status`.
3. Run `python domain.py ontology-check --all`.
4. Add at least one record example and one test proving the engine behaves the
   same in the new domain.
5. If the vocabulary has no sourced terms, use the `generic` fallback instead.
   **An unsourced vocabulary is worse than no vocabulary.**

## Adding an activation case

Add to `evals/cases.json`: `id`, `prompt`, `expect`, `expect_domain` and `why`.
Write the label **before** running the classifier. Include negative cases:
over-triggering is a defect, not a feature. For CLI behaviour add a case in
`evals/run.py::contract_cases()` that drives the real command and grades its
exit code and output.

## Reporting a defect

Include the exact command, the record JSON (with any credentials removed), the
expected gate and the observed message. A defect where a validator silently
repairs or upgrades a claim is more serious than a defect where it refuses.
