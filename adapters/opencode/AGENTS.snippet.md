# OpenCode / AGENTS.md snippet

Append the following block to the instruction file your harness actually reads
(`AGENTS.md`, `.opencode` instructions, or an equivalent project rules file).
This is a **paste-in instruction**, not a config file a harness has been
observed to auto-load; verify it against your OpenCode version.

```markdown
## Scientific knowledge claims

When a task produces or reviews knowledge claims about any domain (analysing a
text, score, paper, dataset or artifact; naming concepts; relating observations
to established terminology or theory; writing research notes; auditing notes for
overclaiming), load `scientific-domain/SKILL.md` and use its CLI before asserting
anything.

Run from the `scientific-domain/` directory:

- `python domain.py route --text "<task>"` — propose a domain vocabulary; it
  never decides. `NO_MATCH` / `ABSTAIN` mean: do NOT invent canonical terms.
- `python domain.py use --ontology <domain>` — the consent step: ask the user
  which expertise domain they work in and record their confirmation. Until it
  exists, the generic vocabulary applies and every link is refused.
- `python domain.py terms --kind all` — read the canonical vocabulary first.
- `python domain.py add --json @record.json --file records.jsonl` — validate a
  record before storing it.
- `python domain.py check --file records.jsonl --strict` and
  `python domain.py brief --file records.jsonl` — verify and present.

Hard rules: an observation is not a mechanism; a theory link is never OBSERVED;
no term or citation may be invented; the expertise domain is the user's
decision, never a guess; every record carries a claim_limit stating
what it cannot assert. Simple factual questions, routine edits and creative
writing do not need this skill.
```

## Deterministic option

If your harness supports command hooks, use `activate.py` as the gate:

```bash
python activate.py --text "<prompt>"     # ACTIVATE / SKIP / ABSTAIN + domain
python activate.py --hook                # stdin JSON, silent unless ACTIVATE
```

An `ABSTAIN` means no knowledge-work signal was found. Do not coerce it into
`ACTIVATE` to make the skill look useful.
