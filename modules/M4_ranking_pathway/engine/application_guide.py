from __future__ import annotations
from ..models.opportunity import Opportunity


def build_application_guide(opportunity: Opportunity) -> dict:
    """Separate from Opportunity Pathway: only M1 application/document information."""
    return {
        "opportunity_id": opportunity.opportunity_id,
        "application_route": opportunity.application_route or None,
        "documents_summary": opportunity.required_documents_summary or None,
        "official_source_url": opportunity.official_source_url,
        "note": "Application Guide is not the Opportunity Pathway. Verify the latest steps and documents on the official source before applying.",
    }
