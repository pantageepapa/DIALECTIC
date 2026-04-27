## Context

`SKILL.md` currently has two problems:
1. The bash path detection uses `find "$HOME/.claude" -name "cli.py"` — fragile if the repo is renamed or nested differently
2. The intake flow asks users to type everything manually — wastes time and produces shallow team data

The `Person` dataclass (`education`, `experience`, `about`, `city`, `connections`) is already designed for rich LinkedIn data. The pipeline's team evaluation dimension is largely unused because there's no UX path to populate it. Claude has both `WebFetch` and vision built in — no new tools needed.

## Goals / Non-Goals

**Goals:**
- Replace bash path search with Claude reading its own skill invocation context
- Website-first intake that auto-fills company fields, with user confirmation
- Multi-screenshot LinkedIn intake that extracts full `Person` schema per founder, with per-person confirmation cards
- Clean fallback to manual entry if scrape fails or user skips

**Non-Goals:**
- Automated LinkedIn scraping (against ToS — screenshots only)
- Changing any Python pipeline code
- Adding new dependencies

## Decisions

**Decision 1: Path detection via skill invocation context**

Claude Code injects `Base directory for this skill: <path>` into the skill's system context at invocation time. SKILL.md instructs Claude to read this value and use it as `DIALECTIC_DIR` directly in the bash command. This is zero-fragility — no filesystem search, no assumptions about directory name.

Alternative (find by SKILL.md): more portable but adds unnecessary complexity since the path is already available.

**Decision 2: WebFetch for website scraping, not a Python scraper**

The skill is Claude-native. WebFetch is available to Claude directly in SKILL.md without any Python. The output quality varies (JS SPAs return shells), but the fallback is immediate — Claude detects empty/useless content and drops back to manual questions. A Python scraper would add a dependency and a CLI flag for no gain over WebFetch.

**Decision 3: One screenshot per founder, loop until done**

Rather than asking the user to upload all screenshots at once, Claude asks after each extraction: "Another founder? Upload the next screenshot or type 'done'." This is cleaner UX — users know when each person was captured correctly before moving on.

**Decision 4: Extraction maps to Person schema fields exactly**

Claude extracts from each screenshot into explicit fields matching `Person`:
- `name`, `city`, `country_code`
- `about` (the bio/summary section)
- `education`: list of `{institution, start_year, end_year}`
- `experience`: list of `{company, title, description, start_date, end_date}`
- `followers`, `connections` (if visible)

Claude then formats these using `Person.get_profile_summary()` text format and passes them in `--extra`. This ensures the pipeline receives team data in the exact format its prompts already expect.

**Decision 5: Per-person confirmation card, editable**

After extracting each person, Claude shows a structured card:
```
Founder: Alice Chen
Location: San Francisco, US
Education: Stanford University (2015–2019)
Experience: PM at Google (2019–2023); Co-founder at Acme (2023–present)
About: "Builder focused on..."
```
User says "correct" or points out errors. Claude corrects before moving to the next screenshot. Final team summary shown before running the pipeline.

## Risks / Trade-offs

- **JS-heavy sites return empty content** → Mitigation: Claude checks if scraped content is meaningful (has company description > 50 chars); if not, drops to manual immediately
- **LinkedIn screenshots vary in layout** → Mitigation: Claude is instructed to extract what's visible and mark fields as "not visible" rather than guessing; user confirmation catches errors
- **Multi-screenshot flow can feel long** → Mitigation: optional — user can skip at any point; typical teams are 2–3 founders so 2–3 confirmation rounds

## Open Questions

- Should the skill ask for the website first unconditionally, or only offer it as "optional"? (Recommend: ask first, frame as the fast path)
- If the user uploads a screenshot that's not LinkedIn (e.g., Twitter/X, personal site), should Claude attempt extraction anyway? (Recommend: yes, extract what's available)
