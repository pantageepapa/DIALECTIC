"""Main LangGraph for iterative investment story generation.

This module defines and compiles the full investment analysis pipeline,
orchestrating all stages from question decomposition through argument
generation to final investment decision.

Pipeline Flow:
1. Decompose 4 investment questions in parallel
2. Answer all question trees in parallel
3. Generate pro/contra arguments from Q&A pairs
4. Apply devil's advocate critiques
5. Score and evaluate arguments
6. Refine top arguments
7. Iterate or make final decision
"""

import asyncio
from typing import Literal

from langgraph.graph import END, START, StateGraph

from agent.dataclasses.config import Config
from agent.pipeline.stages.critique import (
    apply_devils_advocate,
    apply_devils_advocate_to_contra_arguments,
    apply_devils_advocate_to_pro_arguments,
)
from agent.pipeline.stages.decision import (
    add_arguments_to_history,
    check_continue,
    create_final_investment_story,
    decide_final_investment_decision,
    prepare_final_arguments,
    reset_arguments_and_increment_iteration,
)
from agent.pipeline.stages.evaluation import score_and_select_best_k
from agent.pipeline.stages.generation import (
    check_if_final,
    generate_contra_arguments,
    generate_pro_and_contra_arguments,
    generate_pro_arguments,
    merge_arguments,
)
from agent.pipeline.stages.parallel_answering import answer_all_trees
from agent.pipeline.stages.parallel_decomposition import decompose_all_questions
from agent.pipeline.stages.refinement import (
    merge_refined_arguments,
    refine_contra_arguments,
    refine_pro_arguments,
)
from agent.pipeline.state.investment_story import (
    InputState,
    IterativeInvestmentStoryState,
)


def check_start_point(
    state: IterativeInvestmentStoryState,
) -> Literal["decompose_questions", "generate_pro_and_contra_arguments", "score_and_select_best_k"]:
    """Router: determines pipeline entry point based on state.

    - If company provided but no question_trees: start with decomposition
    - If question_trees exist but is_final=False: start with argument generation
    - If is_final=True: skip to scoring (for final evaluation only)
    """
    # If is_final, skip to scoring
    if state.is_final:
        if len(state.current_arguments) == 0:
            raise ValueError("No current arguments to prepare final arguments")
        return "score_and_select_best_k"

    # If we have question_trees or all_qa_pairs, skip decomposition/answering
    if state.question_trees or state.all_qa_pairs:
        return "generate_pro_and_contra_arguments"

    # Otherwise, start from decomposition (company always has a default)
    return "decompose_questions"


def build_graph() -> StateGraph:
    """Build the investment story graph.

    Creates a StateGraph with all nodes and edges for the
    full investment analysis pipeline, from decomposition to decision.

    The graph uses InputState as the input schema (for langgraph.dev)
    and IterativeInvestmentStoryState as the full state schema.

    Returns:
        Compiled StateGraph ready for invocation.
    """
    builder = StateGraph(
        state_schema=IterativeInvestmentStoryState,
        input=InputState,
    )

    # Stage 1: Parallel decomposition of 4 investment questions
    builder.add_node("decompose_questions", decompose_all_questions)

    # Stage 2: Parallel answering of all question trees
    builder.add_node("answer_questions", answer_all_trees)

    # Stage 3: Generate arguments
    builder.add_node("generate_pro_arguments", generate_pro_arguments)
    builder.add_node("generate_contra_arguments", generate_contra_arguments)
    builder.add_node("generate_pro_and_contra_arguments", generate_pro_and_contra_arguments)
    builder.add_node("merge_arguments", merge_arguments)

    # Stage 4: Critique arguments
    builder.add_node("apply_devils_advocate", apply_devils_advocate)
    builder.add_node(
        "apply_devils_advocate_to_pro_arguments", apply_devils_advocate_to_pro_arguments
    )
    builder.add_node(
        "apply_devils_advocate_to_contra_arguments",
        apply_devils_advocate_to_contra_arguments,
    )

    # Stage 5: Evaluate arguments
    builder.add_node("score_and_select_best_k", score_and_select_best_k)

    # Stage 6: Refine arguments
    builder.add_node("refine_pro_arguments", refine_pro_arguments)
    builder.add_node("refine_contra_arguments", refine_contra_arguments)
    builder.add_node("merge_refined_arguments", merge_refined_arguments)

    # Stage 7: Decision
    builder.add_node("add_arguments_to_history", add_arguments_to_history)
    builder.add_node(
        "reset_arguments_and_increment_iteration", reset_arguments_and_increment_iteration
    )
    builder.add_node("prepare_final_arguments", prepare_final_arguments)
    builder.add_node("decide_final_investment_decision", decide_final_investment_decision)
    builder.add_node("create_final_investment_story", create_final_investment_story)

    # === EDGES ===

    # 1. Conditional start - check where to begin
    builder.add_conditional_edges(START, check_start_point)

    # 2. Decomposition -> Answering
    builder.add_edge("decompose_questions", "answer_questions")

    # 3. Answering -> Argument generation
    builder.add_edge("answer_questions", "generate_pro_and_contra_arguments")

    # 4. Generate pro and contra arguments (parallel)
    builder.add_edge("generate_pro_and_contra_arguments", "generate_pro_arguments")
    builder.add_edge("generate_pro_and_contra_arguments", "generate_contra_arguments")

    # 5. Merge pro and contra arguments
    builder.add_edge("generate_contra_arguments", "merge_arguments")
    builder.add_edge("generate_pro_arguments", "merge_arguments")

    # 6. Apply devil's advocate (parallel)
    builder.add_edge("merge_arguments", "apply_devils_advocate")
    builder.add_edge("apply_devils_advocate", "apply_devils_advocate_to_pro_arguments")
    builder.add_edge("apply_devils_advocate", "apply_devils_advocate_to_contra_arguments")

    # 7. Score and select best k arguments
    builder.add_edge("apply_devils_advocate_to_pro_arguments", "score_and_select_best_k")
    builder.add_edge("apply_devils_advocate_to_contra_arguments", "score_and_select_best_k")

    # 8. Refine arguments (parallel)
    builder.add_edge("score_and_select_best_k", "refine_contra_arguments")
    builder.add_edge("score_and_select_best_k", "refine_pro_arguments")

    # 9. Merge refined arguments
    builder.add_edge("refine_pro_arguments", "merge_refined_arguments")
    builder.add_edge("refine_contra_arguments", "merge_refined_arguments")

    # 10. Add arguments to history
    builder.add_edge("merge_refined_arguments", "add_arguments_to_history")

    # 11. Reset arguments and increment iteration
    builder.add_edge("add_arguments_to_history", "reset_arguments_and_increment_iteration")

    # 12. Conditional routing: continue iterations or prepare final arguments
    builder.add_conditional_edges("reset_arguments_and_increment_iteration", check_continue)

    # 13. Prepare final arguments and create final story
    builder.add_edge("prepare_final_arguments", "decide_final_investment_decision")
    builder.add_edge("decide_final_investment_decision", "create_final_investment_story")
    builder.add_edge("create_final_investment_story", END)

    return builder


