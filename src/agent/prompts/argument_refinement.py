"""Prompts for refining arguments based on critique and evaluation."""

REFINE_PRO_ARGUMENT_SYSTEM_PROMPT = """You are a very experienced investor at a top‑tier VC fund. You are sure that the company is a good investment opportunity.
Your job is to revise your argument to reach better argument quality scores.
"""

REFINE_CONTRA_ARGUMENT_SYSTEM_PROMPT = """You are a very experienced investor at a top‑tier VC fund. You are sure that the company is a bad investment opportunity.
Your job is to revise your argument to reach better argument quality scores.
"""

REFINE_PRO_ARGUMENTS_USER_PROMPT = """Here are the Q&A facts about the company:
{questions_and_answers}

Here is your previous argument:
{argument}

Here are the argument quality scores (1-7) to your previous argument:
{argument_feedback}

Refine your argument by improving argument quality scores.

Output format:
{{
    "refined_argument": "Refined Argument without qa_indices (one paragraph in max. 2 sentences)",
    "qa_indices": "List of indices referencing which questions and answers from the provided Q&A pairs were used to support this argument"
}}
"""

REFINE_CONTRA_ARGUMENTS_USER_PROMPT = """Here are the Q&A facts about the company:
{questions_and_answers}

Here are the argument quality scores (1-7) to your previous argument:
{argument_feedback}

Here is your previous argument:
{argument}

Refine your argument by improving argument quality scores.

Output format:
{{
    "refined_argument": "Refined Argument without qa_indices (one paragraph in max. 2 sentences)",
    "qa_indices": "List of indices referencing which questions and answers from the provided Q&A pairs were used to support this argument"
}}
"""
