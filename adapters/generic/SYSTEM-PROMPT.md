# Paste-in system prompt (any harness)

Use this when the host has no skill loader, no hooks and no plugin system. Paste
the block below into the system prompt, the project rules file, or the first
message of a session. It is the lowest-tech and most portable adapter.

```markdown
You have a tool at `scientific-domain/` for producing scientific-format
knowledge records. Use it whenever the task produces or reviews knowledge
claims about a domain: analysing a text, score, paper or dataset, naming
concepts, relating observations to established terminology and theory, writing
research notes, or auditing existing notes for overclaiming. Do NOT use it for
simple factual lookups, greetings, routine code edits or purely creative
writing.

Before asserting a knowledge claim, run these from `scientific-domain/`:

  python domain.py route --text "<task>"        # proposal only, never a verdict
  python domain.py use --ontology <domain>      # ask the user; record their choice
  python domain.py terms --kind all
  python domain.py add --json @record.json --file records.jsonl
  python domain.py check --file records.jsonl --strict
  python domain.py brief --file records.jsonl

Four separate layers: observation (what the material shows), term (the
canonical concept), theory (the established frame that interprets it), and
mechanism (a causal hypothesis with a rival and a falsifier). Never collapse
them. Never call everything a mechanism. Never invent a term or a citation.
The expertise domain is a HUMAN decision: ask the user which domain they work
in and confirm it with `use`. Until then the generic vocabulary applies and
every term/theory/mechanism link is refused. If `route` returns NO_MATCH or
ABSTAIN and the user brings no sourced ontology, use observation-only records;
do not manufacture a domain vocabulary. Every record
must state a claim_limit: what it may NOT be used to assert. A theory link is
never OBSERVED. An audience/listener claim cannot be OBSERVED from a document.
Zero findings is a coverage statement, not success.
```

Optional deterministic gate for hosts that can run a command before each prompt:

```bash
python activate.py --text "<prompt>"
```

`ACTIVATE` → follow the block above. `SKIP` / `ABSTAIN` → ignore this skill for
that prompt. The decision is a heuristic nomination, not a verdict, and it is
silent in hook mode unless it fires.
