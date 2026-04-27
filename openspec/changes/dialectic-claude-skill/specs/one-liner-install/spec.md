## ADDED Requirements

### Requirement: SKILL.md exists at repo root
A `SKILL.md` file SHALL exist at the repository root so that when the repo is cloned to `~/.claude/skills/dialectic/`, Claude Code registers `/dialectic` as a global skill.

#### Scenario: Global install via clone
- **WHEN** user clones to `~/.claude/skills/dialectic/`
- **THEN** Claude Code loads `SKILL.md` and `/dialectic` is available in all projects

#### Scenario: Project-level use
- **WHEN** user opens the repo directly in Claude Code (not as a global skill)
- **THEN** `/dialectic` is still available via the project-level `SKILL.md`

### Requirement: setup script installs dependencies and creates .env
An executable `setup` shell script SHALL exist at the repo root and handle all first-time setup.

#### Scenario: uv not installed
- **WHEN** `uv` is not found on PATH
- **THEN** setup installs uv via its official curl installer and continues

#### Scenario: uv installed
- **WHEN** `uv` is found on PATH
- **THEN** setup runs `uv sync` to install Python dependencies

#### Scenario: .env does not exist
- **WHEN** `.env` file is not present
- **THEN** setup copies `.env.example` to `.env` and prints instructions to fill in API keys

#### Scenario: .env already exists
- **WHEN** `.env` file already exists
- **THEN** setup skips the copy step (does not overwrite existing config)

#### Scenario: Setup completes
- **WHEN** all steps succeed
- **THEN** setup prints: success message, path to `.env`, list of required keys (OPENAI_API_KEY, PPLX_API_KEY or BRAVE_API_KEY), and instruction to open Claude Code and type `/dialectic`

### Requirement: Install prompt is copy-pasteable into Claude Code
The README SHALL include a single-block install prompt that users paste into Claude Code to install the skill globally.

#### Scenario: User pastes install prompt
- **WHEN** user pastes the install block into Claude Code
- **THEN** Claude runs the git clone, runs setup, and tells the user to fill in API keys
