# Claude Code adapter (template)

Three files here are **templates**, not an installed plugin. Adjust paths and
verify against your installed Claude Code version before publishing.

## Expected plugin layout

```
<plugin-root>/
├── .claude-plugin/
│   ├── plugin.json          <- from adapters/claude-code/plugin.json
│   └── marketplace.json     <- from adapters/claude-code/marketplace.json
├── hooks/
│   └── hooks.json           <- from adapters/claude-code/hooks.json
└── skills/
    └── scientific-domain/   <- copy the WHOLE package folder here
        ├── SKILL.md
        ├── domain.py
        ├── activate.py
        ├── ontology.index.json
        ├── ontology.*.json
        └── evals/
```

`plugin.json` declares `"skills": ["./skills/scientific-domain"]`, and the hook
calls `$CLAUDE_PLUGIN_ROOT/skills/scientific-domain/activate.py`. If you install
the package somewhere else, change both paths consistently.

## What each mechanism does

- **`description` in `SKILL.md`** — model-invoked skill selection. Broad positive
  triggers, explicit negative triggers. This is a model decision, not a
  deterministic one.
- **`hooks/hooks.json`** — deterministic `UserPromptSubmit` gate. The hook reads
  the prompt JSON from stdin, runs `activate.py --hook`, and prints
  `hookSpecificOutput.additionalContext` only on `ACTIVATE`. On `SKIP` /
  `ABSTAIN` it prints nothing, so ordinary prompts cost zero context.
- **`activate.py`** — the classifier itself. It also routes the domain via
  `ontology.index.json` and always emits a `claim_limit` stating that its
  decision is a heuristic nomination.

## Verify before trusting

```bash
# deterministic gate: silent on a routine edit
echo '{"prompt":"fix a typo in the readme"}' | python activate.py --hook

# deterministic gate: injects context on a knowledge task
echo '{"prompt":"Analyze this lyric and relate it to theory"}' | python activate.py --hook

# full static suite
python tests.py && python evals/run.py
```

The hook output shape (`hookSpecificOutput` / `additionalContext`) follows the
Claude Code plugin hook convention. It is not documented in WorkBuddy's public
Skills docs, and OpenCode does not read this file at all — use the matching
adapter there.

**Honesty boundary:** a hook firing is not proof that the model followed the
skill, nor that the research improved. `eval-results.json` reports the live
dual-arm model comparison as `NOT_RUN` until someone runs it.
