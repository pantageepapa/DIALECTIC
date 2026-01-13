"""Pipeline stages for investment analysis.

This module exports all stage functions and subgraphs:

Stage 1 - Decomposition: Break down complex questions
Stage 2 - Answering: Answer questions via web search or synthesis
Stage 3 - Generation: Generate pro/contra arguments
Stage 4 - Critique: Apply devil's advocate critiques
Stage 5 - Evaluation: Score arguments on 14 criteria
Stage 6 - Refinement: Improve arguments based on feedback
Stage 7 - Decision: Make final investment recommendation
"""

# Stage 1: Decomposition
# Stage 2: Answering
from agent.pipeline.stages.answering import (
    answer_tree_graph,
    answer_with_tool_graph,
    answer_without_tool_graph,
)

# Stage 4: Critique
from agent.pipeline.stages.critique import (
    apply_devils_advocate,
    apply_devils_advocate_to_contra_arguments,
    apply_devils_advocate_to_pro_arguments,
)

# Stage 7: Decision
from agent.pipeline.stages.decision import (
    add_arguments_to_history,
    check_continue,
    create_final_investment_story,
    decide_final_investment_decision,
    prepare_final_arguments,
    reset_arguments_and_increment_iteration,
)
from agent.pipeline.stages.decomposition import graph as decomposition_graph

# Stage 5: Evaluation
from agent.pipeline.stages.evaluation import (
    score_and_select_best_k,
    score_arguments_in_parallel,
    score_single_argument,
)

# Stage 3: Generation
from agent.pipeline.stages.generation import (
    check_if_final,
    generate_contra_arguments,
    generate_pro_and_contra_arguments,
    generate_pro_arguments,
    merge_arguments,
)

# Stage 6: Refinement
from agent.pipeline.stages.refinement import (
    merge_refined_arguments,
    refine_contra_arguments,
    refine_pro_arguments,
)

__all__ = [
    # Stage 1
    "decomposition_graph",
    # Stage 2
    "answer_tree_graph",
    "answer_with_tool_graph",
    "answer_without_tool_graph",
    # Stage 3
    "check_if_final",
    "generate_pro_and_contra_arguments",
    "generate_pro_arguments",
    "generate_contra_arguments",
    "merge_arguments",
    # Stage 4
    "apply_devils_advocate",
    "apply_devils_advocate_to_pro_arguments",
    "apply_devils_advocate_to_contra_arguments",
    # Stage 5
    "score_single_argument",
    "score_arguments_in_parallel",
    "score_and_select_best_k",
    # Stage 6
    "refine_pro_arguments",
    "refine_contra_arguments",
    "merge_refined_arguments",
    # Stage 7
    "add_arguments_to_history",
    "reset_arguments_and_increment_iteration",
    "check_continue",
    "prepare_final_arguments",
    "decide_final_investment_decision",
    "create_final_investment_story",
]
