"""Stage 4: Apply devil's advocate critiques to arguments.

Each argument is challenged from the opposing perspective:
- Pro arguments are critiqued by someone against investing
- Contra arguments are critiqued by someone in favor of investing

This helps identify weaknesses and areas for improvement,
making the final arguments more robust and well-reasoned.
"""

import asyncio

import backoff
from langchain_core.messages import HumanMessage, SystemMessage
from openai import RateLimitError

from agent.common.llm_config import get_llm
from agent.common.utils import (
    format_qa_pairs_without_index,
    get_qa_pairs_from_question_tree,
)
from agent.dataclasses.argument import Argument
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState
from agent.pipeline.state.schemas import ArgumentCritique
from agent.prompts import (
    DEVILS_ADVOCATE_CONTRA_SYSTEM_PROMPT,
    DEVILS_ADVOCATE_INDIVIDUAL_CONTRA_ARGUMENT_USER_PROMPT,
    DEVILS_ADVOCATE_INDIVIDUAL_PRO_ARGUMENT_USER_PROMPT,
    DEVILS_ADVOCATE_PRO_SYSTEM_PROMPT,
)

# Initialize LLM
llm = get_llm(temperature=0.5)


@backoff.on_exception(
    backoff.expo, RateLimitError, max_tries=5, max_time=60, jitter=backoff.full_jitter
)
async def _apply_devils_advocate_to_pro_argument(
    argument: Argument, qa_pairs_formatted: str, former_critique: str | None = None
) -> Argument:
    """Critique a single pro argument from the opposing perspective.

    The critique comes from someone against investing, challenging
    the reasons why this would be a good investment.
    """
    llm_with_structured_output = llm.with_structured_output(ArgumentCritique)

    user_prompt = DEVILS_ADVOCATE_INDIVIDUAL_PRO_ARGUMENT_USER_PROMPT.format(
        questions_and_answers=qa_pairs_formatted, argument=argument.content
    )
    if former_critique:
        user_prompt += f"\nHere is your past critique - do not repeat the same critique but find a new one:\n{former_critique}"

    critique: ArgumentCritique = await llm_with_structured_output.ainvoke(
        [
            SystemMessage(content=DEVILS_ADVOCATE_PRO_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    argument.critique = critique.critique
    return argument


@backoff.on_exception(
    backoff.expo, RateLimitError, max_tries=5, max_time=60, jitter=backoff.full_jitter
)
async def _apply_devils_advocate_to_contra_argument(
    argument: Argument, qa_pairs_formatted: str, former_critique: str | None = None
) -> Argument:
    """Critique a single contra argument from the opposing perspective.

    The critique comes from someone in favor of investing, challenging
    the reasons why this would be a bad investment.
    """
    llm_with_structured_output = llm.with_structured_output(ArgumentCritique)

    user_prompt = DEVILS_ADVOCATE_INDIVIDUAL_CONTRA_ARGUMENT_USER_PROMPT.format(
        questions_and_answers=qa_pairs_formatted, argument=argument.content
    )
    if former_critique:
        user_prompt += f"\nHere is your past critique - do not repeat the same critique but find a new one:\n{former_critique}"

    critique: ArgumentCritique = await llm_with_structured_output.ainvoke(
        [
            SystemMessage(content=DEVILS_ADVOCATE_CONTRA_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    argument.critique = critique.critique
    return argument


def apply_devils_advocate(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Helper node that routes to parallel pro/contra critique."""
    return state


async def apply_devils_advocate_to_pro_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Apply critiques to all pro arguments in parallel.

    Uses asyncio.gather for concurrent execution, significantly
    speeding up the critique phase.
    """
    if not state.current_arguments:
        raise ValueError("No current arguments to apply devil's advocate to")

    qa_pairs = get_qa_pairs_from_question_tree(state.question_tree)
    formatted_qa_pairs = format_qa_pairs_without_index(qa_pairs)

    pro_arguments = [
        arg for arg in state.current_arguments if arg.argument_type == "pro"
    ]
    if len(pro_arguments) == 0:
        return {"devils_advocate_pro_arguments": []}

    critique_tasks = [
        _apply_devils_advocate_to_pro_argument(
            arg, formatted_qa_pairs, arg.former_critique
        )
        for arg in pro_arguments
    ]

    critiqued_arguments = await asyncio.gather(*critique_tasks)

    return {"devils_advocate_pro_arguments": critiqued_arguments}


async def apply_devils_advocate_to_contra_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Apply critiques to all contra arguments in parallel.

    Uses asyncio.gather for concurrent execution, significantly
    speeding up the critique phase.
    """
    if not state.current_arguments:
        raise ValueError("No current arguments to apply devil's advocate to")

    qa_pairs = get_qa_pairs_from_question_tree(state.question_tree)
    formatted_qa_pairs = format_qa_pairs_without_index(qa_pairs)

    contra_arguments = [
        arg for arg in state.current_arguments if arg.argument_type == "contra"
    ]
    if len(contra_arguments) == 0:
        return {"devils_advocate_contra_arguments": []}

    critique_tasks = [
        _apply_devils_advocate_to_contra_argument(
            arg, formatted_qa_pairs, arg.former_critique
        )
        for arg in contra_arguments
    ]

    critiqued_arguments = await asyncio.gather(*critique_tasks)

    return {"devils_advocate_contra_arguments": critiqued_arguments}
