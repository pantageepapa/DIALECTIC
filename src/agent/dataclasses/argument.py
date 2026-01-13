import uuid
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Argument(BaseModel):
    """Argument model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tracking_id: str = Field(default="")
    content: str
    argument_type: Literal["pro", "contra"]
    qa_indices: list[int]
    qa_pairs: list[dict[str, str]] = Field(default_factory=list)
    score: int = 0
    percentile_score: float = 0.0
    argument_feedback: Optional[str] = None
    critique: Optional[str] = None
    refined_content: Optional[str] = None
    refined_qa_indices: Optional[list[int]] = None
    former_critique: Optional[str] = None