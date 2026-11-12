# WorkBuddy adapter

> Based on the public WorkBuddy Skills documentation retrieved 2026-11-09. That
> page documents installation and manual invocation; it does **not** document
> `SKILL.md`, exact filesystem paths, hooks, or description-based automatic
> model invocation. Treat "automatic" here as unconfirmed.

## Install

1. Open the Skills panel, choose **Add Skill → Upload Skill**, select the
   `scientific-domain/` folder packaged as a skill package.
2. The upload undergoes a security check. Non-high-risk installs continue
   automatically; high-risk ones require manual confirmation.
3. After import the configuration is completed automatically. Uploaded or
   created skills are stored in the user configuration directory and are
   **available to all projects**. To limit it to one project, place it in that
   project's skills directory instead.

The Skills panel also offers **Find Skills**: enter a task description and
WorkBuddy will look for relevant skills. Installed skills can be disabled and
re-enabled at any time; disabled skills are not invoked.

## What is confirmed vs not

| Claim | Status |
|---|---|
| Installed skills can be directly invoked in conversations | documented |
| Uploaded/created skills are visible to all projects by default | documented |
| Project skills directory limits visibility to one project | documented |
| Exact path of the user config / project skills directory | **not given** in the docs |
| `SKILL.md` frontmatter requirements | **not mentioned** in the docs |
| Automatic invocation from a `description` field | **not documented** |
| Hooks (`SessionStart` / `UserPromptSubmit`) | **not documented** |

Practical consequence: for WorkBuddy, do not rely on the `description` alone.
Either invoke the skill explicitly, or add the always-loaded instruction line
from `adapters/generic/SYSTEM-PROMPT.md` to the project's instruction file.

## Deterministic activation regardless of host

The engine itself is plain Python and does not depend on any harness:

```bash
cd scientific-domain
python activate.py --text "Analyze this lyric and relate it to theory"
python domain.py ontology-check --all
python domain.py terms --kind all
python evals/run.py
```

`activate.py --hook` is included for hosts that support command hooks, but
WorkBuddy's public documentation does not describe such a mechanism. Do not
ship a claim that it is wired up until it has been observed working.
