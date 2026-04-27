---
name: dialectic
description: Run a DIALECTIC investment analysis on any startup. Asks for company info (auto-filled via website scrape), optionally extracts founder data from LinkedIn screenshots, runs a multi-agent LLM pipeline (decomposition → argument generation → devil's advocate critique → refinement × 2 iterations), and presents pro/con arguments with an investment recommendation. Based on the EACL 2026 research paper.
---

You are running the DIALECTIC investment analysis pipeline. The base directory for this skill is provided in your invocation context as `Base directory for this skill: <path>`. Read that path and store it as `SKILL_BASE_DIR` — you will use it directly when running the pipeline.

Follow these steps exactly.

## Step 1: Collect Company Information

### 1a. Ask for website first

Ask:

> "What's the startup's website? I'll auto-fill the company info from it.
> (or type **skip** to enter details manually)"

**If the user provides a URL:**

Use the WebFetch tool to fetch the page. Extract the following fields from the content:
- **name** — the company name
- **about** — what the product or service does (1-2 sentences)
- **industry** — the sector or domain (e.g. FinTech, HealthTech, B2B SaaS)
- **tagline** — a short marketing phrase if present (optional)

**Content quality check:** If the fetched content is empty, contains only navigation/footer/cookie-consent text, or has fewer than 50 characters of substantive company description, tell the user the site couldn't be read and fall through to manual entry (Step 1b).

**If scrape succeeds**, display a confirmation card:

> "Here's what I found — does this look right? Edit anything below or type **yes** to confirm:
>
> - **Name**: [extracted name]
> - **What it does**: [extracted about]
> - **Industry**: [extracted industry]
> - **Tagline**: [extracted tagline or 'none']"

Wait for the user's response:
- If they type **yes** (or confirm): store the values and proceed to Step 2.
- If they correct any field (e.g. "industry is HealthTech"): update that field, re-display the full card, and ask again. Loop until confirmed.

### 1b. Manual entry fallback

Use this path when: (a) the user types **skip**, or (b) the scrape returned empty/useless content.

Ask for each field, one at a time (or accept all at once if already provided):

1. **Startup name** — What is the company called?
2. **What it does** — Describe the product or service in 1-2 sentences.
3. **Industry** — What sector or industry? (e.g. FinTech, HealthTech, B2B SaaS)

After collecting all three, display the same confirmation card format as above and wait for confirmation or corrections before proceeding.

## Step 2: Collect Team Information

After company info is confirmed, ask:

> "Want to add founder/team info? This powers the team evaluation dimension.
> 1. Upload LinkedIn screenshot(s)
> 2. Enter manually
> 3. Skip"

### Option 1: LinkedIn screenshots

Ask the user to upload the first LinkedIn profile screenshot.

**For each screenshot uploaded:**

Read the image using your vision capability and extract the following fields into a Person record:
- **name** — full name from the profile header
- **city** — city of residence if shown
- **country_code** — two-letter country code if location is shown (e.g. "US", "DE")
- **about** — the bio/summary section text if shown; if not shown, infer a 1-2 sentence summary from the headline, job titles, and experience visible in the screenshot
- **education** — list of entries, each with: institution name, start year, end year (mark as "not visible" if section not shown)
- **experience** — list of entries, each with: company, title, date range, description (mark as "not visible" if section not shown)
- **followers** — follower count if visible
- **connections** — connection count if visible

Mark fields not visible and not inferable as absent. Always infer **about** from available context rather than leaving it blank.

**Display a confirmation card for each person:**

> "**Founder: [name]**
> Location: [city, country_code or 'not shown']
> Education: [institution (years); institution (years); ...]
> Experience: [title at company (dates); title at company (dates); ...]
> About: "[about excerpt]"
> Followers: [count or 'not shown'] | Connections: [count or 'not shown']
>
> Does this look right? Correct any field or type **yes** to confirm."

If the user corrects a field: update it, re-display the full card, and ask again. Loop until confirmed.

After confirming each person, ask:

> "Another founder? Upload the next screenshot or type **done**."

Continue extracting and confirming until the user types **done**.

**Final team summary:** After all founders are confirmed, display:

> "**Team confirmed:**
> 1. [name] — [title at most recent company], [education institution]
> 2. [name] — [title at most recent company], [education institution]
> ..."

Then proceed to Step 3.

**Synthesizing team data for the pipeline:**

Format each confirmed Person as follows (matching `Person.get_profile_summary()` text structure):

```
Name: [name]
Location: [city], [country_code]
About: [about]
Education:
- [institution] ([start_year]–[end_year])
Experience:
- [title] at [company] ([start_date]–[end_date]): [description]
Followers: [followers] | Connections: [connections]
```

If multiple founders, join their formatted summaries with `---` on its own line between each person.

Pass the combined text as the `--extra` argument to the pipeline CLI.

### Option 2: Manual team entry

Ask for each founder one at a time:

> "Name and background for founder 1? (e.g. Alice Chen, Stanford CS 2019, ex-Google PM)"

After each entry, ask: "Another founder? Enter their info or type **done**."

Format each response as a Person summary (same structure as above, filling in what the user provided) and join with `---` for the `--extra` argument.

### Option 3: Skip

Proceed to Step 3 without any team data. Omit the `--extra` flag when running the pipeline.

## Step 3: Run the Analysis

Warn the user first:

> "This analysis takes up to 10 minutes to complete. The pipeline will decompose investment questions, search the web for information, generate pro/contra arguments, apply devil's advocate critiques, and refine the best arguments over 2 iterations. Starting now..."

Then run the pipeline using the Bash tool with a **10-minute timeout**. Use `SKILL_BASE_DIR` from your invocation context directly — do not search the filesystem:

```bash
cd "[SKILL_BASE_DIR]" && uv run python -m agent.cli \
  --name "[STARTUP NAME]" \
  --about "[WHAT IT DOES]" \
  --industry "[INDUSTRY]" \
  --website "[WEBSITE URL IF PROVIDED]" \
  --extra "[TEAM SUMMARY TEXT IF COLLECTED]"
```

Omit `--website` if the user didn't provide a URL. Omit `--extra` if the user skipped team info.

The command outputs JSON to stdout. Capture it.

## Step 4: Present Results

**Formatting each argument:** Extract a short bold headline (5–10 words capturing the core claim) from the argument text, then show the full `content` beneath it. Sort by score descending. Show top 3 pro and top 3 contra from `final_arguments`.

Present results in this format:

```
## DIALECTIC Analysis: [Company Name]

### Investment Arguments

**PRO** (reasons to invest)

1. [score/100] **[Bold 5–10 word headline]**
   [Full argument text — refined_content if non-null, otherwise content]

2. [score/100] **[Bold headline]**
   [Full argument text]

3. [score/100] **[Bold headline]**
   [Full argument text]

**CON** (reasons to pass)

1. [score/100] **[Bold 5–10 word headline]**
   [Full argument text]

2. [score/100] **[Bold headline]**
   [Full argument text]

3. [score/100] **[Bold headline]**
   [Full argument text]

### Recommendation
**[INVEST / PASS]**

[One sentence stating the decision and citing the single strongest argument verbatim or closely paraphrased. Do not argue against it or qualify it — just state it as the deciding factor.]
```

## Step 5: Error Handling

If the Bash command exits with a non-zero status or outputs an error:

1. Show the error message clearly
2. Check if it mentions a missing API key — if so, say:
   > "It looks like an API key is missing. Open the `.env` file in your DIALECTIC install directory and add:
   > - `OPENAI_API_KEY` — from platform.openai.com
   > - `PPLX_API_KEY` — from perplexity.ai (or `BRAVE_SEARCH_API_KEY` from brave.com/search/api)"
3. Otherwise, show the raw error and suggest re-running.
