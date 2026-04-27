---
name: dialectic
description: Run a DIALECTIC investment analysis on any startup. Asks for company info, runs a multi-agent LLM pipeline (decomposition → argument generation → devil's advocate critique → refinement × 2 iterations), and presents pro/con arguments with an investment recommendation. Based on the EACL 2026 research paper.
---

You are running the DIALECTIC investment analysis pipeline. Follow these steps exactly.

## Step 1: Collect Company Information

Ask the user for the following, one message at a time (or all at once if they've already provided some):

1. **Startup name** — What is the company called?
2. **What it does** — Describe the product or service in 1-2 sentences.
3. **Industry** — What sector or industry? (e.g. FinTech, HealthTech, B2B SaaS)
4. **Website or additional context** — URL, founding year, funding stage, team info — anything relevant. (optional, press enter to skip)

After collecting, confirm with the user:

> "Got it. Here's what I have:
> - **Name**: [name]
> - **What it does**: [about]
> - **Industry**: [industry]
> - **Additional context**: [website/extra or 'none']
>
> Ready to run the analysis?"

## Step 2: Ask for Output Verbosity

Ask:

> "How would you like the results presented?
> 1. **Summary** (recommended) — Top arguments + investment recommendation
> 2. **Detailed** — Full iteration history with critiques and refinements
>
> Enter 1 or 2:"

Store their choice.

## Step 3: Run the Analysis

Warn the user first:

> "This analysis takes 2–5 minutes to complete. The pipeline will decompose investment questions, search the web for information, generate pro/contra arguments, apply devil's advocate critiques, and refine the best arguments over 2 iterations. Starting now..."

Then run the pipeline using the Bash tool:

```bash
cd ~/.claude/skills/dialectic && uv run python -m agent.cli \
  --name "[STARTUP NAME]" \
  --about "[WHAT IT DOES]" \
  --industry "[INDUSTRY]" \
  --website "[WEBSITE/EXTRA IF PROVIDED]" \
  --extra "[ANY REMAINING EXTRA INFO]"
```

Omit `--website` and `--extra` flags if the user didn't provide that information.

The command outputs JSON to stdout. Capture it.

## Step 4: Present Results

Parse the JSON output and present results based on the user's verbosity choice.

### If Summary (choice 1):

Present in this format:

```
## DIALECTIC Analysis: [Company Name]

### Investment Arguments

**PRO** (reasons to invest)
1. [score/10] [refined_content or content of top pro argument]
2. [score/10] [second pro argument]
3. [score/10] [third pro argument]

**CON** (reasons to pass)
1. [score/10] [refined_content or content of top contra argument]
2. [score/10] [second contra argument]
3. [score/10] [third contra argument]

### Recommendation
**[INVEST / PASS]**

[Write a 2-3 sentence synthesis based on the balance of arguments, their scores, and the final_decision field. Be direct and specific to this startup.]
```

Sort arguments by score descending. Use `refined_content` if non-null, otherwise `content`. Show top 3 of each type.

### If Detailed (choice 2):

Show everything above, then add:

```
### Full Iteration History

**Iteration [N]:**
- **[PRO/CON]** Original: [content]
  - Critique: [critique]
  - Refined: [refined_content]
  - Score: [score]/10
```

Show all arguments from `arguments_history`, preserving iteration grouping.

## Step 5: Error Handling

If the Bash command exits with a non-zero status or outputs an error:

1. Show the error message clearly
2. Check if it mentions a missing API key — if so, say:
   > "It looks like an API key is missing. Open `~/.claude/skills/dialectic/.env` and add:
   > - `OPENAI_API_KEY` — from platform.openai.com
   > - `PPLX_API_KEY` — from perplexity.ai (or `BRAVE_API_KEY` from brave.com/search/api)"
3. Otherwise, show the raw error and suggest re-running.
