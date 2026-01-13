"""State classes for question answering stages.

These state classes are used by the answering subgraphs to track
the question being answered, context, and tool usage.
"""

from datetime import datetime

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from agent.dataclasses.company import Company
from agent.dataclasses.examples import BRANDBACK_COMPANY
from agent.dataclasses.question_tree import QuestionTree


class AnswerState(BaseModel):
    """State for answering a single question with tool support.

    Used by the with_tool answering stage for leaf nodes that
    may require web search to find answers.
    """

    question: str
    is_backtesting: bool | None = False
    search_end_date: str | None = None

    # Domain-specific fields
    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
    company: Company = Field(default_factory=lambda: BRANDBACK_COMPANY)
    qa_pairs: list[dict[str, str]] = Field(default_factory=list)
    answer: str | None = None
    vc_context: str = ""

    # Tool usage tracking
    tool_usage_count: int = 0
    max_tool_usage: int = 1

    def model_post_init(self, __context):
        """Set search_end_date automatically for non-backtesting mode."""
        if not self.is_backtesting and not self.search_end_date:
            self.search_end_date = datetime.now().strftime("%Y-%m-%d")

        if self.is_backtesting and not self.search_end_date:
            self.search_end_date = datetime(year=2022, month=1, day=24).strftime(
                "%Y-%m-%d"
            )


class AnswerStateSimple(BaseModel):
    """State for answering without tools (synthesis only).

    Used by the without_tool answering stage for parent nodes that
    synthesize answers from their children's Q&A pairs.
    """

    question: str

    # Domain-specific fields
    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
    company: Company = Field(default_factory=lambda: BRANDBACK_COMPANY)
    qa_pairs: list[dict[str, str]] = Field(default_factory=list)
    answer: str | None = None
    vc_context: str = ""


class AnswerQuestionTreeState(BaseModel):
    """State for answering an entire question tree.

    Used by the tree answering stage to recursively answer
    all questions from leaves to root.
    """

    question_tree: QuestionTree
    company: Company = BRANDBACK_COMPANY
    vc_context: str | None = None

    is_backtesting: bool | None = False
    search_end_date: str | None = None
