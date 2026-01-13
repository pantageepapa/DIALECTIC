from typing import Any, Dict, Literal, Optional

from agent.common.cache import get, set
from agent.dataclasses.company import Company
from agent.dataclasses.question_tree import QuestionTree
from agent.pipeline.stages.decomposition import DecompositionInput
from agent.pipeline.stages.decomposition import graph as decompose_question_graph

# Helper
CACHE_NAME = "question_trees.json"


def _get_question_tree(question: str, company: Company, aspect: Optional[Literal["general_company", "market", "product", "team"]] = "general_company") -> QuestionTree:
    """Return cached QuestionTree or fetch via API and cache the result."""
    cache_key = f"{question}_{company.name}"
    cached = get(cache_key, CACHE_NAME)
    if cached is not None:
        # Cached JSON → dataclass
        return QuestionTree(**cached)

    result: QuestionTree = decompose_question_graph.invoke(
        DecompositionInput(question=question, industry=company.industry, aspect=aspect)
    )["question_tree"]

    # dataclass → JSON-serialisable dict
    question_tree_dict: Dict[str, Any] = result.model_dump()
    set(cache_key, question_tree_dict, CACHE_NAME)
    return result


# Question constants
GENERAL_COMPANY_QUESTION = (
    "Do the company's sector, development stage, and operating geography align with the VC's investment strategy?"
)
MARKET_QUESTION = "What is the current size, historical growth rate, and forecast growth of the target market and which specific customer needs or market gaps does the company address?"
PRODUCT_QUESTION = "What are the product's core features, underlying technology, and existing forms of protection?"
TEAM_QUESTION = "Who are the key members of the founding team, and what relevant experience and track record do they have?"

def get_company_question_trees(company: Company) -> Dict[str, QuestionTree]:
    """Get all question trees for a specific company, customized for their industry."""
    return {
        "general_company": _get_question_tree(GENERAL_COMPANY_QUESTION, company, "general_company"),
        "market": _get_question_tree(MARKET_QUESTION, company, "market"),
        "product": _get_question_tree(PRODUCT_QUESTION, company, "product"),
        "team": _get_question_tree(TEAM_QUESTION, company, "team"),
    }


def get_general_company_question_tree(company: Company) -> QuestionTree:
    """Get the general company question tree for a specific company."""
    return _get_question_tree(GENERAL_COMPANY_QUESTION, company, "general_company")


def get_market_question_tree(company: Company) -> QuestionTree:
    """Get the market question tree for a specific company."""
    return _get_question_tree(MARKET_QUESTION, company, "market")


def get_product_question_tree(company: Company) -> QuestionTree:
    """Get the product question tree for a specific company."""
    return _get_question_tree(PRODUCT_QUESTION, company, "product")


def get_team_question_tree(company: Company) -> QuestionTree:
    """Get the team question tree for a specific company."""
    return _get_question_tree(TEAM_QUESTION, company, "team")


if __name__ == "__main__":
    from agent.dataclasses.examples import BRANDBACK_COMPANY
    
    team_question_tree = get_team_question_tree(BRANDBACK_COMPANY)
    print(team_question_tree)
