"""Parallel answering of all question trees.

This stage takes question trees for all 4 aspects and answers them
in parallel, then merges all Q&A pairs for use in argument generation.

Each tree is answered recursively:
- Leaf nodes use web search for research
- Parent nodes synthesize answers from children

Answered trees are cached to avoid redundant web searches.
"""

import asyncio
from typing import Dict, List

from agent.common.utils import get_qa_pairs_from_question_tree
from agent.dataclasses.company import Company
from agent.dataclasses.question_tree import QuestionTree
from agent.pipeline.stages.answering.tree import graph as answer_tree_graph
from agent.pipeline.stages.cache import cache_answered_tree, get_cached_answered_tree
from agent.pipeline.stages.constants import QuestionAspect
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState

# 'internal' aspect uses a private/local provider module — see notes in
# parallel_decomposition.py.
try:
    from agent.pipeline.stages import internal_data  # type: ignore
except ImportError:  # pragma: no cover - module is optional/local-only
    internal_data = None


async def _answer_single_tree(
    aspect: str,
    tree: QuestionTree,
    company: Company,
    is_backtesting: bool = False,
    search_end_date: str | None = None,
) -> Dict:
    """Answer a single question tree (with web search).

    Args:
        aspect: The question aspect (general_company, market, product, team)
        tree: The QuestionTree to answer
        company: The company being analyzed
        is_backtesting: Whether to use historical search dates
        search_end_date: End date for search (for backtesting)

    Returns:
        Dict with aspect and answered tree
    """
    result = await answer_tree_graph.ainvoke(
        {
            "question_tree": tree,
            "company": company,
            "is_backtesting": is_backtesting,
            "search_end_date": search_end_date,
        }
    )
    answered_tree = result["question_tree"]

    # Cache the answered tree for future use
    cache_answered_tree(aspect, company, answered_tree)

    return {"aspect": aspect, "tree": answered_tree}


async def _get_or_answer_tree(
    aspect: QuestionAspect,
    tree: QuestionTree,
    company: Company,
    is_backtesting: bool = False,
    search_end_date: str | None = None,
) -> Dict:
    """Get cached answered tree or answer if not cached.

    Args:
        aspect: The question aspect (general_company, market, product, team)
        tree: The QuestionTree to answer (used if not cached)
        company: The company being analyzed
        is_backtesting: Whether to use historical search dates
        search_end_date: End date for search (for backtesting)

    Returns:
        Dict with aspect and answered tree (cached or newly answered)
    """
    # Check cache first
    cached_tree = get_cached_answered_tree(aspect, company)
    if cached_tree is not None:
        return {"aspect": aspect, "tree": cached_tree}

    # Not cached - answer and cache
    return await _answer_single_tree(
        aspect=aspect,
        tree=tree,
        company=company,
        is_backtesting=is_backtesting,
        search_end_date=search_end_date,
    )


async def answer_all_trees(
    state: IterativeInvestmentStoryState,
) -> Dict:
    """Answer all question trees in parallel.

    Takes the question_trees dict from state and answers each tree
    in parallel (checking cache first). Then merges all Q&A pairs
    from all trees.

    Args:
        state: The pipeline state containing question_trees

    Returns:
        Dict with updated question_trees and all_qa_pairs
    """
    if not state.question_trees:
        raise ValueError("No question trees to answer. Run decomposition first.")

    if state.company is None:
        raise ValueError("Company is required for answering")

    # Create tasks for answering all trees in parallel (with caching). The
    # 'internal' aspect runs synchronous Mongo lookups instead of going
    # through the LLM/web-search answering graph.
    tasks = []
    static_results: List[Dict] = []
    for aspect, tree in state.question_trees.items():
        if aspect == "internal":
            if internal_data is not None:
                answered = internal_data.answer_internal_tree(tree, state.company)
                static_results.append({"aspect": aspect, "tree": answered})
            continue
        task = asyncio.create_task(
            _get_or_answer_tree(
                aspect=aspect,
                tree=tree,
                company=state.company,
                is_backtesting=False,  # Could be made configurable
                search_end_date=None,
            )
        )
        tasks.append(task)

    # Execute all answering in parallel
    dynamic_results = await asyncio.gather(*tasks) if tasks else []
    results = [*dynamic_results, *static_results]

    # Build the updated question_trees dict and collect all Q&A pairs
    question_trees: Dict[str, QuestionTree] = {}
    all_qa_pairs: List[Dict[str, str]] = []

    for result in results:
        aspect = result["aspect"]
        answered_tree = result["tree"]
        question_trees[aspect] = answered_tree

        # Extract Q&A pairs from this tree
        tree_qa_pairs = get_qa_pairs_from_question_tree(answered_tree)
        all_qa_pairs.extend(tree_qa_pairs)

    return {
        "question_trees": question_trees,
        "all_qa_pairs": all_qa_pairs,
    }
