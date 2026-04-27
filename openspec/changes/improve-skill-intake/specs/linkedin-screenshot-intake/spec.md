## ADDED Requirements

### Requirement: Skill offers LinkedIn screenshot upload after company info is confirmed
After company info is confirmed, the skill SHALL offer the user the option to add founder/team information via LinkedIn profile screenshots.

#### Scenario: User chooses to add team info
- **WHEN** user selects the screenshot option
- **THEN** Claude asks the user to upload the first LinkedIn profile screenshot

#### Scenario: User skips team info
- **WHEN** user selects "skip" or types "skip"
- **THEN** Claude proceeds to verbosity selection and pipeline execution without team data

### Requirement: Claude extracts Person schema fields from each screenshot
For each uploaded screenshot, Claude SHALL extract the following fields using vision: name, city, country_code, about (bio/summary), education (list of institution + years), experience (list of company + title + dates + description), followers, connections.

#### Scenario: Full LinkedIn profile screenshot
- **WHEN** user uploads a LinkedIn profile screenshot with visible name, experience, and education sections
- **THEN** Claude extracts all visible fields into Person schema structure and marks any non-visible fields as absent

#### Scenario: Partial or non-LinkedIn screenshot
- **WHEN** user uploads a screenshot that is not a full LinkedIn profile (e.g., Twitter, personal site, partial view)
- **THEN** Claude extracts whatever fields are visible, marks missing fields as absent, and proceeds to confirmation

### Requirement: Claude shows a confirmation card for each extracted person
After extracting each person, Claude SHALL display a structured confirmation card showing all extracted fields and ask the user to confirm or correct before moving to the next screenshot.

#### Scenario: User confirms person
- **WHEN** user confirms the extracted person info is correct
- **THEN** Claude adds the person to the team list and asks if there is another founder to add

#### Scenario: User corrects person info
- **WHEN** user corrects one or more fields (e.g., "her degree is from MIT not Stanford")
- **THEN** Claude updates the corrected fields, re-displays the updated card, and asks for confirmation again

### Requirement: Skill loops until user indicates no more founders
After confirming each person, Claude SHALL ask whether there is another founder to add, continuing the loop until the user says done.

#### Scenario: User uploads another screenshot
- **WHEN** user uploads another LinkedIn screenshot after confirming the previous person
- **THEN** Claude extracts and confirms the new person, then asks again if there are more

#### Scenario: User says done
- **WHEN** user types "done" or "no more"
- **THEN** Claude shows a final team summary listing all confirmed founders and proceeds to verbosity selection

### Requirement: Confirmed team data is synthesized into pipeline input
All confirmed Person records SHALL be formatted using the Person.get_profile_summary() text structure and passed to the pipeline via the --extra CLI argument.

#### Scenario: Single founder
- **WHEN** one person is confirmed
- **THEN** --extra contains the formatted profile summary for that person

#### Scenario: Multiple founders
- **WHEN** two or more persons are confirmed
- **THEN** --extra contains all formatted profile summaries concatenated with "---" separator between each person