# Compile the graph
graph = build_graph().compile()


async def main() -> None:
    """Entry point for running the investment story pipeline.

    Runs the full pipeline starting from company input:
    1. Decompose 4 investment questions
    2. Answer all question trees
    3. Generate and refine arguments
    4. Make final investment decision
    """
    from agent.dataclasses.examples import BRANDBACK_COMPANY

    try:
        # Start from company - the pipeline will handle everything
        initial_state = IterativeInvestmentStoryState(
            company=BRANDBACK_COMPANY,
            config=Config(
                n_pro_arguments=3,
                n_contra_arguments=3,
                k_best_arguments_per_iteration=[5, 4],
                max_iterations=2,
            ),
        )

        print("=" * 70)
        print(f"Starting investment analysis for: {BRANDBACK_COMPANY.name}")
        print(f"Industry: {BRANDBACK_COMPANY.industry}")
        print("=" * 70)

        final_state: IterativeInvestmentStoryState = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": 100},
        )

        display_results(final_state)

    except Exception as e:
        print(f"Error running iterative investment story: {e}")
        raise


def display_results(final_state) -> None:
    """Pretty-print the pipeline results.

    Shows configuration, iteration history, and final decision.
    """
    print("\n=== CONFIGURATION ===")
    print(
        f"Pro/Contra arguments: {final_state['config'].n_pro_arguments}/{final_state['config'].n_contra_arguments}"
    )
    print(f"K best per iteration: {final_state['config'].k_best_arguments_per_iteration}")
    print(f"Max iterations: {final_state['config'].max_iterations}")

    print("\n=== ITERATION HISTORY ===")
    for i, iteration_data in enumerate(final_state["arguments_history"]):
        print(f"\n ITERATION {i + 1}")
        print("-" * 70)

        selected_args = iteration_data.get("selected_arguments", [])
        refined_pro_args = iteration_data.get("refined_pro_arguments", [])
        refined_contra_args = iteration_data.get("refined_contra_arguments", [])

        # Create mapping from selected to refined arguments
        refined_args_map = {}
        for arg in refined_pro_args + refined_contra_args:
            for sel_arg in selected_args:
                if sel_arg.id == arg.id:
                    refined_args_map[sel_arg.id] = arg
                    break

        # Display each selected argument with its transformation
        for idx, selected_arg in enumerate(selected_args):
            refined_arg = refined_args_map.get(selected_arg.id, selected_arg)

            print(f"\n Argument {idx + 1} ({selected_arg.argument_type.upper()}):")
            print(f"  TRACKING ID: {selected_arg.tracking_id}")
            print(f"  ORIGINAL: {selected_arg.content}")
            print(
                f"  CRITIQUE: {selected_arg.critique if selected_arg.critique else '[No critique]'}"
            )
            print(
                f"  REFINED: {refined_arg.refined_content if hasattr(refined_arg, 'refined_content') and refined_arg.refined_content else selected_arg.content}"
            )
            print(f"  Score: {selected_arg.score:.1f}")

        print("\n")

    print("\n=== FINAL ARGUMENTS ===")
    final_arguments = final_state.get("final_arguments", [])

    if final_arguments:
        print(f"Total final arguments: {len(final_arguments)}")
        for i, arg in enumerate(final_arguments):
            content = arg.refined_content if arg.refined_content else arg.content
            print(f"\n{i + 1}. {arg.argument_type.upper()} (Score: {arg.score:.1f}):")
            print(f"   {content}")
    else:
        print("No final arguments found!")

    print("\n=== SUMMARY ===")
    print(
        f"Iterations completed: {final_state.get('current_iteration', 0)}/{final_state['config'].max_iterations}"
    )
    print(f"Final decision: {final_state.get('final_decision', 'Not determined')}")


if __name__ == "__main__":
    asyncio.run(main())
