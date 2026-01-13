"""Stage 3: Generate pro and contra investment arguments.

Takes the answered question tree and generates initial arguments
for and against investing in the company based on the Q&A pairs.

This is the first stage of the argument refinement loop.
"""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage

from agent.common.llm_config import get_llm
from agent.common.utils import (
    format_qa_pairs_with_index,
    get_qa_pair_from_question_tree_with_index,
    get_qa_pairs_from_question_tree,
)
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState
from agent.pipeline.state.schemas import ArgumentsOutput
from agent.pipeline.utils.helpers import convert_llm_arguments_to_objects
from agent.prompts import (
    ARGUMENT_GENERATION_SYSTEM_PROMPT,
    CONTRA_ARGUMENTS_USER_PROMPT,
    PRO_ARGUMENTS_USER_PROMPT,
)

# Initialize LLM
llm = get_llm(temperature=0.5)


def check_if_final(
    state: IterativeInvestmentStoryState,
) -> Literal["score_and_select_best_k", "generate_pro_and_contra_arguments"]:
    """Router: determines entry point based on is_final flag.

    If is_final is True, skip generation and go straight to scoring.
    This is used when we already have arguments and just want to
    run the final evaluation.
    """
    if state.is_final:
        if len(state.current_arguments) == 0:
            raise ValueError("No current arguments to prepare final arguments")
        return "score_and_select_best_k"
    return "generate_pro_and_contra_arguments"


def generate_pro_and_contra_arguments(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Helper node that routes to parallel pro/contra generation."""
    return state


def generate_pro_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Generate N pro arguments from Q&A pairs.

    Only runs in iteration 0 - subsequent iterations use refined
    arguments from previous iterations.

    Returns dict with pro_arguments to update state.
    """
    if state.current_iteration > 0:
        return state

    qa_pairs = get_qa_pairs_from_question_tree(state.question_tree)
    formatted_qa_pairs = format_qa_pairs_with_index(qa_pairs)

    llm_with_structured_output = llm.with_structured_output(ArgumentsOutput)
    arguments: ArgumentsOutput = llm_with_structured_output.invoke(
        [
            SystemMessage(content=ARGUMENT_GENERATION_SYSTEM_PROMPT),
            HumanMessage(
                content=PRO_ARGUMENTS_USER_PROMPT.format(
                    n_pro_arguments=state.config.n_pro_arguments,
                    questions_and_answers=formatted_qa_pairs,
                )
            ),
        ]
    )

    pro_argument_objects, _ = convert_llm_arguments_to_objects(
        arguments.arguments, "pro", tracking_id_counter=1
    )

    # Attach Q&A pairs to each argument
    for arg in pro_argument_objects:
        qa_pairs_list = get_qa_pairs_from_question_tree(state.question_tree)
        arg.qa_pairs = [
            get_qa_pair_from_question_tree_with_index(state.question_tree, index)
            for index in arg.qa_indices
            if index < len(qa_pairs_list)
        ]

    return {"pro_arguments": pro_argument_objects}


def generate_contra_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Generate N contra arguments from Q&A pairs.

    Only runs in iteration 0 - subsequent iterations use refined
    arguments from previous iterations.

    Returns dict with contra_arguments to update state.
    """
    if state.current_iteration > 0:
        return state

    qa_pairs = get_qa_pairs_from_question_tree(state.question_tree)
    formatted_qa_pairs = format_qa_pairs_with_index(qa_pairs)

    llm_with_structured_output = llm.with_structured_output(ArgumentsOutput)
    arguments: ArgumentsOutput = llm_with_structured_output.invoke(
        [
            SystemMessage(content=ARGUMENT_GENERATION_SYSTEM_PROMPT),
            HumanMessage(
                content=CONTRA_ARGUMENTS_USER_PROMPT.format(
                    n_contra_arguments=state.config.n_contra_arguments,
                    questions_and_answers=formatted_qa_pairs,
                )
            ),
        ]
    )

    # Start counter after pro arguments
    pro_args_count = len(state.pro_arguments) if state.pro_arguments else 0
    contra_argument_objects, _ = convert_llm_arguments_to_objects(
        arguments.arguments, "contra", tracking_id_counter=pro_args_count + 1
    )

    # Attach Q&A pairs to each argument
    for arg in contra_argument_objects:
        qa_pairs_list = get_qa_pairs_from_question_tree(state.question_tree)
        arg.qa_pairs = [
            get_qa_pair_from_question_tree_with_index(state.question_tree, index)
            for index in arg.qa_indices
            if index < len(qa_pairs_list)
        ]

    return {"contra_arguments": contra_argument_objects}


def merge_arguments(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Combine pro and contra into current_arguments.

    This merges the separately generated arguments into a single
    list for the next stage of processing.
    """
    return {"current_arguments": state.pro_arguments + state.contra_arguments}
