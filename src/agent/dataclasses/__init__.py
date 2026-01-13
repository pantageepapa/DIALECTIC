"""Data models and domain objects for the investment analysis system."""

from agent.dataclasses.argument import Argument
from agent.dataclasses.company import Company
from agent.dataclasses.config import Config
from agent.dataclasses.person import Person
from agent.dataclasses.question_tree import QuestionNode, QuestionTree

__all__ = [
    "Argument",
    "Company",
    "Config",
    "Person",
    "QuestionNode",
    "QuestionTree",
]
