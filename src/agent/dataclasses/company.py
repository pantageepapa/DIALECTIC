from typing import List, Optional

from pydantic import BaseModel

from agent.dataclasses.person import Person


class Company(BaseModel):
    name: str
    industry: Optional[str] = None
    tagline: Optional[str] = None
    about: Optional[str] = None
    team: Optional[List["Person"]] = None
    
    def _get_team_summary(self) -> str:
        """Format team data focusing on team members with their details.

        Returns:
            str: Formatted team summary with member information.
        """
        if not self.team:
            return "No team information available"
        summary = "Founders:\n"
        for person in self.team:
            person_summary = person.get_profile_summary()
            summary += f"{person_summary}\n"
        return summary

    def get_company_summary(self) -> str:
        """Generate a comprehensive company summary for LLM processing.

        Returns:
            str: Complete company summary including all key information.
        """
        parts = []

        # Basic company information
        parts.append(f"Company: {self.name}")

        if self.tagline:
            parts.append(f"Tagline: {self.tagline}")

        if self.about:
            parts.append(f"About: {self.about}")

        if self.team:
            parts.append(f"\n{self._get_team_summary()}")

        return "\n".join(parts)
