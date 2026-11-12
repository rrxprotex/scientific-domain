# Harness adapters — automatic activation

**Automatic activation is a host capability, not a property of `SKILL.md`.**
This package ships a host-independent engine (`domain.py` + ontologies) and thin
adapters. Choose the one for your harness; do not edit the core.

| Harness | Adapter | Mechanism | Deterministic? |
|---|---|---|---|
| Claude Code | `claude-code/` | `UserPromptSubmit` hook + `description` | hook: yes; description: no |
| WorkBuddy | `workbuddy/` | installed skill package; optionally a project instruction line | not documented as automatic |
| OpenCode | `opencode/` | `AGENTS.md` / instruction snippet | depends on the harness |
| Any CLI / prompt | `generic/` | paste-in system prompt line | n/a (manual) |

## The shared activation gate

All adapters can call the same deterministic, model-free classifier:

```bash
python activate.py --text "Analyze this lyric and relate it to theory"
```

It returns `ACTIVATE / SKIP / ABSTAIN`, a `domain`, the resolved `ontology`, a
`reason` and a `claim_limit`. `ABSTAIN` is a first-class outcome. Negative
triggers keep it off simple factual questions, greetings, routine edits, git
commands and purely creative writing.

In hook mode (`--hook`) it reads `{ "prompt": "..." }` from stdin and stays
**completely silent** unless it fires.

## What is NOT promised

- WorkBuddy's public Skills documentation describes installed skills as
  "directly invoked in conversations" and describes **discovery** via Find Skills;
  it does not document description-based automatic invocation, hooks, or exact
  filesystem paths. Treat WorkBuddy auto-activation as unconfirmed.
- OpenCode's exact skill/hook contract is not verified here; the adapter is an
  instruction snippet, not a config file that a harness has been observed to load.
- A perfect static eval score does not prove a model reads the skill, fires it,
  or produces better research. See `evals/README.md`.
