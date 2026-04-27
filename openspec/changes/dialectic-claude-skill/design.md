## Context

DIALECTIC's LangGraph pipeline runs end-to-end via `asyncio.run(main())` in `graph.py`, using a hardcoded `BRANDBACK_COMPANY` example. The `display_results()` function prints verbose iteration history to stdout. There is no CLI interface.

Claude Code skills are markdown files (`SKILL.md`) in `~/.claude/skills/<name>/`. They instruct Claude on what to do when a slash command is invoked. Skills can run shell commands via Bash. The gstack project established the pattern: clone to `~/.claude/skills/<name>`, run `./setup`, update `CLAUDE.md`.

## Goals / Non-Goals

**Goals:**
- `/dialectic` available globally after one clone + setup command
- Skill gathers company info conversationally, runs the pipeline, presents clean output
- User can choose summary (default, recommended) or detailed (full iteration history)
- Zero changes to the existing LangGraph pipeline code

**Non-Goals:**
- Rewriting the pipeline to use Claude SDK or any other framework
- Web search is kept as-is (required, not optional)
- No streaming/live progress during pipeline execution
- No persistent storage of analyses

## Decisions

**Decision 1: SKILL.md at repo root, not nested in `.claude/skills/`**

When cloned to `~/.claude/skills/dialectic/`, Claude Code expects `SKILL.md` at that directory's root. The entire repo becomes the skill package — `SKILL.md` + Python backend co-located. Alternative (separate skills repo) would require maintaining two repos.

**Decision 2: cli.py outputs JSON, skill formats output**

`cli.py` outputs structured JSON (final_arguments with scores/types, final_decision). The skill instructs Claude to parse and present it. Alternative (cli.py outputs formatted text) would make the skill's output rigid. JSON lets Claude format conversationally and respect the user's verbosity choice.

JSON schema:
```json
{
  "company": "string",
  "final_decision": "invest | not_invest",
  "final_arguments": [
    {"type": "pro|contra", "content": "string", "refined_content": "string|null", "score": 0.0}
  ],
  "arguments_history": [...],
  "iterations_completed": 2
}
```

**Decision 3: Verbosity choice — ask upfront, recommend summary**

The skill asks "Would you like a summary or the full analysis? (recommended: summary)" before running. This avoids post-hoc reformatting and sets expectations. Summary = top 3 pro + top 3 contra + recommendation paragraph. Detailed = full iteration history with critiques and refinements.

**Decision 4: setup script installs uv if missing**

`uv` is the project's package manager. Setup checks `which uv`, installs via `curl` if absent (official uv installer), then runs `uv sync`. Alternative (require uv pre-installed) adds friction. Alternative (use pip) loses lockfile reproducibility.

**Decision 5: Skill uses absolute path to python via uv**

Skill runs: `cd ~/.claude/skills/dialectic && uv run python -m agent.cli --name "..." ...`

This is portable across machines — `uv run` uses the project's `.venv` regardless of shell's active Python. The `--project` flag is an alternative but `cd` + `uv run` is simpler and more readable in the skill markdown.

## Risks / Trade-offs

- **Long runtime** → Pipeline takes 2-5 minutes. The skill should warn the user upfront: "This analysis takes a few minutes. Starting now..."
- **API key errors** → If OPENAI_API_KEY or search key is missing, cli.py will fail mid-run. cli.py should validate keys at startup before the graph runs and exit with a clear message.
- **openspec skills in public repo** → `.claude/skills/` contains openspec skills (explore, propose, etc.). These will be visible in the public repo but won't activate unless openspec CLI is installed. Low risk, but worth noting in README.
- **SKILL.md at root looks unusual** → First-time contributors may not understand why there's a `SKILL.md` at repo root. A comment in README explains it.

## Migration Plan

No migration needed — purely additive. Existing LangGraph Studio workflow is unchanged.

Deploy order:
1. Add `cli.py` + tests
2. Add `SKILL.md` + `setup`
3. Update `README.md`
4. Tag release

## Open Questions

- What's the GitHub repo URL for the one-liner? (`pantageepapa/DIALECTIC` — confirm this is the public repo name)
- Should `setup` also update `~/.claude/CLAUDE.md` automatically (like gstack's prompt suggests), or leave that to the user's Claude Code session?
