## Why

The `/dialectic` skill currently requires users to manually type all company information, which is tedious and misses rich team data the pipeline is designed to use. By scraping the startup's website and extracting founder profiles from LinkedIn screenshots, we can minimize user input while feeding the pipeline richer data — particularly the team dimension, which the `Person` dataclass is already built to handle.

## What Changes

- **Modified**: `SKILL.md` path detection — replace fragile `find` bash search with Claude reading the base directory from its own skill invocation context
- **Modified**: `SKILL.md` intake flow — new Step 1 asks for website URL, scrapes it via WebFetch, auto-fills company fields, confirms with user
- **Modified**: `SKILL.md` team intake — new Step 2 accepts multiple LinkedIn screenshots, extracts each to `Person` schema fields (name, education, experience, about, location), shows confirmation card per person, allows corrections before proceeding
- **Modified**: `SKILL.md` fallback — if scrape fails or user skips, falls back to original manual question flow

## Capabilities

### New Capabilities

- `website-scrape-intake`: Claude scrapes the startup's website URL using WebFetch, extracts company name/tagline/about/industry, presents a confirmation card, and allows user corrections before proceeding
- `linkedin-screenshot-intake`: Claude accepts one or more LinkedIn profile screenshots (one per founder), extracts each to `Person` schema fields via vision, shows a structured confirmation card per person, allows corrections, then synthesizes confirmed data into the pipeline's `--extra` argument

### Modified Capabilities

- `dialectic-skill`: intake flow is replaced — website-first with manual fallback, team screenshots added as optional second step before confirming and running

## Impact

- `SKILL.md` only — no Python code changes
- No new dependencies
- Backward compatible — manual entry still works as fallback
