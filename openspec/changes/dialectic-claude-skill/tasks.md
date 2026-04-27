## 1. CLI Entrypoint

- [x] 1.1 Create `src/agent/cli.py` with argparse for `--name`, `--about`, `--industry`, `--website`, `--extra`
- [x] 1.2 Add startup validation: check `OPENAI_API_KEY` and at least one search key, exit with clear error if missing
- [x] 1.3 Build `Company` object from CLI args and run `graph.ainvoke()` with `max_iterations=2`, `n_pro_arguments=3`, `n_contra_arguments=3`
- [x] 1.4 Serialize final state to JSON and print to stdout (company, final_decision, final_arguments with type/content/refined_content/score, arguments_history, iterations_completed)
- [x] 1.5 Catch exceptions, print to stderr, exit with code 1

## 2. SKILL.md

- [x] 2.1 Create `SKILL.md` at repo root with frontmatter (name, description)
- [x] 2.2 Write intake flow: ask for name, what it does, industry, website/extra, verbosity preference (summary recommended)
- [x] 2.3 Write pre-run warning message ("This analysis takes 2-5 minutes...")
- [x] 2.4 Write Bash invocation: `cd ~/.claude/skills/dialectic && uv run python -m agent.cli --name "..." ...`
- [x] 2.5 Write summary output instructions: top 3 pro, top 3 contra, final decision, recommendation paragraph
- [x] 2.6 Write detailed output instructions: full iteration history with critiques and refinements
- [x] 2.7 Write error handling instructions: check `.env`, suggest API key fix

## 3. Setup Script

- [x] 3.1 Create `setup` at repo root (bash script, `chmod +x`)
- [x] 3.2 Add uv check: if not found, install via `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [x] 3.3 Run `uv sync` to install Python dependencies
- [x] 3.4 Copy `.env.example` to `.env` if `.env` does not exist
- [x] 3.5 Print completion message with required API keys and next step (`/dialectic`)

## 4. README Update

- [x] 4.1 Add "Install" section at top with the copy-pasteable Claude Code prompt (git clone one-liner + setup)
- [x] 4.2 Add API keys setup instructions (OPENAI_API_KEY, PPLX_API_KEY or BRAVE_API_KEY)
- [x] 4.3 Add "Usage" section: "Open Claude Code in any project and type `/dialectic`"
- [x] 4.4 Demote LangGraph Studio instructions to an "Advanced / Development" section
- [x] 4.5 Add note explaining `SKILL.md` at repo root (for global skill install pattern)
