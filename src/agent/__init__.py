"""DIALECTIC Investment Analysis Agent.

This package provides tools for analyzing startup investment opportunities
using LLM-powered question decomposition, research, and argument generation.

Main entry point:
    from agent import graph

    result = await graph.ainvoke(initial_state)
"""

from agent.pipeline import graph

__all__ = ["graph"]
