from __future__ import annotations
from typing import Any
from ..models.opportunity import Opportunity

STATUS_BASE = {"ELIGIBLE": 60, "POTENTIALLY_ELIGIBLE": 45}
BROAD_FINANCE = {"CREDIT", "LOAN", "SUBSIDY", "GRANT", "CREDIT_GUARANTEE"}
SUPPORT_SYNONYMS = {
    "FINANCE": BROAD_FINANCE,
    "FUNDING": BROAD_FINANCE,
    "MARKET": {"MARKET_ACCESS", "EXPORT_SUPPORT"},
    "MARKETING": {"MARKET_ACCESS", "EXPORT_SUPPORT"},
    "SKILLS": {"TRAINING", "SKILL_DEVELOPMENT", "CERTIFICATION"},
    "TRAINING": {"TRAINING", "SKILL_DEVELOPMENT"},
    "INCUBATION": {"INCUBATION", "MENTORSHIP"},
}


def _norm_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        values = [values]
    return {str(v).strip().upper() for v in values if str(v).strip()}


def _expand(values: set[str]) -> set[str]:
    out = set(values)
    for v in values:
        out |= SUPPORT_SYNONYMS.get(v, set())
    return out



def _canonical_category(value: Any) -> str:
    v = str(value or "").strip().lower()
    return {
        "sc":"SC", "scheduled caste":"SC",
        "st":"ST", "scheduled tribe":"ST",
        "obc":"OBC", "backward class":"OBC", "notified backward classes":"OBC",
        "minority":"Minority", "general":"General",
    }.get(v, str(value or "").strip())

def _demographic_match(opportunity: Opportunity, profile: dict) -> list[str]:
    if not opportunity.demographic_targeting and not opportunity.demographic_benefit_variants:
        return []
    reasons = []
    gender = str(profile.get("gender") or "").strip()
    category = _canonical_category(profile.get("category"))
    disability = str(profile.get("disability_status") or "").strip().upper()
    all_genders = {"Male", "Female", "Transgender"}
    all_categories = {"General", "OBC", "SC", "ST", "Minority"}
    eligible_g = set(opportunity.eligible_genders or [])
    eligible_c = {_canonical_category(x) for x in (opportunity.eligible_social_categories or [])}
    if eligible_g and eligible_g != all_genders and gender in eligible_g:
        reasons.append(f"Gender-targeted opportunity matches your profile ({gender}).")
    if eligible_c and eligible_c != all_categories and category in eligible_c:
        reasons.append(f"Social-category-targeted opportunity matches your profile ({category}).")
    if opportunity.disability_eligibility == "PERSON_WITH_DISABILITY" and disability == "PERSON_WITH_DISABILITY":
        reasons.append("Disability-targeted opportunity matches your confirmed profile.")

    def dimension_match(key: str, allowed: Any) -> bool:
        vals = {str(v).strip() for v in (allowed or []) if str(v).strip()}
        if not vals:
            return True
        if key == "social_categories":
            return category in {_canonical_category(v) for v in vals}
        if key == "genders":
            return gender in vals
        if key == "disability_status":
            return disability in {v.upper() for v in vals}
        return False

    for variant in opportunity.demographic_benefit_variants or []:
        all_rules = variant.get("match_all") or {}
        any_rules = variant.get("match_any") or {}
        all_ok = bool(all_rules) and all(dimension_match(k, v) for k, v in all_rules.items())
        any_ok = bool(any_rules) and any(dimension_match(k, v) for k, v in any_rules.items())
        if (all_rules and not all_ok) or (any_rules and not any_ok):
            continue
        if all_rules or any_rules:
            reasons.append("A verified demographic-specific benefit applies to your profile.")
            break
    return reasons

def _sector_match(profile_sector: Any, opportunity: Opportunity) -> bool:
    if not profile_sector:
        return False
    p = str(profile_sector).strip().lower()
    hay = [opportunity.primary_sector or ""] + opportunity.secondary_sectors
    return any(p == str(x).strip().lower() or p in str(x).strip().lower() or str(x).strip().lower() in p for x in hay if x)


class RankingEngine:
    """Ranks only M2-recommendable opportunities. It never changes eligibility truth."""

    def score(self, opportunity: Opportunity, profile: dict) -> tuple[int, dict]:
        if not opportunity.is_safe_to_recommend():
            return 0, {"excluded": "NOT_RECOMMENDABLE"}

        offered = _norm_set(opportunity.support_types)
        preferred_raw = _norm_set(profile.get("preferred_support_types"))
        needs_raw = _norm_set(profile.get("support_needs"))
        preferred = _expand(preferred_raw)
        needs = _expand(needs_raw)

        preferred_matches = offered & preferred
        need_matches = offered & needs
        score = STATUS_BASE.get(opportunity.eligibility_status, 40)
        score += min(24, 12 * len(preferred_matches))
        score += min(12, 6 * len(need_matches - preferred_matches))
        sector_match = _sector_match(profile.get("sector"), opportunity)
        # Sector relevance remains the primary fit signal; demographic targeting is a modest
        # tie-breaker so it never displaces a clearly sector-relevant opportunity by itself.
        if sector_match:
            score += 8
        demographic_matches = _demographic_match(opportunity, profile)
        if demographic_matches:
            score += min(4, 2 * len(demographic_matches))
        # Passed deterministic conditions are a mild tie-breaker, never a substitute for M2 status.
        score += min(4, len(opportunity.passed))
        score = max(0, min(int(score), 100))

        if preferred_matches:
            tier = "PREFERRED_SUPPORT_MATCH"
        elif need_matches:
            tier = "INFERRED_NEED_MATCH"
        else:
            tier = "OTHER_RELEVANT_OPPORTUNITY"

        return score, {
            "tier": tier,
            "preferred_support_matches": sorted(preferred_matches),
            "inferred_need_matches": sorted(need_matches - preferred_matches),
            "sector_match": sector_match,
            "demographic_matches": demographic_matches,
            "demographic_targeted": opportunity.demographic_targeting,
            "offered_support_types": sorted(offered),
            "eligibility_status": opportunity.eligibility_status,
        }

    def rank(self, opportunities: list[Opportunity], profile: dict) -> list[dict]:
        tier_order = {"PREFERRED_SUPPORT_MATCH": 0, "INFERRED_NEED_MATCH": 1, "OTHER_RELEVANT_OPPORTUNITY": 2}
        ranked = []
        for opp in opportunities:
            if not opp.is_safe_to_recommend():
                continue
            score, match = self.score(opp, profile)
            ranked.append({"opportunity": opp, "score": score, "match": match})
        ranked.sort(key=lambda x: (tier_order.get(x["match"]["tier"], 9), -x["score"], x["opportunity"].opportunity_name.lower()))
        for i, item in enumerate(ranked, 1):
            item["rank"] = i
        return ranked
