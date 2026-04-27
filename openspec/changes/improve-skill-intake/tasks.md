## 1. Fix Path Detection

- [x] 1.1 Replace the bash `find` path search in SKILL.md with an instruction for Claude to read the base directory from its skill invocation context (`Base directory for this skill: ...`)
- [x] 1.2 Update the bash execution block to use `cd [SKILL_BASE_DIR]` directly instead of the dynamic find command

## 2. Website Scrape Intake

- [x] 2.1 Replace Step 1 (manual company questions) with a website URL prompt: "What's the startup's website? (or type 'skip' to enter manually)"
- [x] 2.2 Add instructions for Claude to use WebFetch on the provided URL and extract: name, tagline, about, industry
- [x] 2.3 Add content quality check: if scraped content is empty or lacks substantive company description, fall back to manual questions
- [x] 2.4 Add confirmation card display after successful scrape showing all extracted fields, followed by explicit prompt: "Does this look right? Edit anything below or type 'yes' to confirm" with a free-text field showing the current values
- [x] 2.5 Add correction flow: user can type corrections inline (e.g. "industry is HealthTech"), Claude updates and re-displays full card, loops until user confirms
- [x] 2.6 Preserve manual fallback questions (name, what it does, industry) for skip/fail path

## 3. LinkedIn Screenshot Intake

- [x] 3.1 Add new Step 2 after company confirmation: offer team info via "1. Upload LinkedIn screenshot(s) 2. Type manually 3. Skip"
- [x] 3.2 Write screenshot extraction instructions: Claude reads each image and extracts name, city, country_code, about, education list, experience list, followers, connections
- [x] 3.3 Write per-person confirmation card format (name, location, education, experience, about)
- [x] 3.4 Add correction flow per person: user corrects fields, Claude updates and re-displays card
- [x] 3.5 Add loop prompt after each confirmed person: "Another founder? Upload next screenshot or type 'done'"
- [x] 3.6 Add final team summary display after all founders confirmed, before proceeding to verbosity selection
- [x] 3.7 Write synthesis instructions: format each confirmed Person using get_profile_summary() text structure, join multiple persons with "---" separator, pass as --extra arg

## 4. Manual Team Entry Fallback

- [x] 4.1 Add instructions for manual team entry path (option 2): Claude asks "Name and background for each founder, one at a time" and formats responses as Person summary text
