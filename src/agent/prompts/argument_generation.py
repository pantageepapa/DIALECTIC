"""Prompts for generating pro and contra investment arguments."""

ARGUMENT_GENERATION_SYSTEM_PROMPT = """You are a very experienced investor at a top‑tier VC fund. You are also a great storyteller and can tell a compelling story.

"""

PRO_ARGUMENTS_USER_PROMPT = """Generate {n_pro_arguments} pro arguments why this company is a good investment opportunity.

Each argument should be concise (max. 100 words) and backed by specific data from the questions and answers.

A good argument provides a unique perspective on the investment opportunity that addresses the following criteria:
1. Local Acceptability - Are the premises believable and factually plausible given the provided Q&A facts?
2. Local Relevance - Do the premises clearly contribute to supporting or rejecting the conclusion about investment?
3. Local Sufficiency - Do the premises provide enough support to justify the conclusion?
4. Cogency - Does the argument have premises that are acceptable, relevant, and sufficient to support the investment conclusion?
5. Credibility - Does the argument make the author appear credible and trustworthy to VC investors?
6. Emotional Appeal - Does the argument create emotions that make the VC investors more receptive?
7. Clarity - Does the argument use correct and widely unambiguous language as well as avoid deviation from the issue?
8. Appropriateness - Is the style of reasoning and language suitable for a professional VC investment discussion?
9. Arrangement - Is the argument well-structured, with a logical order of premises and conclusion?
10. Effectiveness - Does the argument succeed in persuading the VC investors toward or against investing?
11. Global Acceptability - Would most VCs consider it a valid/legitimate argument?
12. Global Relevance - Does the argument meaningfully contribute to resolving the overall investment question?
13. Global Sufficiency - Does the argument adequately anticipate and rebut the main counterarguments from the argument's stance?
14. Reasonableness - Does the argument resolve the issue in a way acceptable to the VC investors, balancing global acceptability, relevance, and sufficiency?

Here are the questions and answers about the company:
{questions_and_answers}

Provide the qa_indices that were used to generate the argument but never show them in the argument text.
"""

CONTRA_ARGUMENTS_USER_PROMPT = """Generate {n_contra_arguments} contra arguments why this company is a bad investment opportunity.

Each argument should be concise (2-3 sentences) and backed by specific data from the questions and answers.
Lack of data is not a good contra argument.

A good argument provides a unique perspective on the investment opportunity that addresses the following criteria:
1. Local Acceptability - Are the premises believable and factually plausible given the provided Q&A facts?
2. Local Relevance - Do the premises clearly contribute to supporting or rejecting the conclusion about investment?
3. Local Sufficiency - Do the premises provide enough support to justify the conclusion?
4. Cogency - Does the argument have premises that are acceptable, relevant, and sufficient to support the investment conclusion?
5. Credibility - Does the argument make the author appear credible and trustworthy to VC investors?
6. Emotional Appeal - Does the argument create emotions that make the VC investors more receptive?
7. Clarity - Does the argument use correct and widely unambiguous language as well as avoid deviation from the issue?
8. Appropriateness - Is the style of reasoning and language suitable for a professional VC investment discussion?
9. Arrangement - Is the argument well-structured, with a logical order of premises and conclusion?
10. Effectiveness - Does the argument succeed in persuading the VC investors toward or against investing?
11. Global Acceptability - Would most VCs consider it a valid/legitimate argument?
12. Global Relevance - Does the argument meaningfully contribute to resolving the overall investment question?
13. Global Sufficiency - Does the argument adequately anticipate and rebut the main counterarguments from the argument's stance?
14. Reasonableness - Does the argument resolve the issue in a way acceptable to the VC investors, balancing global acceptability, relevance, and sufficiency?

Here are the questions and answers about the company:
{questions_and_answers}

Provide the qa_indices that were used to generate the argument but never show them in the argument text.
"""
