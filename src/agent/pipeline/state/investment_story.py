"""State for the iterative investment story pipeline.

This module defines the main state class that tracks arguments
through multiple refinement iterations.
"""

from typing import Any, Dict, Literal

from pydantic import BaseModel

from agent.dataclasses.argument import Argument
from agent.dataclasses.config import Config
from agent.dataclasses.question_tree import QuestionTree


class IterativeInvestmentStoryState(BaseModel):
    """Main state tracking arguments through refinement iterations.

    The pipeline generates pro/contra arguments, applies devil's advocate
    critiques, scores them, and refines the best ones over multiple iterations.

    Attributes:
        question_tree: The answered question tree providing context
        config: Pipeline configuration (num arguments, iterations, etc.)
        is_final: If True, skip generation and go straight to scoring
        company_name: Name of the company being evaluated

        current_arguments: Arguments being processed in current iteration
        refined_arguments: Arguments after refinement
        selected_arguments: Top K arguments selected for refinement
        arguments_history: History of all iterations for analysis

        final_arguments: The final set of arguments after all iterations
        final_decision: Investment recommendation (invest/not_invest)
    """

    # Input
    question_tree: QuestionTree
    config: Config = Config(
        n_pro_arguments=3,
        n_contra_arguments=3,
        k_best_arguments_per_iteration=[3, 1],
        max_iterations=2,
    )
    is_final: bool = False
    company_name: str = ""

    # Argument tracking
    current_arguments: list[Argument] = []
    refined_arguments: list[Argument] = []
    selected_arguments: list[Argument] = []
    arguments_history: list[Dict[str, Any]] = []
    current_iteration: int = 0

    # Per-type argument tracking
    pro_arguments: list[Argument] = []
    contra_arguments: list[Argument] = []
    devils_advocate_pro_arguments: list[Argument] = []
    devils_advocate_contra_arguments: list[Argument] = []
    refined_pro_arguments: list[Argument] = []
    refined_contra_arguments: list[Argument] = []

    # Final output
    final_arguments: list[Argument] = []
    final_decision: Literal["invest", "not_invest"] = None

    @property
    def should_continue_iterations(self) -> bool:
        """Check if we should continue with more iterations."""
        return self.current_iteration < self.config.max_iterations

    def get_current_k_best(self) -> int:
        """Get k_best_arguments for the current iteration."""
        return self.config.get_k_best_for_iteration(self.current_iteration)
