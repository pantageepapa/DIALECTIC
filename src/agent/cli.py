"""CLI entry point for the DIALECTIC investment analysis pipeline.

Usage:
    uv run python -m agent.cli --name "Acme AI" --about "AI for supply chain" \
        --industry "Logistics" --website "acme.ai" --extra "Founded 2022"
"""

import argparse
import asyncio
import json
import os
import sys


def validate_env() -> None:
    """Exit early with a clear message if required API keys are missing."""
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Error: OPENAI_API_KEY not set. "
            "Add it to ~/.claude/skills/dialectic/.env",
            file=sys.stderr,
        )
        sys.exit(1)

    has_search_key = os.getenv("PPLX_API_KEY") or os.getenv("BRAVE_SEARCH_API_KEY")
    if not has_search_key:
        print(
            "Error: No search API key set. "
            "Add PPLX_API_KEY or BRAVE_SEARCH_API_KEY to ~/.claude/skills/dialectic/.env",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run DIALECTIC investment analysis pipeline"
    )
    parser.add_argument("--name", required=True, help="Startup name")
    parser.add_argument("--about", required=True, help="What the startup does")
    parser.add_argument("--industry", default=None, help="Industry / sector")
    parser.add_argument("--website", default=None, help="Website or additional context")
    parser.add_argument("--extra", default=None, help="Any extra information")
    return parser.parse_args()


async def run(args: argparse.Namespace) -> dict:
    from dotenv import load_dotenv

    load_dotenv()

    from agent.dataclasses.company import Company
    from agent.dataclasses.config import Config
    from agent.pipeline.graph import graph
    from agent.pipeline.state.investment_story import IterativeInvestmentStoryState

    about_parts = [args.about]
    if args.website:
        about_parts.append(f"Website: {args.website}")
    if args.extra:
        about_parts.append(args.extra)

    company = Company(
        name=args.name,
        industry=args.industry,
        about=" | ".join(about_parts),
    )

    initial_state = IterativeInvestmentStoryState(
        company=company,
        config=Config(
            n_pro_arguments=3,
            n_contra_arguments=3,
            k_best_arguments_per_iteration=[5, 3],
            max_iterations=2,
        ),
    )

    final_state: IterativeInvestmentStoryState = await graph.ainvoke(
        initial_state,
        config={"recursion_limit": 100},
    )

    final_arguments = [
        {
            "type": arg.argument_type,
            "content": arg.content,
            "refined_content": arg.refined_content,
            "score": arg.score,
        }
        for arg in (final_state.get("final_arguments") or [])
    ]

    history = []
    for iteration in final_state.get("arguments_history") or []:
        selected = iteration.get("selected_arguments", [])
        refined_pro = {a.id: a for a in iteration.get("refined_pro_arguments", [])}
        refined_contra = {a.id: a for a in iteration.get("refined_contra_arguments", [])}
        history.append([
            {
                "type": arg.argument_type,
                "content": arg.content,
                "critique": arg.critique,
                "refined_content": (
                    refined_pro.get(arg.id) or refined_contra.get(arg.id) or arg
                ).refined_content,
                "score": arg.score,
            }
            for arg in selected
        ])

    def _node_to_dict(node) -> dict:
        return {
            "question": node.question,
            "answer": node.answer,
            "aspect": node.aspect,
            "sub_nodes": [_node_to_dict(child) for child in node.sub_nodes],
        }

    question_trees_out = {}
    for aspect, tree in (final_state.get("question_trees") or {}).items():
        question_trees_out[aspect] = {
            "aspect": tree.aspect,
            "root": _node_to_dict(tree.root_node),
        }

    return {
        "company": args.name,
        "final_decision": final_state.get("final_decision", "undetermined"),
        "final_arguments": final_arguments,
        "arguments_history": history,
        "question_trees": question_trees_out,
        "all_qa_pairs": final_state.get("all_qa_pairs") or [],
        "iterations_completed": final_state.get("current_iteration", 0),
    }


def main() -> None:
    validate_env()
    args = parse_args()
    try:
        result = asyncio.run(run(args))
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
