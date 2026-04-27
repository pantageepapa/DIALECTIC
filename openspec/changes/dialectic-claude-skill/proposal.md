## Why

DIALECTIC is a published research system for startup investment analysis, but running it requires navigating LangGraph Studio, multiple API keys, and Python setup. There's no way for Claude Code users to just use it. Adding a `/dialectic` Claude Code skill with a one-liner install makes the system accessible to anyone — clone, fill in two API keys, and type `/dialectic`.

## What Changes

- **New**: `SKILL.md` at repo root — the `/dialectic` Claude Code skill definition
- **New**: `src/agent/cli.py` — CLI entry point that accepts company info as args, runs the LangGraph pipeline, and outputs structured JSON
- **New**: `setup` — executable shell script that installs deps and creates `.env` from example
- **Updated**: `README.md` — one-liner install prompt as primary path, LangGraph Studio demoted to "advanced"

## Capabilities

### New Capabilities

- `dialectic-skill`: The `/dialectic` Claude Code skill — conversational intake (company name, description, industry, website, extra info, output verbosity), runs the LangGraph pipeline via CLI, presents pro/con arguments and investment recommendation
- `cli-entrypoint`: `src/agent/cli.py` — thin wrapper that accepts company data as CLI args, runs `graph.ainvoke()`, and outputs structured JSON for the skill to consume
- `one-liner-install`: `setup` script + `SKILL.md` at repo root enabling `git clone ... ~/.claude/skills/dialectic && ./setup` global install pattern

### Modified Capabilities

## Impact

- `src/agent/` — adds `cli.py`, no changes to existing pipeline code
- `SKILL.md` — new file at repo root
- `setup` — new executable at repo root
- `README.md` — restructured, install instructions updated
- No changes to LangGraph graph, prompts, or pipeline stages
- Requires `uv` on user's machine (setup script checks/installs it)
