## ADDED Requirements

### Requirement: Skill collects company information conversationally
The skill SHALL ask the user for company information in a natural conversational flow before running the analysis.

#### Scenario: Full intake flow
- **WHEN** user invokes `/dialectic`
- **THEN** Claude asks for: (1) startup name, (2) what it does, (3) industry, (4) website or additional context
- **THEN** Claude confirms the collected info and asks the user to confirm before proceeding

#### Scenario: User provides info upfront in the command
- **WHEN** user invokes `/dialectic Acme AI — AI for supply chain`
- **THEN** Claude uses the provided info and only asks for missing fields

### Requirement: Skill asks for output verbosity preference
The skill SHALL ask the user whether they want a summary or detailed output before running the pipeline.

#### Scenario: User chooses summary (default)
- **WHEN** user selects "summary" or accepts the default recommendation
- **THEN** after the pipeline completes, Claude presents top 3 pro arguments, top 3 contra arguments, and a one-paragraph investment recommendation

#### Scenario: User chooses detailed
- **WHEN** user selects "detailed"
- **THEN** after the pipeline completes, Claude presents all arguments with their original content, critique, refined content, and scores, plus the investment recommendation

### Requirement: Skill warns about runtime duration
The skill SHALL inform the user that the analysis takes several minutes before starting.

#### Scenario: Pre-run warning
- **WHEN** Claude has collected all company info and verbosity preference
- **THEN** Claude says "This analysis takes 2-5 minutes. Starting now..." before executing the CLI

### Requirement: Skill presents structured output after pipeline completes
The skill SHALL parse the CLI's JSON output and present it according to the user's verbosity choice.

#### Scenario: Summary output
- **WHEN** pipeline completes and user chose summary
- **THEN** Claude displays: company name header, top 3 pro arguments with scores, top 3 contra arguments with scores, final decision (invest/not invest), and a synthesized recommendation paragraph

#### Scenario: Detailed output
- **WHEN** pipeline completes and user chose detailed
- **THEN** Claude displays all of the above plus full iteration history with critiques and refinements

#### Scenario: Pipeline error
- **WHEN** CLI exits with non-zero status or outputs an error message
- **THEN** Claude reports the error clearly and suggests checking API keys in `~/.claude/skills/dialectic/.env`
