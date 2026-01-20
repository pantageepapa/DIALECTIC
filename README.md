# DIALECTIC

**LLM-Based Multi-Agent System for Startup Evaluation**

📄 *Accepted at EACL 2026 Industry Track*

Paper[paper.pdf]

## Overview

DIALECTIC is an LLM-based multi-agent system that helps venture capital investors evaluate startup investment opportunities. The system addresses a critical challenge: investors face an overwhelming number of opportunities but can only invest in a small fraction.

The pipeline works through four key stages:

1. **Data Collection** — Gather factual knowledge about the startup via web search
2. **Knowledge Organization** — Structure information into hierarchical question trees
3. **Argument Generation** — Synthesize pro and contra investment arguments
4. **Iterative Refinement** — Simulate debate (devil's advocate) to critique and refine arguments

The output includes natural-language arguments with numeric scores, enabling efficient opportunity ranking.

## Quick Start

### 1. Install Dependencies

```bash
pip install -e . "langgraph-cli[inmem]"
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```
OPENAI_API_KEY=your_openai_api_key_here
PPLX_API_KEY=your_perplexity_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here  # Optional, for tracing
```

### 3. Run with LangGraph Studio

```bash
langgraph dev
```

This opens LangGraph Studio where you can run the pipeline interactively, visualize the graph, and debug individual stages.

## Project Structure

```
src/agent/
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

The main entry point is `pipeline/graph.py`, which orchestrates all stages using LangGraph. Each stage is modular and can be tested independently.

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
