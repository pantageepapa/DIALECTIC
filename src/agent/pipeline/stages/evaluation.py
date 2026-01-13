"""Stage 5: Score arguments on 14 quality criteria.

Each argument is evaluated on dimensions like:
- Local Acceptability, Relevance, Sufficiency
- Cogency, Credibility, Clarity
- Global Acceptability, Relevance, Sufficiency
- Reasonableness, etc.

Scores determine which arguments advance to refinement.
The top K arguments (based on config) are selected for the next stage.
"""

import asyncio

import backoff
from langchain_core.messages import HumanMessage, SystemMessage
from openai import RateLimitError

from agent.common.llm_config import get_llm
from agent.dataclasses.argument import Argument
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState
from agent.pipeline.state.schemas import SingleArgumentScore
from agent.pipeline.utils.helpers import format_argument_feedback
from agent.prompts import (
    CRITERIA_MAPPING,
    EVALUATE_SINGLE_ARGUMENT_USER_PROMPT,
    SINGLE_ARGUMENT_EVALUATION_SYSTEM_PROMPT,
)


@backoff.on_exception(
    backoff.expo, RateLimitError, max_tries=5, max_time=60, jitter=backoff.full_jitter
)
async def score_single_argument(argument: Argument) -> Argument:
    """Score one argument against all 14 criteria.

    Uses temperature=0.0 for consistent, reproducible scoring.
    Includes retry logic to ensure we get exactly 14 scores.
    """
    llm = get_llm(temperature=0.0)
    llm_with_structured_output = llm.with_structured_output(SingleArgumentScore)

    system_prompt = SINGLE_ARGUMENT_EVALUATION_SYSTEM_PROMPT
    critique = (
        "Critique of the argument: " + argument.critique if argument.critique else ""
    )

    # Retry logic for getting correct number of scores
    max_retries = 5
    score = None
    for attempt in range(max_retries):
        score = await llm_with_structured_output.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=EVALUATE_SINGLE_ARGUMENT_USER_PROMPT.format(
                        argument=argument.content, critique=critique
                    )
                ),
            ]
        )

        if len(score.scores) == len(CRITERIA_MAPPING):
            break
        elif attempt < max_retries - 1:
            print(
                f"Attempt {attempt + 1}: Got {len(score.scores)} scores instead of {len(CRITERIA_MAPPING)}, retrying..."
            )
        else:
            raise ValueError(
                f"After {max_retries} attempts, still got {len(score.scores)} scores instead of {len(CRITERIA_MAPPING)}"
            )

    argument.score = sum(criterion.score for criterion in score.scores)
    argument.argument_feedback = format_argument_feedback(score.scores)
    return argument


async def score_arguments_in_parallel(arguments: list[Argument]) -> list[Argument]:
    """Score multiple arguments concurrently.

    Uses asyncio.gather for parallel execution, significantly
    speeding up the evaluation phase.
    """
    if not arguments:
        return []

    tasks = [score_single_argument(argument) for argument in arguments]
    scored_arguments = await asyncio.gather(*tasks)

    return scored_arguments


async def score_and_select_best_k(
    state: IterativeInvestmentStoryState,
) -> dict:
    """Score all arguments, select top K for refinement.

    Scores all current arguments individually, then selects the
    top K based on the current iteration's k_best setting.

    Returns both the full scored list and the selected subset.
    """
    arguments_to_score = state.current_arguments
    scored_arguments = await score_arguments_in_parallel(arguments_to_score)

    # Sort and select top K for current iteration
    k_best = state.get_current_k_best()
    top_arguments = sorted(scored_arguments, key=lambda x: x.score, reverse=True)[
        :k_best
    ]

    return {
        "current_arguments": scored_arguments,
        "selected_arguments": top_arguments,
    }
