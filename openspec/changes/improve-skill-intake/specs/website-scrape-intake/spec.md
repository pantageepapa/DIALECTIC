## ADDED Requirements

### Requirement: Skill asks for website URL as first intake step
The skill SHALL ask the user for the startup's website URL as the first question, framing it as the fast path to auto-fill company information.

#### Scenario: User provides URL
- **WHEN** user provides a URL
- **THEN** Claude fetches the page using WebFetch and attempts to extract company information

#### Scenario: User skips URL
- **WHEN** user says "skip" or provides no URL
- **THEN** Claude proceeds directly to manual question flow (name, what it does, industry)

### Requirement: Claude extracts company fields from scraped content
After fetching the website, Claude SHALL extract the following fields if present: company name, tagline, what it does (about), and industry/sector.

#### Scenario: Successful extraction
- **WHEN** scraped content contains meaningful company description (more than 50 characters of substantive text)
- **THEN** Claude populates name, about, industry from the content and presents a confirmation card

#### Scenario: Empty or JS-shell content
- **WHEN** scraped content is empty, contains only navigation/footer text, or lacks a company description
- **THEN** Claude informs the user the site couldn't be read and falls back to manual questions

### Requirement: Claude confirms extracted company info with the user
After extraction, Claude SHALL display a structured confirmation card and allow the user to correct any field before proceeding.

#### Scenario: User confirms all fields
- **WHEN** user confirms the extracted info is correct
- **THEN** Claude uses the confirmed values and proceeds to team info step

#### Scenario: User corrects a field
- **WHEN** user corrects one or more fields (e.g., "the industry is HealthTech not B2B SaaS")
- **THEN** Claude updates the corrected fields and re-displays the card for final confirmation
