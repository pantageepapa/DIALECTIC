"""Person Dataclass for LinkedIn Profile Data

Transforms raw Brightdata LinkedIn profile responses into clean, structured data
optimized for LLM processing and analysis. Focuses on semantic content while
removing technical identifiers and URLs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from agent.dataclasses.company import Company


class Education(BaseModel):
    """Represents educational background."""

    institution: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None

    def __str__(self) -> str:
        if not self.institution:
            return ""

        parts = [self.institution]
        if self.start_year and self.end_year:
            parts.append(f"({self.start_year}-{self.end_year})")
        elif self.end_year:
            parts.append(f"(graduated {self.end_year})")
        elif self.start_year:
            parts.append(f"({self.start_year}-present)")

        return " ".join(parts)


class Experience(BaseModel):
    """Represents work experience with timeline and description."""

    company: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None

    def __str__(self) -> str:
        parts = []

        if self.title:
            parts.append(self.title)
        if self.company:
            parts.append(f"at {self.company}")

        if self.start_date and self.end_date:
            parts.append(f"({self.start_date} - {self.end_date})")
        elif self.start_date:
            parts.append(f"({self.start_date} - present)")

        if self.location:
            parts.append(f"[{self.location}]")

        result = " ".join(parts)

        if self.description and result:
            result += f" - {self.description}"

        return result


def safe_int(value: Any) -> Optional[int]:
    """Safely convert value to int, return None if not possible."""
    if value is None:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_str(value: Any) -> Optional[str]:
    """Safely convert value to string, return None if empty."""
    if value is None:
        return None

    str_val = str(value).strip()
    return str_val if str_val else None


class Person(BaseModel):
    """Represents a LinkedIn profile with clean, LLM-optimized data.

    Focuses on your core fields: name, followers, education, current_company,
    city, country_code, experience, plus additional semantic content.
    """

    # Core fields of interest
    name: Optional[str] = None
    followers: Optional[int] = None
    education: Optional[List[Education]] = None
    current_company: Optional["Company"] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    experience: Optional[List[Experience]] = None
    educations_details: Optional[str] = None

    # Additional semantic content for LLM analysis
    about: Optional[str] = None
    connections: Optional[int] = None

    def __post_init__(self):
        """Initialize empty lists if None."""
        if self.education is None:
            self.education = []
        if self.experience is None:
            self.experience = []

    def get_profile_summary(self) -> str:
        """Generate a comprehensive text summary for LLM prompts."""
        parts = []

        # Basic info
        if self.name:
            parts.append(f"Name: {self.name}")

        if self.city and self.country_code:
            parts.append(f"Location: {self.city}, {self.country_code}")
        elif self.city:
            parts.append(f"Location: {self.city}")
        elif self.country_code:
            parts.append(f"Country: {self.country_code}")

        # Network size
        network_info = []
        if self.followers:
            network_info.append(f"{self.followers} followers")
        if self.connections:
            network_info.append(f"{self.connections} connections")
        if network_info:
            parts.append(f"Network: {', '.join(network_info)}")

        # Current role
        if self.current_company:
            parts.append(f"Current Company: {self.current_company}")

        # About section
        if self.about:
            parts.append(f"About: {self.about}")

        # Education
        if self.education:
            edu_summary = self.get_education_summary()
            if edu_summary:
                parts.append(f"Education: {edu_summary}")

        if self.educations_details:
            parts.append(f"Educations Details: {self.educations_details}")

        # Work experience
        if self.experience:
            work_summary = self.get_work_timeline()
            if work_summary:
                parts.append(f"Work Experience: {work_summary}")

        return "\n".join(parts)

    def get_work_timeline(self) -> str:
        """Get chronological work experience summary."""
        if not self.experience:
            return ""

        exp_strings = [str(exp) for exp in self.experience if str(exp).strip()]
        return "; ".join(exp_strings) if exp_strings else ""

    def get_education_summary(self) -> str:
        """Get education background summary."""
        if not self.education:
            return ""

        edu_strings = [str(edu) for edu in self.education if edu and str(edu).strip()]
        return "; ".join(edu_strings) if edu_strings else ""

    def get_current_role(self) -> str:
        """Get current position context."""
        if self.current_company:
            return f"Currently at {self.current_company}"
        return ""

    def to_analysis_context(self) -> str:
        """Get structured text optimized for LLM analysis."""
        return self.get_profile_summary()

    def is_complete(self) -> bool:
        """Check if profile has core information for analysis."""
        return bool(
            self.name
            and (self.current_company or self.experience)
            and (self.education or self.about)
        )
