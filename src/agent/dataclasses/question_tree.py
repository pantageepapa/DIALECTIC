from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

class QuestionNode(BaseModel):
    """A node in a hierarchical question tree."""

    question: str
    answer: Optional[str] = None
    sub_nodes: list[QuestionNode] = Field(default_factory=list)

    aspect: Optional[str] = None


class QuestionTree(BaseModel):
    """A hierarchical question tree with a single root node."""
    aspect: str
    root_node: QuestionNode
