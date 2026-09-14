from __future__ import annotations
from ..models.opportunity import Opportunity


def build_why_match(opportunity: Opportunity, match: dict) -> dict:
    """Explain ranking using only M2 pass evidence + M1 support metadata."""
    reasons = []
    for detail in opportunity.passed:
        reasons.append({
            "type": "ELIGIBILITY_RULE_MATCH",
            "field": detail.get("field"),
            "text": detail.get("reason", "A deterministic eligibility condition matched."),
            "actual": detail.get("actual"),
            "expected": detail.get("expected"),
        })
    if match.get("preferred_support_matches"):
        reasons.append({"type": "PREFERRED_SUPPORT", "text": "Offers support types you explicitly preferred.", "support_types": match["preferred_support_matches"]})
    if match.get("inferred_need_matches"):
        reasons.append({"type": "INFERRED_NEED", "text": "Offers support related to needs inferred from your profile conversation.", "support_types": match["inferred_need_matches"]})
    if match.get("sector_match"):
        reasons.append({"type": "SECTOR", "text": "The opportunity sector aligns with the sector in your profile."})
    return {
        "reasons": reasons,
        "missing_profile_fields": opportunity.missing_profile_fields,
        "uncertain_rules": opportunity.uncertain_rules,
        "note": "These reasons explain known deterministic/profile matches. They do not override official scheme rules or M2 eligibility status.",
    }
