# Quick reference — one page

Read `PROTOCOL.md` for the full procedure. This page is the pocket card.

## Which layer does my sentence belong to?

```
Does it state a CAUSE ("X increases Y", "leads to", "because")?
  yes -> mechanism   (HYPOTHESIS + rivals + falsifier + term/theory anchor)
  no  -> Does it NAME a canonical concept from the ontology?
           yes -> term   (INFERRED/CANDIDATE + declared rival + distinguishing test)
           no  -> Does it APPLY an established theory to the observation?
                    yes -> theory (INFERRED/HYPOTHESIS/CANDIDATE - never OBSERVED)
                    no  -> observation (OBSERVED + artifact_site + locator)
```

When in doubt, write the observation first. The other layers may be added
later; a collapsed sentence cannot be un-collapsed.

## The four layers

| Layer | May claim | Never | Requires |
|---|---|---|---|
| `observation` | `OBSERVED` / `PRESENT` | causation, classification | `scope.sources` + `artifact_site` with `locator` |
| `term` | `INFERRED` / `CANDIDATE` | interpretation, causation | `term_id` + `rival_term_ids` + `distinguishing_test` |
| `theory` | `INFERRED` / `HYPOTHESIS` / `CANDIDATE` | `OBSERVED` | `theory_ids` + `theory_link_note` + citation status |
| `mechanism` | `HYPOTHESIS` (or `OBSERVED` with intervention) | a cause without rivals | `mechanism.rivals` + `mechanism.falsifier` |

## The epistemic ladder

`OBSERVED` → measured/seen · `CANDIDATE` → plausible, citation not verified ·
`INFERRED` → follows from the observation · `HYPOTHESIS` → causal proposal ·
`DOCUMENTED_CLAIM` → the source says it itself · `UNVERIFIED_CLAIM` → asserted,
uncertain (`uncertainty_reason` required).

**Caps:** a theory link is never `OBSERVED` (T5). A theory without a
`VERIFIED_BIBLIOGRAPHIC` source is capped at `CANDIDATE` (T6). An
`EXTERNAL_SUBJECT` claim (listener, reader) is never `OBSERVED` from a document.

## Gates at a glance

| Tag | Refusal |
|---|---|
| G0–G5 | missing fields, no scope, no claim limit, bad evidence rows |
| G3 | `NOT_REPRESENTED` without declared scope |
| G6–G9 | `OBSERVED` beyond what the evidence class admits; `DOCUMENTED_CLAIM` without `source_mention`; `CANDIDATE` carrying verdict keys |
| G10–G11 | credential-shaped strings; wrong ontology for the named domain |
| T1 | invented term / theory id |
| T2 | causation or links smuggled into the wrong layer |
| T3–T4 | term without canonical id, without declared rival, without distinguishing test |
| T5–T6 | theory as `OBSERVED`; uncited theory above `CANDIDATE` |
| T7–T8 | mechanism without causal wording, rivals or falsifier; ungrounded mechanism |
| T9 | vocabulary-free (`generic`) domain used to link terms/theories/mechanisms |

## Commands

```bash
python activate.py --text "<prompt>"            # ACTIVATE / SKIP / ABSTAIN?
python domain.py route --text "<prompt>"        # propose a vocabulary (never decides)
python domain.py attention --text "<prompt>" --dir .   # ranked domains + evidence (deterministic weights)
python domain.py use --ontology <domain>        # consent: the user confirms the domain
python domain.py --ontology <domain> terms --kind all   # read before naming
python domain.py add --json @record.json --file store.jsonl
python domain.py check --file store.jsonl --strict
python domain.py brief --file store.jsonl --layered
python domain.py audit --notes notes.md --file store.jsonl
python domain.py schema                          # JSON Schema for tooling
```

`--profile strict` (default) is the rigorous path; `research` / `lite` only
relax field-length minimums. The validator refuses; it never repairs.

## Non-negotiables

1. **No default domain.** The user confirms the expertise domain (`use`); until
   then `generic` applies and every term/theory/mechanism link is refused (T9).
   `attention` only ranks candidates with explainable weights — never a verdict.
2. Zero findings is a coverage statement, not success.
3. Absence is always scoped ("this file has no X", never "the field lacks X").
4. Naming a theory is an interpretation, not evidence that its effect occurred.
5. A verified bibliographic record means the citation exists — the full text was
   not read.
