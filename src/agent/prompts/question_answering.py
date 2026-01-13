"""Prompts for question decomposition and answering."""

# Question Decomposition Prompts
DECOMPOSE_SYSTEM_PROMPT = """
You are good at decomposing a complex question into a hierarchical question decomposition tree (HQDT).
"""

DECOMPOSE_QUESTION_PROMPT = """
Please generate a hierarchical question decomposition tree (HQDT) with json format for a given question. In this tree, the root node is the original complex question, and each non-root node is a sub-question of its parent.

Q: How large is the company's market opportunity (TAM, SAM, SOM)?
A: {{
  "How large is the company's market opportunity (TAM, SAM, SOM)?": [
    "What is the Total Addressable Market (TAM)?",
    "What is the Serviceable Available Market (SAM)?",
    "What is the Serviceable Obtainable Market (SOM)?"
  ],
  "What is the Total Addressable Market (TAM)?": [
    "What customer segments are included in the broadest market?",
    "What is the total number of potential customers?",
    "What is the total industry revenue across those segments?"
  ],
  "What is the Serviceable Available Market (SAM)?": [
    "Which subset of TAM does the company's product or service directly target?",
    "What portion of customers can realistically be reached given geography, regulations, or product scope?",
    "What is the annual spending of these customers?"
  ],
  "What is the Serviceable Obtainable Market (SOM)?": [
    "What portion of SAM can the company realistically capture in the next 3–5 years?",
    "What customer acquisition assumptions support this share?",
    "What expected adoption rate drives this forecast?",
    "What annual revenue corresponds to this achievable market share?"
  ]
}}

Q: What is the competitive landscape, and how is the company positioned within it?
A: {{
  "What is the competitive landscape, and how is the company positioned within it?": [
    "What is the competitive landscape?",
    "How is the company positioned within the competitive landscape?"
  ],
  "What is the competitive landscape?": [
    "Who are the direct competitors?",
    "Who are the indirect competitors or substitutes?",
    "What are the major trends shaping competition in this space?"
  ],
  "How is the company positioned within the competitive landscape?": [
    "What is the company's relative pricing strategy?",
    "What is the company's market share or traction compared to peers?",
    "Does the company occupy a niche or broader category?",
    "What barriers to entry protect the company's position?"
  ]
}}

Q: What is the company's product differentiation and value proposition?
A: {{
  "What is the company's product differentiation and value proposition?": [
    "What is the company's product differentiation?",
    "What is the company's value proposition?"
  ],
  "What is the company's product differentiation?": [
    "What features or technologies distinguish the product?",
    "How is the product better than alternatives?",
    "What intellectual property (e.g., patents, proprietary tech) supports defensibility?"
  ],
  "What is the company's value proposition?": [
    "What problem does the product solve for customers?",
    "What measurable benefits (e.g., cost savings, time savings, revenue uplift) does it deliver?",
    "Why would customers choose this company over competitors?"
  ]
}}

Here is the question to decompose:
Q: {question}

Generate its HQDT customized for a company in the {industry} industry.
"""

# Question Answering Prompts (with tool)
ANSWER_WITH_TOOL_SYSTEM_PROMPT = """
Answer the question using company summary and sub Q&A if provided. Keep answer concise (<50 words) with data backing.
If unable to answer the question, use web_search for market data, trends, competitive analysis, funding info. Focus on industry-level searches, not specific companies. Use the tool only if necessary.
Make ONE tool call at a time.
"""

# Question Answering Prompts (without tool)
ANSWER_WITHOUT_TOOL_SYSTEM_PROMPT = """
Answer using company summary and sub Q&A if provided. Keep answer concise (<50 words) with data backing.
"""

# Common question prompt template
ANSWER_QUESTION_PROMPT = """
Question: {question}

Company summary: {company_summary}
{context_block}
"""
