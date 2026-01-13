"""Main LangGraph for iterative investment story generation.

This module defines and compiles the full investment analysis pipeline,
orchestrating all stages from argument generation to final decision.

Pipeline Flow:
    START
      |
      v
    [check_if_final] --- is_final ---> [score_and_select_best_k]
      |                                        |
      | not_final                              |
      v                                        |
    [generate_pro_arguments]  <----------------+
    [generate_contra_arguments]  (parallel)
      |
      v
    [merge_arguments]
      |
      v
    [apply_devils_advocate_to_pro]    (parallel)
    [apply_devils_advocate_to_contra]
      |
      v
    [score_and_select_best_k]
      |
      v
    [refine_pro_arguments]    (parallel)
    [refine_contra_arguments]
      |
      v
    [merge_refined_arguments]
      |
      v
    [add_arguments_to_history]
      |
      v
    [reset_and_increment_iteration]
      |
      v
    [check_continue] --- continue ---> [apply_devils_advocate...]
      |
      | finalize
      v
    [prepare_final_arguments]
      |
      v
    [decide_final_investment_decision]
      |
      v
    [create_final_investment_story]
      |
      v
    END
"""

import asyncio

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
from agent.pipeline.stages.refinement import (
    merge_refined_arguments,
    refine_contra_arguments,
    refine_pro_arguments,
)
from agent.pipeline.state.investment_story import IterativeInvestmentStoryState


def build_graph() -> StateGraph:
    """Build the investment story graph.

    Creates a StateGraph with all nodes and edges for the
    iterative argument refinement pipeline.

    Returns:
        Compiled StateGraph ready for invocation.
    """
    builder = StateGraph(state_schema=IterativeInvestmentStoryState)

    # Add nodes
    builder.add_node("generate_pro_arguments", generate_pro_arguments)
    builder.add_node("generate_contra_arguments", generate_contra_arguments)
    builder.add_node("generate_pro_and_contra_arguments", generate_pro_and_contra_arguments)
    builder.add_node("merge_arguments", merge_arguments)
    builder.add_node("apply_devils_advocate", apply_devils_advocate)
    builder.add_node("score_and_select_best_k", score_and_select_best_k)
    builder.add_node(
        "apply_devils_advocate_to_pro_arguments", apply_devils_advocate_to_pro_arguments
    )
    builder.add_node(
        "apply_devils_advocate_to_contra_arguments",
        apply_devils_advocate_to_contra_arguments,
    )
    builder.add_node("refine_pro_arguments", refine_pro_arguments)
    builder.add_node("refine_contra_arguments", refine_contra_arguments)
    builder.add_node("merge_refined_arguments", merge_refined_arguments)
    builder.add_node("add_arguments_to_history", add_arguments_to_history)
    builder.add_node(
        "reset_arguments_and_increment_iteration", reset_arguments_and_increment_iteration
    )
    builder.add_node("prepare_final_arguments", prepare_final_arguments)
    builder.add_node("decide_final_investment_decision", decide_final_investment_decision)
    builder.add_node("create_final_investment_story", create_final_investment_story)

    # 1. Conditional start - check if final
    builder.add_conditional_edges(START, check_if_final)

    # 2. Generate pro and contra arguments (parallel)
    builder.add_edge("generate_pro_and_contra_arguments", "generate_pro_arguments")
    builder.add_edge("generate_pro_and_contra_arguments", "generate_contra_arguments")

    # 3. Merge pro and contra arguments
    builder.add_edge("generate_contra_arguments", "merge_arguments")
    builder.add_edge("generate_pro_arguments", "merge_arguments")

    # 4. Apply devil's advocate (parallel)
    builder.add_edge("merge_arguments", "apply_devils_advocate")
    builder.add_edge("apply_devils_advocate", "apply_devils_advocate_to_pro_arguments")
    builder.add_edge("apply_devils_advocate", "apply_devils_advocate_to_contra_arguments")

    # 5. Score and select best k arguments
    builder.add_edge("apply_devils_advocate_to_pro_arguments", "score_and_select_best_k")
    builder.add_edge("apply_devils_advocate_to_contra_arguments", "score_and_select_best_k")

    # 6. Refine arguments (parallel)
    builder.add_edge("score_and_select_best_k", "refine_contra_arguments")
    builder.add_edge("score_and_select_best_k", "refine_pro_arguments")

    # 7. Merge refined arguments
    builder.add_edge("refine_pro_arguments", "merge_refined_arguments")
    builder.add_edge("refine_contra_arguments", "merge_refined_arguments")

    # 8. Add arguments to history
    builder.add_edge("merge_refined_arguments", "add_arguments_to_history")

    # 9. Reset arguments and increment iteration
    builder.add_edge("add_arguments_to_history", "reset_arguments_and_increment_iteration")

    # 10. Conditional routing: continue iterations or prepare final arguments
    builder.add_conditional_edges("reset_arguments_and_increment_iteration", check_continue)

    # 11. Prepare final arguments and create final story
    builder.add_edge("prepare_final_arguments", "decide_final_investment_decision")
    builder.add_edge("decide_final_investment_decision", "create_final_investment_story")
    builder.add_edge("create_final_investment_story", END)

    return builder


# Compile the graph
graph = build_graph().compile()


async def main() -> None:
    """Entry point for running the investment story pipeline.

    Uses a cached question tree for demonstration.
    """
    from agent.cached_answered_question_trees import get_retable_answered_question_tree

    try:
        initial_state = IterativeInvestmentStoryState(
            question_tree=get_retable_answered_question_tree(),
            config=Config(
                n_pro_arguments=1,
                n_contra_arguments=1,
                k_best_arguments_per_iteration=[2, 2],
                max_iterations=2,
            ),
        )

        final_state: IterativeInvestmentStoryState = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": 50},
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
