# DIALECTIC

**LLM-Based Multi-Agent System for Startup Evaluation**

📄 *Accepted at EACL 2026 Industry Track* — [Read the Paper](./paper.pdf)

## Overview

DIALECTIC is an LLM-based multi-agent system that helps venture capital investors evaluate startup investment opportunities. The system addresses a critical challenge: investors face an overwhelming number of opportunities but can only invest in a small fraction.

The pipeline works through four key stages:

1. **Data Collection** — Gather factual knowledge about the startup via web search
2. **Knowledge Organization** — Structure information into hierarchical question trees
3. **Argument Generation** — Synthesize pro and contra investment arguments
4. **Iterative Refinement** — Simulate debate (devil's advocate) to critique and refine arguments

The output includes natural-language arguments with numeric scores, enabling efficient opportunity ranking.

## Install

DIALECTIC ships as a [Claude Code](https://claude.ai/code) skill. Once installed, type `/dialectic` in any Claude Code session to analyze a startup.

**Open Claude Code and paste this prompt:**

```
run git clone --single-branch --depth 1 https://github.com/pantageepapa/DIALECTIC.git ~/.claude/skills/dialectic && cd ~/.claude/skills/dialectic && ./setup
```

Claude will clone the repo, install dependencies, and walk you through the rest.

### API Keys

After setup, add your keys to `~/.claude/skills/dialectic/.env`:

| Key | Required | Where to get it |
|-----|----------|-----------------|
| `OPENAI_API_KEY` | Yes | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `PPLX_API_KEY` | Yes (or Brave) | [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) |
| `BRAVE_SEARCH_API_KEY` | Yes (or Perplexity) | [brave.com/search/api](https://brave.com/search/api/) |
| `LANGSMITH_API_KEY` | No | Optional tracing |

## Usage

Open Claude Code in any project and type:

```
/dialectic
```

Claude will ask for the startup's name, what it does, industry, and any additional context. Then it runs the full analysis pipeline and presents:

- **Pro arguments** — reasons to invest, with scores
- **Con arguments** — reasons to pass, with scores
- **Investment recommendation** — invest or pass, with synthesis

Choose between a clean **summary** (recommended) or the full **detailed** view showing iteration history, critiques, and refinements.

## Project Structure

```
src/agent/
├── cli.py                    # CLI entry point for the /dialectic skill
├── pipeline/
│   ├── graph.py              # Main LangGraph definition
│   ├── stages/               # Pipeline stages
│   │   ├── constants.py      # Investment questions & types
│   │   ├── cache.py          # Caching utilities
│   │   ├── decomposition.py  # Question tree decomposition
│   │   ├── answering/        # Question answering (with/without tools)
│   │   ├── generation.py     # Pro/contra argument generation
│   │   ├── critique.py       # Devil's advocate critiques
│   │   ├── evaluation.py     # Argument scoring
│   │   ├── refinement.py     # Argument refinement
│   │   └── decision.py       # Final investment decision
│   ├── state/                # Pydantic state schemas
│   └── utils/                # Helper functions
├── prompts/                  # All LLM prompts
├── dataclasses/              # Core data models (Company, Argument, etc.)
└── web_search/               # Web search providers
```

> **Note:** `SKILL.md` at the repo root is the Claude Code skill definition. When the repo is cloned to `~/.claude/skills/dialectic/`, Claude Code automatically registers `/dialectic` as a global slash command.

## Uninstall

```bash
~/.claude/skills/dialectic/uninstall
```

This removes the skill directory and deregisters `/dialectic` from Claude Code.

## Advanced: LangGraph Studio

For development, graph visualization, and debugging individual pipeline stages:

### 1. Install Dependencies

```bash
pip install -e . "langgraph-cli[inmem]"
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Add your API keys
```

### 3. Run with LangGraph Studio

```bash
langgraph dev
```

This opens LangGraph Studio where you can run the pipeline interactively, visualize the graph, and inspect state at each node.

## Citation

```bibtex
@inproceedings{dialectic2026,
  title={DIALECTIC: An LLM-Based Multi-Agent System for Startup Evaluation},
  author={Bae, Jae Yoon and Malberg, Simon and Galang, Joyce and Retterath, Andre and Groh, Georg},
  booktitle={Proceedings of the 2026 Conference of the European Chapter of the Association for Computational Linguistics: Industry Track},
  year={2026},
  publisher={Association for Computational Linguistics}
}
```

## License

See [LICENSE](./LICENSE) for details.
