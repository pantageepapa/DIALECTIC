"""Stage 7: Make final investment decision.

After all iterations complete:
1. Score final arguments
2. Compare average pro vs contra scores
3. Determine invest/not_invest recommendation

This stage also handles iteration management - tracking history,
resetting state for the next iteration, and deciding when to finalize.
"""

from typing import Literal

from agent.dataclasses.argument import Argument
from agent.pipeline.stages.evaluation import score_arguments_in_parallel
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState


def add_arguments_to_history(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Track iteration state in history.

    Saves a snapshot of the current iteration's arguments for
    later analysis and debugging.
    """
    state.arguments_history.append(
        {
            "iteration": state.current_iteration,
            "refined_arguments": state.refined_arguments,
            "selected_arguments": state.selected_arguments,
            "pro_arguments": state.pro_arguments,
            "contra_arguments": state.contra_arguments,
            "devils_advocate_pro_arguments": state.devils_advocate_pro_arguments,
            "devils_advocate_contra_arguments": state.devils_advocate_contra_arguments,
            "refined_pro_arguments": state.refined_pro_arguments,
            "refined_contra_arguments": state.refined_contra_arguments,
        }
    )

    return state


def reset_arguments_and_increment_iteration(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Prepare for next iteration cycle.

    Converts refined arguments to new current arguments,
    preserving tracking IDs and critique history.
    """
    new_current_arguments = []
    for refined_arg in state.refined_arguments:
        new_arg = Argument(
            # refined_content becomes content
            content=refined_arg.refined_content,
            qa_indices=refined_arg.refined_qa_indices,
            argument_type=refined_arg.argument_type,
            score=refined_arg.score,
            qa_pairs=refined_arg.qa_pairs,
            # Add former critique to the argument
            former_critique=refined_arg.critique,
            # Preserve tracking_id across iterations
            tracking_id=refined_arg.tracking_id,
        )
        new_current_arguments.append(new_arg)

    state.current_arguments = new_current_arguments

    # Reset other arguments to empty lists
    state.refined_arguments = []
    state.selected_arguments = []
    state.pro_arguments = []
    state.contra_arguments = []
    state.devils_advocate_pro_arguments = []
    state.devils_advocate_contra_arguments = []
    state.refined_pro_arguments = []
    state.refined_contra_arguments = []

    # Increment iteration
    state.current_iteration += 1

    return state


def check_continue(
    state: IterativeInvestmentStoryState,
) -> Literal["apply_devils_advocate", "prepare_final_arguments"]:
    """Router: continue iterating or finalize.

    Checks if we've reached max_iterations. If so, proceeds to
    final argument preparation. Otherwise, continues the loop.
    """
    if not state.should_continue_iterations:
        return "prepare_final_arguments"
    return "apply_devils_advocate"


async def prepare_final_arguments(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Score the final set of arguments.

    Performs one final scoring of all remaining arguments
    before making the investment decision.
    """
    state.final_arguments = state.current_arguments

    # Score the final arguments
    scored_arguments = await score_arguments_in_parallel(state.final_arguments)
    state.arguments_history.append(
        {
            "iteration": state.current_iteration,
            "selected_arguments": scored_arguments,
            "refined_arguments": scored_arguments,
        }
    )

    return state


def decide_final_investment_decision(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Compare pro/contra scores, make decision.

    Calculates average scores for pro and contra arguments.
    If pro average > contra average, recommend invest.
    Otherwise, recommend not_invest.
    """
    pro_final_arguments = [
        arg for arg in state.final_arguments if arg.argument_type == "pro"
    ]
    contra_final_arguments = [
        arg for arg in state.final_arguments if arg.argument_type == "contra"
    ]

    pro_final_arguments_score = (
        sum(arg.score for arg in pro_final_arguments) / len(pro_final_arguments)
        if pro_final_arguments
        else 0
    )
    contra_final_arguments_score = (
        sum(arg.score for arg in contra_final_arguments) / len(contra_final_arguments)
        if contra_final_arguments
        else 0
    )

    if pro_final_arguments_score > contra_final_arguments_score:
        state.final_decision = "invest"
    else:
        state.final_decision = "not_invest"

    return state


def create_final_investment_story(
    state: IterativeInvestmentStoryState,
) -> IterativeInvestmentStoryState:
    """Finalize the investment story state.

    Currently a no-op since we don't generate investment proposals.
    The state already contains all necessary final data.
    """
    return state
