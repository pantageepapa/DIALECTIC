"""Stage 6: Refine arguments based on critiques and scores.

Arguments are improved by:
1. Addressing weaknesses identified in devil's advocate critiques
2. Improving low-scoring evaluation criteria
3. Incorporating additional evidence from Q&A pairs

The refined arguments replace the originals for the next iteration
or become the final arguments if this is the last iteration.
"""

import asyncio

import backoff
from langchain_core.messages import HumanMessage, SystemMessage
from openai import RateLimitError

from agent.common.llm_config import get_llm
from agent.common.utils import (
    format_qa_pairs_with_index,
    get_qa_pair_from_question_tree_with_index,
    get_qa_pairs_from_question_tree,
)
from agent.dataclasses.argument import Argument
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState
from agent.pipeline.state.schemas import IndividualRefinedArgumentOutput
from agent.prompts import (
    REFINE_CONTRA_ARGUMENT_SYSTEM_PROMPT,
    REFINE_CONTRA_ARGUMENTS_USER_PROMPT,
    REFINE_PRO_ARGUMENT_SYSTEM_PROMPT,
    REFINE_PRO_ARGUMENTS_USER_PROMPT,
)

# Initialize LLM
llm = get_llm(temperature=0.5)


@backoff.on_exception(
    backoff.expo, RateLimitError, max_tries=5, max_time=60, jitter=backoff.full_jitter
)
async def _refine_individual_pro_argument(
    argument: Argument, qa_pairs_formatted: str
) -> IndividualRefinedArgumentOutput:
    """Refine a single pro argument using its critique and feedback.

    Uses the argument's feedback scores to guide improvement,
    focusing on low-scoring criteria.
    """
    llm_with_structured_output = llm.with_structured_output(
        IndividualRefinedArgumentOutput
    )

    refined_argument: IndividualRefinedArgumentOutput = (
        await llm_with_structured_output.ainvoke(
            [
                SystemMessage(content=REFINE_PRO_ARGUMENT_SYSTEM_PROMPT),
                HumanMessage(
                    content=REFINE_PRO_ARGUMENTS_USER_PROMPT.format(
                        argument=argument.content,
                        argument_feedback=argument.argument_feedback,
                        questions_and_answers=qa_pairs_formatted,
                    )
                ),
            ]
        )
    )

    return refined_argument


@backoff.on_exception(
    backoff.expo, RateLimitError, max_tries=5, max_time=60, jitter=backoff.full_jitter
)
async def _refine_individual_contra_argument(
    argument: Argument, qa_pairs_formatted: str
) -> IndividualRefinedArgumentOutput:
    """Refine a single contra argument using its critique and feedback.

    Uses the argument's feedback scores to guide improvement,
    focusing on low-scoring criteria.
    """
    llm_with_structured_output = llm.with_structured_output(
        IndividualRefinedArgumentOutput
    )

    refined_argument: IndividualRefinedArgumentOutput = (
        await llm_with_structured_output.ainvoke(
            [
                SystemMessage(content=REFINE_CONTRA_ARGUMENT_SYSTEM_PROMPT),
                HumanMessage(
                    content=REFINE_CONTRA_ARGUMENTS_USER_PROMPT.format(
                        argument=argument.content,
                        argument_feedback=argument.argument_feedback,
                        questions_and_answers=qa_pairs_formatted,
                    )
                ),
            ]
        )
    )

    return refined_argument


async def refine_pro_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Refine all selected pro arguments in parallel.

    Only refines arguments that were selected in the previous
    evaluation stage (the top K).
    """
    pro_arguments_with_critiques: list[Argument] = [
        arg for arg in state.selected_arguments if arg.argument_type == "pro"
    ]

    if len(pro_arguments_with_critiques) == 0:
        return {"refined_pro_arguments": []}

    qa_pairs = get_qa_pairs_from_question_tree(state.question_tree)
    formatted_qa_pairs = format_qa_pairs_with_index(qa_pairs)

    refinement_tasks = [
        _refine_individual_pro_argument(arg, formatted_qa_pairs)
        for arg in pro_arguments_with_critiques
    ]

    refined_results = await asyncio.gather(*refinement_tasks)

    # Update arguments with refined content
    for arg, refined_result in zip(pro_arguments_with_critiques, refined_results):
        arg.refined_content = refined_result.content
        arg.refined_qa_indices = refined_result.qa_indices
        qa_pairs_list = get_qa_pairs_from_question_tree(state.question_tree)
        arg.qa_pairs = [
            get_qa_pair_from_question_tree_with_index(state.question_tree, index)
            for index in arg.refined_qa_indices
            if index < len(qa_pairs_list)
        ]

    return {"refined_pro_arguments": pro_arguments_with_critiques}


async def refine_contra_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Refine all selected contra arguments in parallel.

    Only refines arguments that were selected in the previous
    evaluation stage (the top K).
    """
    contra_arguments_with_critiques: list[Argument] = [
        arg for arg in state.selected_arguments if arg.argument_type == "contra"
    ]

    if len(contra_arguments_with_critiques) == 0:
        return {"refined_contra_arguments": []}

    qa_pairs = get_qa_pairs_from_question_tree(state.question_tree)
    formatted_qa_pairs = format_qa_pairs_with_index(qa_pairs)

    refinement_tasks = [
        _refine_individual_contra_argument(arg, formatted_qa_pairs)
        for arg in contra_arguments_with_critiques
    ]

    refined_results = await asyncio.gather(*refinement_tasks)

    # Update arguments with refined content
    for arg, refined_result in zip(contra_arguments_with_critiques, refined_results):
        arg.refined_content = refined_result.content
        arg.refined_qa_indices = refined_result.qa_indices
        qa_pairs_list = get_qa_pairs_from_question_tree(state.question_tree)
        arg.qa_pairs = [
            get_qa_pair_from_question_tree_with_index(state.question_tree, index)
            for index in arg.refined_qa_indices
            if index < len(qa_pairs_list)
        ]

    return {"refined_contra_arguments": contra_arguments_with_critiques}


def merge_refined_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Combine refined pro and contra arguments.

    Merges the separately refined arguments into a single list
    for history tracking and iteration management.
    """
    return {
        "refined_arguments": state.refined_pro_arguments + state.refined_contra_arguments
    }
