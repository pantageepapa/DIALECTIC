"""Internal CRM lookup for the 'internal' question tree.

This module replaces both the LLM-driven decomposition and the web-search
answering for the 'internal' aspect. It uses a hand-coded tree of 5
sub-questions and answers each via direct read-only MongoDB queries against
UVC's Salesforce-mirror database.

Read-only enforcement is double-layered:
- Atlas role: the Mongo user is configured with read-only privileges
- This module only ever calls find / count_documents / aggregate

Behaviour when the company is not in the CRM: the tree still gets built
and answered, but the answers honestly say 'not in CRM' so downstream
argument generation can use this signal.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any

from agent.dataclasses.company import Company
from agent.dataclasses.question_tree import QuestionNode, QuestionTree
from agent.pipeline.stages.constants import INVESTMENT_QUESTIONS

DB_NAME = "UVC_Master_DB"

# The 5 internal sub-questions (static, hand-coded)
INTERNAL_SUB_QUESTIONS: list[str] = [
    "Is the company already in our CRM, and what is the relationship history (owner, first/last contact, recent activity)?",
    "What is the pipeline status — any active or past investment opportunities (IOs)?",
    "Which founders or other contacts are recorded for this company in our CRM?",
    "Who at UVC or in our extended network has affinity connections to this company or its team?",
    "Are there portfolio companies or thesis-adjacent investments in adjacent industries already in our records?",
]


def _client():
    """Lazy-init pymongo client. Imported at call time to avoid hard dep."""
    from pymongo import MongoClient

    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "MONGODB_URI is not set. The 'internal' aspect requires a "
            "read-only MongoDB connection string in .env."
        )
    return MongoClient(uri, serverSelectionTimeoutMS=10000)


@lru_cache(maxsize=1)
def _db():
    return _client()[DB_NAME]


def is_enabled() -> bool:
    """Whether the internal aspect should run.

    Disabled if either MONGODB_URI is missing or INTERNAL_DATA_ENABLED=false.
    """
    if os.environ.get("INTERNAL_DATA_ENABLED", "true").lower() in ("false", "0", "no"):
        return False
    return bool(os.environ.get("MONGODB_URI"))


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def _find_account(company_name: str) -> dict | None:
    """Best-effort account match by name.

    Tries exact (case-insensitive) match first, then a regex prefix match.
    Returns None if no match found.
    """
    db = _db()
    coll = db["salesforce_accounts"]

    # Strip common legal suffixes for fuzzier matching
    stripped = re.sub(
        r"\b(AG|GmbH|Inc\.?|LLC|Ltd\.?|Limited|S\.?A\.?|B\.?V\.?|Oy)\b",
        "",
        company_name,
        flags=re.IGNORECASE,
    ).strip()

    # 1) exact match (case-insensitive)
    doc = coll.find_one({"Name": {"$regex": f"^{re.escape(stripped)}$", "$options": "i"}})
    if doc:
        return doc

    # 2) prefix match
    doc = coll.find_one({"Name": {"$regex": f"^{re.escape(stripped)}", "$options": "i"}})
    if doc:
        return doc

    # 3) substring match (last resort)
    doc = coll.find_one({"Name": {"$regex": re.escape(stripped), "$options": "i"}})
    return doc


def _resolve_user(user_id: str | None) -> str:
    """Map a Salesforce user id to a 'Name <email>' string."""
    if not user_id:
        return "unknown"
    user = _db()["salesforce_users"].find_one({"Id": user_id})
    if not user:
        return f"user:{user_id}"
    name = user.get("Name") or "unknown"
    email = user.get("Email") or ""
    return f"{name} <{email}>" if email else name


def _fmt_date(value: Any) -> str:
    if value in (None, ""):
        return "n/a"
    s = str(value)
    return s[:10] if len(s) >= 10 else s


# ---------------------------------------------------------------------------
# Per-question answerers
# ---------------------------------------------------------------------------


def _answer_relationship_history(account: dict | None, company_name: str) -> str:
    if not account:
        return (
            f"{company_name} is NOT in UVC's CRM. No prior relationship recorded — "
            "this would be a cold/new opportunity."
        )

    owner = _resolve_user(account.get("OwnerId"))
    name = account.get("Name", company_name)
    created = _fmt_date(account.get("CreatedDate"))
    first_meeting = _fmt_date(account.get("Affinity_First_Meeting__c"))
    last_meeting = _fmt_date(account.get("Affinity_Last_Meeting__c"))
    last_email = _fmt_date(account.get("Affinity_Last_Email__c"))
    last_activity = _fmt_date(account.get("LastActivityDate"))
    status = account.get("Account_Status__c") or "n/a"

    return (
        f"{name} is in UVC's CRM (account created {created}). "
        f"Owner: {owner}. Status: {status}. "
        f"First meeting: {first_meeting}; last meeting: {last_meeting}. "
        f"Last email: {last_email}. Last activity: {last_activity}."
    )


def _answer_pipeline_status(account: dict | None) -> str:
    if not account:
        return "No pipeline status — company not in CRM."

    db = _db()
    account_id = account["Id"]
    ios = list(
        db["salesforce_investment_opportunities"]
        .find({"Account__c": account_id})
        .sort("CreatedDate", -1)
        .limit(20)
    )
    fund_ios = list(
        db["salesforce_fund_investment_opportunities"]
        .find({"Account__c": account_id})
        .sort("CreatedDate", -1)
        .limit(20)
    )

    if not ios and not fund_ios:
        return (
            "No formal investment opportunity (IO) has been created for this "
            "company. It is being tracked as an account but has not progressed "
            "to a deal record."
        )

    parts: list[str] = []
    for io in ios:
        name = io.get("Name", "unknown")
        created = _fmt_date(io.get("CreatedDate"))
        last_status = io.get("Last_Status__c") or "n/a"
        comment = io.get("Fund_Comment__c") or io.get("Data_Team_Comment__c") or ""
        comment_snip = (comment[:120] + "…") if len(comment) > 120 else comment
        parts.append(
            f"IO {name} (created {created}, status: {last_status}"
            + (f", comment: \"{comment_snip}\"" if comment_snip else "")
            + ")"
        )
    for fio in fund_ios:
        parts.append(
            f"Fund IO {fio.get('Name', 'unknown')} (created {_fmt_date(fio.get('CreatedDate'))})"
        )
    return "Investment opportunities on file: " + "; ".join(parts) + "."


def _answer_contacts(account: dict | None) -> str:
    if not account:
        return "No contacts on file — company not in CRM."

    db = _db()
    account_id = account["Id"]
    relations = list(
        db["salesforce_account_contact_relations"]
        .find({"AccountId": account_id})
        .limit(20)
    )
    if not relations:
        return "No contacts linked to this account in our CRM."

    contacts: list[str] = []
    for rel in relations:
        contact_id = rel.get("ContactId")
        if not contact_id:
            continue
        c = db["salesforce_contacts"].find_one({"Id": contact_id})
        if not c:
            continue
        first = c.get("FirstName") or ""
        last = c.get("LastName") or ""
        title = c.get("Title") or ""
        email = c.get("Email") or ""
        roles = rel.get("Roles") or ""
        bits = [f"{first} {last}".strip()]
        if title:
            bits.append(title)
        if roles:
            bits.append(f"role: {roles}")
        if email:
            bits.append(email)
        contacts.append(" | ".join(bits))
    if not contacts:
        return "Linked contacts exist but contact records could not be resolved."
    return f"{len(contacts)} contact(s) linked to this account: " + "; ".join(contacts) + "."


def _answer_network(account: dict | None) -> str:
    if not account:
        return "No network signal — company not in CRM."

    db = _db()
    account_id = account["Id"]
    connections = list(
        db["salesforce_affinity_connections"]
        .find({"affinity__Account__c": account_id})
        .sort("affinity__Relationship_Score__c", -1)
        .limit(10)
    )
    if not connections:
        owner = _resolve_user(account.get("OwnerId"))
        return (
            f"No affinity connections recorded for this company beyond the "
            f"account owner ({owner})."
        )

    bits: list[str] = []
    for c in connections:
        ally = c.get("affinity__Ally_Name__c") or "unknown"
        email = c.get("affinity__Ally_Email__c") or ""
        score = c.get("affinity__Relationship_Score__c")
        score_str = f" (score: {score})" if score is not None else ""
        bits.append(f"{ally} <{email}>{score_str}")
    return f"{len(connections)} affinity connection(s) to this company in our network: " + "; ".join(bits) + "."


def _answer_portfolio_adjacency(account: dict | None, company: Company) -> str:
    """Find thesis-adjacent companies already in our records."""
    db = _db()

    # Use industry from the input company (it's free-text, so we tokenize)
    industry = (company.industry or "").lower()
    keywords: list[str] = []
    for kw in ["semiconductor", "chip", "edge ai", "in-memory", "robotics", "iot", "ai"]:
        if kw in industry or kw in (company.about or "").lower():
            keywords.append(kw)
    if not keywords and industry:
        keywords = [industry.split("/")[0].strip()]

    if not keywords:
        return "Could not determine industry keywords for adjacency search."

    # Find accounts whose Affinity_Industry__c matches any keyword AND that have
    # an associated IO (signal that we evaluated/invested in them)
    pattern = "|".join(re.escape(kw) for kw in keywords)
    similar = list(
        db["salesforce_accounts"].find(
            {
                "Affinity_Industry__c": {"$regex": pattern, "$options": "i"},
                "Id": {"$ne": account["Id"] if account else ""},
            },
            {"Id": 1, "Name": 1, "Affinity_Industry__c": 1, "Account_Status__c": 1},
        ).limit(50)
    )
    # Filter to those with at least one IO recorded
    with_ios: list[str] = []
    for s in similar:
        io_count = db["salesforce_investment_opportunities"].count_documents({"Account__c": s["Id"]})
        if io_count > 0:
            label = s.get("Name", "unknown")
            ind = s.get("Affinity_Industry__c") or ""
            with_ios.append(f"{label} ({ind})")
        if len(with_ios) >= 8:
            break

    if not with_ios:
        return (
            f"No thesis-adjacent companies (matching keywords: {', '.join(keywords)}) "
            "with investment opportunities found in our CRM."
        )
    return (
        f"Thesis-adjacent companies in our CRM (matching: {', '.join(keywords)}) "
        f"that have IOs on record: " + "; ".join(with_ios) + "."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_internal_question_tree() -> QuestionTree:
    """Return the static internal question tree (questions only — answers filled later)."""
    root = QuestionNode(
        question=INVESTMENT_QUESTIONS["internal"],
        sub_nodes=[QuestionNode(question=q, aspect="internal") for q in INTERNAL_SUB_QUESTIONS],
        aspect="internal",
    )
    return QuestionTree(aspect="internal", root_node=root)


def answer_internal_tree(tree: QuestionTree, company: Company) -> QuestionTree:
    """Fill in answers on every node of the internal tree using Mongo queries."""
    account = _find_account(company.name)

    answerers = [
        lambda: _answer_relationship_history(account, company.name),
        lambda: _answer_pipeline_status(account),
        lambda: _answer_contacts(account),
        lambda: _answer_network(account),
        lambda: _answer_portfolio_adjacency(account, company),
    ]

    sub_answers: list[str] = []
    for node, answerer in zip(tree.root_node.sub_nodes, answerers):
        try:
            answer = answerer()
        except Exception as exc:  # pragma: no cover — surfaces in node text
            answer = f"[internal lookup error: {type(exc).__name__}: {exc}]"
        node.answer = answer
        sub_answers.append(answer)

    # Synthesize root answer by concatenating leaf summaries
    if account:
        tree.root_node.answer = (
            f"UVC has prior records on {account.get('Name', company.name)}. "
            + " ".join(sub_answers)
        )
    else:
        tree.root_node.answer = (
            f"{company.name} is not present in UVC's CRM — this would be a "
            f"cold/new opportunity. "
            + " ".join(sub_answers)
        )
    return tree
