"""Parallel decomposition of all 4 investment questions.

This stage takes a company as input and decomposes all 4 predefined
investment questions in parallel, checking cache first to avoid
redundant LLM calls.

The 4 questions cover:
- General company alignment
- Market size and growth
- Product features and technology
- Team experience and track record
"""

import asyncio
from typing import Dict

from agent.dataclasses.company import Company
from agent.dataclasses.question_tree import QuestionTree
from agent.pipeline.stages.cache import cache_question_tree, get_cached_question_tree
from agent.pipeline.stages.constants import INVESTMENT_QUESTIONS, QuestionAspect
from agent.pipeline.stages.decomposition import graph as decomposition_graph
from agent.pipeline.state.decomposition import DecompositionInput
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState

# 'internal' aspect uses a private/local provider module that is not
# committed to this repo. If the module is not present (or its provider
# is not configured), the 'internal' aspect is silently skipped.
try:
    from agent.pipeline.stages import internal_data  # type: ignore
except ImportError:  # pragma: no cover - module is optional/local-only
    internal_data = None


async def _decompose_single_question(
    question: str,
    industry: str,
    aspect: QuestionAspect,
) -> Dict[str, QuestionTree | str]:
    """Decompose a single question using the decomposition graph.

    Args:
        question: The question to decompose
        industry: The company's industry for customization
        aspect: The question aspect (general_company, market, product, team)

    Returns:
        Dict with aspect key and decomposed QuestionTree
    """
    result = await decomposition_graph.ainvoke(
        DecompositionInput(
            question=question,
            industry=industry,
            aspect=aspect,
        )
    )
    return {"aspect": aspect, "tree": result["question_tree"]}


async def _get_or_decompose_question(
    question: str,
    industry: str,
    aspect: QuestionAspect,
    company_name: str,
) -> Dict[str, QuestionTree | str]:
    """Get cached question tree or decompose if not cached.

    Args:
        question: The question to decompose
        industry: The company's industry for customization
        aspect: The question aspect
        company_name: The company name for cache key

    Returns:
        Dict with aspect key and QuestionTree (cached or newly decomposed)
    """
    cache_company = Company(name=company_name, industry=industry)

    # Check cache first
    cached_tree = get_cached_question_tree(question, cache_company, aspect)
    if cached_tree is not None:
        return {"aspect": aspect, "tree": cached_tree}

    # Not cached - decompose and cache
    result = await _decompose_single_question(question, industry, aspect)
    cache_question_tree(question, cache_company, result["tree"])
    return result


async def decompose_all_questions(
    state: IterativeInvestmentStoryState,
) -> Dict[str, Dict[str, QuestionTree]]:
    """Decompose all 4 investment questions in parallel.

    Takes the company from state and decomposes all 4 predefined questions,
    checking cache first for each. Returns dict of question_trees keyed by aspect.

    Args:
        state: The pipeline state containing the company

    Returns:
        Dict with question_trees mapping aspect to QuestionTree
    """
    if state.company is None:
        raise ValueError("Company is required for decomposition")

    # Create tasks for all questions. The 'internal' aspect uses a static
    # hand-coded tree (no LLM decomposition needed); the other 4 aspects
    # decompose dynamically.
    tasks = []
    static_results: list[Dict[str, QuestionTree | str]] = []
    for aspect, question in INVESTMENT_QUESTIONS.items():
        if aspect == "internal":
            if internal_data is not None and internal_data.is_enabled():
                static_results.append(
                    {
                        "aspect": aspect,
                        "tree": internal_data.build_internal_question_tree(),
                    }
                )
            # If internal data is unavailable, silently skip — pipeline still runs the other 4.
            continue
        task = asyncio.create_task(
            _get_or_decompose_question(
                question=question,
                industry=state.company.industry,
                aspect=aspect,
                company_name=state.company.name,
            )
        )
        tasks.append(task)

    # Execute all decompositions in parallel
    dynamic_results = await asyncio.gather(*tasks) if tasks else []

    # Build the question_trees dict
    question_trees: Dict[str, QuestionTree] = {}
    for result in [*dynamic_results, *static_results]:
        question_trees[result["aspect"]] = result["tree"]

    return {"question_trees": question_trees}
