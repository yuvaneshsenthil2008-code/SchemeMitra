"""
SchemeMitra — Centralized Requirement Presentation Mapping Module
Provides deterministic mapping for presentation wording (display_title, supporting_text, canonical_title)
without mutating canonical M1/M2 data ground truth.
"""

from typing import Dict, Any

def format_requirement_presentation(req: Dict[str, Any]) -> Dict[str, str]:
    """
    Formats a requirement's user-facing presentation fields.
    
    Returns:
        dict with keys:
            - canonical_title: Original M1 requirement action/label
            - display_title: User-facing action text
            - supporting_text: Additional context/guidance for user
    """
    req_type = (req.get("requirement_type") or "").strip().upper()
    raw_action_label = (
        req.get("action_label") or 
        req.get("canonical_title") or 
        req.get("title") or 
        req.get("requirement_id") or 
        req.get("requirement_node_id") or 
        ""
    ).strip()

    # Exact matching rule: requirement_type == "ENTITY_REGISTRATION" or exact normalized legacy action label
    if req_type == "ENTITY_REGISTRATION" or raw_action_label.lower() == "register the entity/organisation":
        display_title = "Register your business/entity if required by this scheme"
        supporting_text = "Exact registration type needs confirmation."
    else:
        display_title = raw_action_label
        supporting_text = req.get("supporting_text") or ""

    return {
        "canonical_title": raw_action_label,
        "display_title": display_title,
        "supporting_text": supporting_text
    }
