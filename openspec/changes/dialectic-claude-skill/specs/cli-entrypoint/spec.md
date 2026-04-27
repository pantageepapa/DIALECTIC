## ADDED Requirements

### Requirement: CLI accepts company data as arguments
`src/agent/cli.py` SHALL accept company information via named CLI arguments and be runnable as `uv run python -m agent.cli`.

#### Scenario: Full argument set
- **WHEN** invoked with `--name "Acme" --about "AI for supply chain" --industry "Logistics" --website "acme.ai" --extra "Founded 2022"`
- **THEN** CLI builds a `Company` object and runs the pipeline

#### Scenario: Minimal argument set
- **WHEN** invoked with only `--name` and `--about`
- **THEN** CLI runs with those fields; industry/website/extra default to None

### Requirement: CLI validates API keys at startup
The CLI SHALL check that required environment variables are set before invoking the graph.

#### Scenario: Missing OPENAI_API_KEY
- **WHEN** `OPENAI_API_KEY` is not set in environment
- **THEN** CLI exits with code 1 and prints: `Error: OPENAI_API_KEY not set. Add it to ~/.claude/skills/dialectic/.env`

#### Scenario: Missing search API key
- **WHEN** neither `PPLX_API_KEY` nor `BRAVE_API_KEY` is set
- **THEN** CLI exits with code 1 and prints: `Error: No search API key set. Add PPLX_API_KEY or BRAVE_API_KEY to ~/.claude/skills/dialectic/.env`

### Requirement: CLI outputs structured JSON to stdout
The CLI SHALL write JSON to stdout upon successful pipeline completion.

#### Scenario: Successful run
- **WHEN** pipeline completes without error
- **THEN** CLI prints a single JSON object to stdout with keys: `company`, `final_decision`, `final_arguments` (array with type/content/refined_content/score), `arguments_history`, `iterations_completed`

#### Scenario: Pipeline error
- **WHEN** the graph raises an exception
- **THEN** CLI exits with code 1 and prints the error message to stderr (not stdout)

### Requirement: CLI uses max_iterations=2
The CLI SHALL run the pipeline with `max_iterations=2` as established by the research paper.

#### Scenario: Config defaults
- **WHEN** CLI is invoked without config flags
- **THEN** pipeline runs with `max_iterations=2`, `n_pro_arguments=3`, `n_contra_arguments=3`
