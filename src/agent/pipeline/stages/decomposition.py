"""Stage 1: Decompose complex questions into hierarchical question trees.

This stage takes a high-level investment question and breaks it down into
a tree of sub-questions that can be answered individually.

Example:
    "What is the market opportunity?" ->
        - "What is the TAM?"
        - "What is the SAM?"
        - "What is the SOM?"

The decomposition uses an LLM to generate a hierarchical question tree (HQDT)
that captures all the sub-questions needed to fully answer the main question.
"""

import json
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent.common.llm_config import get_llm
from agent.dataclasses.question_tree import QuestionNode, QuestionTree

SYSTEM_PROMPT = """
You are good at decomposing a complex question into a hierarchical question decomposition tree (HQDT).
"""

DECOMPOSE_PROMPT = """
Please generate a hierarchical question decomposition tree (HQDT) with json format for a given question. In this tree, the root node is the original complex question, and each non-root node is a sub-question of its parent.

Q: How large is the company's market opportunity (TAM, SAM, SOM)?
A: {{
  "How large is the company's market opportunity (TAM, SAM, SOM)?": [
    "What is the Total Addressable Market (TAM)?",
    "What is the Serviceable Available Market (SAM)?",
    "What is the Serviceable Obtainable Market (SOM)?"
  ],
  "What is the Total Addressable Market (TAM)?": [
    "What customer segments are included in the broadest market?",
    "What is the total number of potential customers?",
    "What is the total industry revenue across those segments?"
  ],
  "What is the Serviceable Available Market (SAM)?": [
    "Which subset of TAM does the company's product or service directly target?",
    "What portion of customers can realistically be reached given geography, regulations, or product scope?",
    "What is the annual spending of these customers?"
  ],
  "What is the Serviceable Obtainable Market (SOM)?": [
    "What portion of SAM can the company realistically capture in the next 3–5 years?",
    "What customer acquisition assumptions support this share?",
    "What expected adoption rate drives this forecast?",
    "What annual revenue corresponds to this achievable market share?"
  ]
}}

Q: What is the competitive landscape, and how is the company positioned within it?
A: {{
  "What is the competitive landscape, and how is the company positioned within it?": [
    "What is the competitive landscape?",
    "How is the company positioned within the competitive landscape?"
  ],
  "What is the competitive landscape?": [
    "Who are the direct competitors?",
    "Who are the indirect competitors or substitutes?",
    "What are the major trends shaping competition in this space?"
  ],
  "How is the company positioned within the competitive landscape?": [
    "What is the company's relative pricing strategy?",
    "What is the company's market share or traction compared to peers?",
    "Does the company occupy a niche or broader category?",
    "What barriers to entry protect the company's position?"
  ]
}}

Q: What is the company's product differentiation and value proposition?
A: {{
  "What is the company's product differentiation and value proposition?": [
    "What is the company's product differentiation?",
    "What is the company's value proposition?"
  ],
  "What is the company's product differentiation?": [
    "What features or technologies distinguish the product?",
    "How is the product better than alternatives?",
    "What intellectual property (e.g., patents, proprietary tech) supports defensibility?"
  ],
  "What is the company's value proposition?": [
    "What problem does the product solve for customers?",
    "What measurable benefits (e.g., cost savings, time savings, revenue uplift) does it deliver?",
    "Why would customers choose this company over competitors?"
  ]
}}

Here is the question to decompose:
Q: {question}

Generate its HQDT customized for a company in the {industry} industry.
"""


class DecompositionNode(BaseModel):
    """A node in the decomposition tree."""

    question: str
    sub_questions: list[str]


class DecompositionTree(BaseModel):
    """The full decomposition tree from the LLM.

    Example structure:
    [
        {
            "question": "Main question",
            "sub_questions": ["Sub Q1", "Sub Q2"],
        },
        {
            "question": "Sub Q1",
            "sub_questions": ["Sub Q1a", "Sub Q1b"],
        }
    ]
    """

    nodes: list[DecompositionNode]


class DecompositionInput(BaseModel):
    """Input state for question decomposition."""

    industry: str | None = "AI marketing tools"
    question: str | None = "What is the current size and forecast growth of the target market?"
    aspect: Literal["general_company", "market", "product", "team"] | None = "general_company"


class DecompositionOutput(BaseModel):
    """Output state with the decomposed question tree."""

    question_tree: QuestionTree
    original_question: str


# Initialize LLM with structured output
llm = get_llm(temperature=0.5)
llm_with_structured_output = llm.with_structured_output(DecompositionTree)


def _build_question_tree_from_decomposition_tree(
    decomposition_tree: DecompositionTree,
    aspect: Literal["general_company", "market", "product", "team"] | None = "general_company",
) -> QuestionTree:
    """Build a hierarchical QuestionTree from the flat DecompositionTree.

    The algorithm works in two passes:
    1. Create a QuestionNode for every unique question
    2. Wire every node to its direct children, building the tree

    The first node in decomposition_tree.nodes is assumed to be the root.
    """
    # 1. Create mapping from question text to QuestionNode
    node_map: dict[str, QuestionNode] = {
        node.question: QuestionNode(question=node.question, sub_nodes=[], aspect=aspect)
        for node in decomposition_tree.nodes
    }

    # 2. Populate parent-child relationships
    for node in decomposition_tree.nodes:
        parent = node_map[node.question]
        for child_q in node.sub_questions:
            child_node = node_map.get(child_q)
            if child_node is None:
                # LLM returned a child we didn't see as standalone - create it
                child_node = QuestionNode(question=child_q, sub_nodes=[], aspect=aspect)
                node_map[child_q] = child_node
            parent.sub_nodes.append(child_node)

    # 3. Root is the first element
    root_question = decomposition_tree.nodes[0].question
    root_node = node_map[root_question]

    return QuestionTree(root_node=root_node, aspect=aspect)


def decompose_question(state: DecompositionInput) -> DecompositionOutput:
    """Decompose a complex question into a hierarchical question tree.

    Takes a high-level investment question and uses an LLM to break it
    down into a tree of sub-questions customized for the given industry.
    """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=DECOMPOSE_PROMPT.format(
                question=state.question, industry=state.industry
            )
        ),
    ]

    decomposition_tree: DecompositionTree = llm_with_structured_output.invoke(messages)

    question_tree: QuestionTree = _build_question_tree_from_decomposition_tree(
        decomposition_tree, state.aspect
    )

    return {
        "question_tree": question_tree,
        "original_question": state.question,
    }


# Build the graph
builder = StateGraph(DecompositionInput, output=DecompositionOutput)

builder.add_node("decompose", decompose_question)

builder.add_edge(START, "decompose")
builder.add_edge("decompose", END)

graph = builder.compile()


if __name__ == "__main__":
    messages = [
        HumanMessage(
            content=DECOMPOSE_PROMPT
            + "Q: Who are the key members of the founding team, and what relevant experience and track record do they have?\nA:"
        ),
    ]

    llm_output = llm.invoke(messages)
    print(json.dumps(llm_output.content, indent=4))
