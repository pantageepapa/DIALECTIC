"""Synthesize answers for parent nodes from child answers.

Parent nodes have sub-questions that are already answered. This stage
combines those answers into a coherent summary without external research.

This is used for non-leaf nodes in the question tree where the answer
can be synthesized from the child Q&A pairs.
"""


from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from agent.common.llm_config import get_llm
from agent.dataclasses.company import Company
from agent.dataclasses.examples import BRANDBACK_COMPANY

SYSTEM_PROMPT = """
Answer using company summary and sub Q&A if provided. Keep answer concise (<50 words) with data backing.
"""

QUESTION_PROMPT = """
Question: {question}

Company summary: {company_summary}
{context_block}
"""


class AnswerState(BaseModel):
    """State for answering without tools (synthesis only)."""

    question: str

    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
    company: Company = Field(default_factory=lambda: BRANDBACK_COMPANY)
    qa_pairs: list[dict[str, str]] = Field(default_factory=list)
    answer: str | None = None
    vc_context: str = ""


# Initialize LLM
llm = get_llm(temperature=0.0)


def _generate_context_block(qa_pairs: list[dict[str, str]], vc_context: str) -> str:
    """Generate a context block from Q&A pairs and VC context."""
    if qa_pairs:
        formatted_pairs = "\n-----------------\n".join(
            [f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs]
        )
        context_block = f"\nSub questions and answers:\n{formatted_pairs}"
    else:
        context_block = ""

    if vc_context:
        context_block += f"\n\nVC Context:\n{vc_context}"

    return context_block


def answer_question(state: AnswerState) -> AnswerState:
    """Synthesize answer from child Q&A pairs.

    This generates a concise answer by combining information from
    the sub-question answers without making external tool calls.
    """
    if len(state.messages) == 0:
        state.messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=QUESTION_PROMPT.format(
                    question=state.question,
                    company_summary=state.company.get_company_summary(),
                    context_block=_generate_context_block(
                        state.qa_pairs, state.vc_context
                    ),
                )
            ),
        ]

    response = llm.invoke(state.messages)
    state.answer = response.content

    return state


# Build the graph
builder = StateGraph(AnswerState)

builder.add_node("answer_question", answer_question)

builder.add_edge(START, "answer_question")
builder.add_edge("answer_question", END)

graph = builder.compile()


if __name__ == "__main__":
    # Simple test
    simple_company = Company(
        name="TechStartup AI",
        industry="Artificial Intelligence",
        tagline="AI-powered automation for businesses",
        about="A startup building AI tools for business process automation.",
    )

    initial_state = AnswerState(
        question="What is the market size for AI-powered business automation?",
        company=simple_company,
    )

    result = graph.invoke(initial_state)
    print(f"Answer: {result['answer']}")
