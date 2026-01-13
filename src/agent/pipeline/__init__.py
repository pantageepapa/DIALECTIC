"""DIALECTIC Investment Analysis Pipeline.

This pipeline generates investment theses for startup companies through:

1. Question decomposition - Break down complex questions into answerable parts
2. Question answering - Research answers via web search or synthesis
3. Argument generation - Create pro/contra investment arguments
4. Devil's advocate - Challenge each argument from opposing perspective
5. Evaluation - Score arguments on 14 quality criteria
6. Refinement - Improve arguments based on feedback
7. Decision - Make final investment recommendation

Usage:
    from agent.pipeline import graph, IterativeInvestmentStoryState

    state = IterativeInvestmentStoryState(question_tree=tree, config=config)
    result = await graph.ainvoke(state)

For standalone stage usage:
    from agent.pipeline.stages import decomposition_graph, answer_tree_graph
"""

# Main graph
from agent.pipeline.graph import display_results, graph, main

# Stage subgraphs (for standalone use)
from agent.pipeline.stages import (
    answer_tree_graph,
    answer_with_tool_graph,
    answer_without_tool_graph,
    decomposition_graph,
)

# State classes
from agent.pipeline.state import (
    AnswerQuestionTreeState,
    AnswerState,
    AnswerStateSimple,
    IterativeInvestmentStoryState,
)

__all__ = [
    # Main graph
    "graph",
    "main",
    "display_results",
    # State classes
    "IterativeInvestmentStoryState",
    "AnswerState",
    "AnswerStateSimple",
    "AnswerQuestionTreeState",
    # Stage subgraphs
    "decomposition_graph",
    "answer_tree_graph",
    "answer_with_tool_graph",
    "answer_without_tool_graph",
]
