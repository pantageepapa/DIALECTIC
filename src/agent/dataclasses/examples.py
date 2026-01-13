"""Example company data for testing and demonstration."""

from agent.dataclasses.company import Company
from agent.dataclasses.person import Person

# Brandback: Early-stage SaaS company
BRANDBACK_COMPANY = Company(
    name="Brandback",
    industry="Software as a Service (SaaS) - Marketing Technology",
    tagline="AI-powered brand protection and reputation management for enterprises",
    about="Brandback provides enterprise brands with AI-powered monitoring and management of their online reputation across channels. The platform helps detect brand safety issues, manage crises, and protect brand equity in real-time.",
    team=[
        Person(
            name="John Founder",
            title="CEO & Co-founder",
            location_description="San Francisco, CA",
            industry_experience=["SaaS", "Marketing Tech"],
            background_summary="Previously led product at major marketing platform",
        )
    ],
    pitchdeck_summary="Series A SaaS company focused on AI-powered brand protection for enterprises",
    website_content="Brandback enables enterprises to monitor, manage, and protect their brand across digital channels",
)
