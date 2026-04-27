## MODIFIED Requirements

### Requirement: Skill uses skill invocation base directory for pipeline execution
The skill SHALL use the base directory provided in the Claude Code skill invocation context (the `Base directory for this skill:` line) as the working directory when executing the pipeline CLI, instead of searching the filesystem for cli.py.

#### Scenario: Skill invoked from global install
- **WHEN** skill is loaded from `~/.claude/skills/dialectic/`
- **THEN** Claude reads the base directory from its invocation context and uses it directly in `cd <base_dir> && uv run python -m agent.cli ...`

#### Scenario: Skill invoked from project directory
- **WHEN** skill is loaded from the repo opened as a project in Claude Code
- **THEN** Claude reads the base directory from its invocation context (the repo root) and uses it directly

### Requirement: Intake flow starts with website URL before manual questions
The skill SHALL ask for the startup's website URL as the first intake step, using scraped content to auto-fill company fields, falling back to manual questions if scraping fails or is skipped.

#### Scenario: Website provided and scrape succeeds
- **WHEN** user provides a URL and scrape returns meaningful content
- **THEN** Claude presents pre-filled confirmation card instead of asking manual questions

#### Scenario: Website skipped or scrape fails
- **WHEN** user skips or scrape returns empty content
- **THEN** Claude asks for name, what it does, and industry manually as before

### Requirement: Team info step follows company info confirmation
After company info is confirmed, the skill SHALL offer the LinkedIn screenshot upload flow before proceeding to verbosity selection.

#### Scenario: User adds team info via screenshots
- **WHEN** user uploads one or more LinkedIn screenshots
- **THEN** Claude extracts, confirms, and synthesizes team data into pipeline input before running

#### Scenario: User skips team info
- **WHEN** user skips the team step
- **THEN** pipeline runs without team data, same as before this change
