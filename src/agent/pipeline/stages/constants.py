"""Investment question constants and type definitions.

This module defines the 4 predefined investment questions that form
the basis of the investment analysis pipeline.

The questions cover:
- General company alignment with VC strategy
- Market size and growth
- Product features and technology
- Team experience and track record
"""

from typing import Dict, Literal

# Type alias for question aspects
QuestionAspect = Literal["general_company", "market", "product", "team", "internal"]

# The 5 predefined investment questions
INVESTMENT_QUESTIONS: Dict[str, str] = {
    "general_company": (
        "Do the company's sector, development stage, and operating geography "
        "align with the VC's investment strategy?"
    ),
    "market": (
        "What is the current size, historical growth rate, and forecast growth "
        "of the target market and which specific customer needs or market gaps "
        "does the company address?"
    ),
    "product": (
        "What are the product's core features, underlying technology, and "
        "existing forms of protection?"
    ),
    "team": (
        "Who are the key members of the founding team, and what relevant "
        "experience and track record do they have?"
    ),
    "internal": (
        "Has the firm encountered this company or its founders before, and "
        "what does our internal CRM data say about pipeline status, network "
        "proximity, and portfolio fit?"
    ),
}


def get_question_for_aspect(aspect: QuestionAspect) -> str:
    """Get the predefined question for a given aspect.

    Args:
        aspect: The aspect of analysis

    Returns:
        The predefined question string

    Raises:
        KeyError: If aspect is not valid
    """
    return INVESTMENT_QUESTIONS[aspect]


def get_all_aspects() -> list[QuestionAspect]:
    """Get all valid question aspects."""
    return ["general_company", "market", "product", "team", "internal"]
