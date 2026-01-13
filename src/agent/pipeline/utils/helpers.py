"""Helper functions for the investment pipeline.

These utilities handle common operations like converting LLM outputs
to internal data structures and formatting feedback for display.
"""

from typing import Literal

from agent.dataclasses.argument import Argument
from agent.pipeline.state.schemas import ArgumentOutput, CriterionScore
from agent.prompts import CRITERIA_MAPPING


def convert_llm_arguments_to_objects(
    llm_arguments: list[ArgumentOutput],
    argument_type: Literal["pro", "contra"],
    tracking_id_counter: int = 1,
) -> tuple[list[Argument], int]:
    """Convert LLM output arguments to Argument dataclass instances.

    Args:
        llm_arguments: List of ArgumentOutput from the LLM
        argument_type: Whether these are "pro" or "contra" arguments
        tracking_id_counter: Starting counter for tracking IDs

    Returns:
        Tuple of (list of Argument objects, next tracking_id_counter)
    """
    arguments = []
    for arg_data in llm_arguments:
        argument = Argument(
            content=arg_data.content,
            argument_type=argument_type,
            qa_indices=arg_data.qa_indices,
            tracking_id=f"arg_{tracking_id_counter}",
        )
        arguments.append(argument)
        tracking_id_counter += 1
    return arguments, tracking_id_counter


def format_argument_feedback(argument_scores: list[CriterionScore]) -> str:
    """Format argument feedback scores into readable text.

    Args:
        argument_scores: List of CriterionScore for each of the 14 criteria

    Returns:
        Formatted string with each criterion, its reasoning, and score
    """
    formatted_feedback_list = []
    for i, feedback in enumerate(argument_scores):
        formatted_feedback_list.append(
            f"{CRITERIA_MAPPING[i]}: {feedback.reasoning} (Score: {feedback.score})"
        )
    return "\n".join(formatted_feedback_list)
