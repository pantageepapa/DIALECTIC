"""Orchestrate answering an entire question tree.

Recursively answers the tree from leaves to root:
1. Leaf nodes -> answer_with_tool (web search)
2. Parent nodes -> answer_without_tool (synthesis)

Uses asyncio.gather for parallel execution of sibling questions,
which significantly speeds up the answering process.
"""

import asyncio

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent.common.llm_config import get_llm
from agent.dataclasses.company import Company
from agent.dataclasses.examples import BRANDBACK_COMPANY
from agent.dataclasses.question_tree import QuestionNode, QuestionTree
from agent.pipeline.stages.answering.with_tool import graph as answer_with_tool_graph
from agent.pipeline.stages.answering.without_tool import (
    graph as answer_without_tool_graph,
)

# Initialize LLM
llm = get_llm(temperature=0.0)


class AnswerQuestionTreeState(BaseModel):
    """State for answering an entire question tree."""

    question_tree: QuestionTree
    company: Company = BRANDBACK_COMPANY
    vc_context: str | None = None

    is_backtesting: bool | None = False
    search_end_date: str | None = None


async def _async_answer_question_with_tool(
    question: str,
    company: Company,
    qa_pairs: list[dict[str, str]] | None = None,
    vc_context: str | None = None,
    is_backtesting: bool | None = False,
    search_end_date: str | None = None,
) -> dict[str, str]:
    """Async wrapper for answer_with_tool_graph."""
    return await answer_with_tool_graph.ainvoke(
        {
            "question": question,
            "company": company,
            "qa_pairs": qa_pairs or [],
            "vc_context": vc_context or "",
            "is_backtesting": is_backtesting,
            "search_end_date": search_end_date,
        }
    )


async def _async_answer_question_without_tool(
    question: str,
    company: Company,
    qa_pairs: list[dict[str, str]] | None = None,
    vc_context: str | None = None,
) -> dict[str, str]:
    """Async wrapper for answer_without_tool_graph."""
    return await answer_without_tool_graph.ainvoke(
        {
            "question": question,
            "company": company,
            "qa_pairs": qa_pairs or [],
            "vc_context": vc_context or "",
        }
    )


async def _answer_node(
    question_node: QuestionNode,
    company: Company,
    vc_context: str | None = None,
    is_backtesting: bool | None = False,
    search_end_date: str | None = None,
) -> QuestionNode:
    """Recursively answer a question node and its children.

    Leaf nodes (no children) use web search tools for research.
    Parent nodes synthesize answers from their children without tools.

    Children are answered in parallel using asyncio.gather.
    """
    # 1. Answer all child questions in parallel
    answered_children: list[QuestionNode] = []
    if question_node.sub_nodes:
        tasks = [
            asyncio.create_task(
                _answer_node(
                    child,
                    company,
                    vc_context=vc_context,
                    is_backtesting=is_backtesting,
                    search_end_date=search_end_date,
                )
            )
            for child in question_node.sub_nodes
        ]
        answered_children = await asyncio.gather(*tasks)

    # 2. Prepare context from child answers
    sub_pairs: list[dict[str, str]] = [
        {"question": n.question, "answer": n.answer}
        for n in answered_children
        if n.answer
    ]

    # 3. Answer this node
    is_leaf = len(question_node.sub_nodes) == 0

    if is_leaf:
        # Leaf: use web search
        result = await _async_answer_question_with_tool(
            question_node.question,
            company,
            qa_pairs=sub_pairs,
            vc_context=vc_context,
            is_backtesting=is_backtesting,
            search_end_date=search_end_date,
        )
    else:
        # Parent: synthesize from children
        result = await _async_answer_question_without_tool(
            question_node.question,
            company,
            qa_pairs=sub_pairs,
            vc_context=vc_context,
        )

    # 4. Store answer on the node
    question_node.answer = result["answer"]
    return question_node


async def answer_question_tree(
    state: AnswerQuestionTreeState,
) -> AnswerQuestionTreeState:
    """Answer the full question tree starting from root.

    Recursively traverses the tree, answering each node.
    Returns the tree with all questions answered.
    """
    await _answer_node(
        state.question_tree.root_node,
        state.company,
        state.vc_context,
        state.is_backtesting,
        state.search_end_date,
    )

    return {"question_tree": state.question_tree}


# Build the graph
builder = StateGraph(state_schema=AnswerQuestionTreeState)

builder.add_node("answer_question_tree", answer_question_tree)

builder.add_edge(START, "answer_question_tree")
builder.add_edge("answer_question_tree", END)

graph = builder.compile()


if __name__ == "__main__":
    import json

    from agent.cached_question_trees import get_market_question_tree

    state = AnswerQuestionTreeState(
        company=BRANDBACK_COMPANY,
        question_tree=get_market_question_tree(BRANDBACK_COMPANY),
        is_backtesting=True,
        search_end_date="2023-06-15",
    )

    result = asyncio.run(graph.ainvoke(state))
    print(json.dumps(result["question_tree"].model_dump(), indent=2, default=str))
