"""Stage 2: Question Answering - answer all questions in a tree.

This stage provides three components:
- answer_tree_graph: Orchestrates answering the full question tree
- answer_with_tool_graph: Answers leaf nodes using web search
- answer_without_tool_graph: Synthesizes parent node answers from children
"""

from agent.pipeline.stages.answering.tree import graph as answer_tree_graph
from agent.pipeline.stages.answering.with_tool import graph as answer_with_tool_graph
from agent.pipeline.stages.answering.without_tool import (
    graph as answer_without_tool_graph,
)

__all__ = [
    "answer_tree_graph",
    "answer_with_tool_graph",
    "answer_without_tool_graph",
]
