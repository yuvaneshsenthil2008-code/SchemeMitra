from __future__ import annotations
import json
from pathlib import Path
from .adapters import combine_m1_m2
from .ranking_engine import RankingEngine
from .why_match import build_why_match
from .application_guide import build_application_guide
from .pathway_bridge import attach_verified_pathway


class RecommendationEngine:
    """M4 contract: rank recommendable M2 outputs, isolate verification, never recommend NOT_ELIGIBLE."""
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")
        self.opportunity_master = json.loads((self.data_dir / "opportunity_master.json").read_text(encoding="utf-8"))
        self.ranker = RankingEngine()

    def build(self, profile: dict, eligibility_results: list[dict], pathway_results: dict | None = None) -> dict:
        opportunities = combine_m1_m2(self.opportunity_master, eligibility_results)
        ranked = self.ranker.rank(opportunities, profile)

        recommendations = []
        for item in ranked:
            o = item["opportunity"]
            recommendations.append({
                "opportunity_id": o.opportunity_id,
                "opportunity_name": o.opportunity_name,
                "rank": item["rank"],
                "score": item["score"],
                "eligibility_status": o.eligibility_status,
                "rule_completeness": o.rule_completeness,
                "primary_sector": o.primary_sector,
                "secondary_sectors": o.secondary_sectors,
                "support_types": o.support_types,
                "benefit_summary": o.benefit_summary,
                "target_beneficiary": o.target_beneficiary,
                "scope": o.scope,
                "match": item["match"],
                "why_match": build_why_match(o, item["match"]),
                "opportunity_pathway": attach_verified_pathway(o.opportunity_id, pathway_results),
                "application_guide": build_application_guide(o),
                "official_source_url": o.official_source_url,
                "last_verified": o.last_verified,
                "missing_profile_fields": o.missing_profile_fields,
            })

        needs_verification = []
        not_eligible = []
        for o in opportunities:
            if o.eligibility_status == "NEEDS_VERIFICATION" or not o.source_recommendable or not o.m2_recommendable or o.lifecycle_status != "ACTIVE":
                needs_verification.append({
                    "opportunity_id": o.opportunity_id,
                    "opportunity_name": o.opportunity_name,
                    "eligibility_status": o.eligibility_status,
                    "lifecycle_status": o.lifecycle_status,
                    "lifecycle_warning": o.lifecycle_warning,
                    "official_source_url": o.official_source_url,
                    "last_verified": o.last_verified,
                })
            elif o.eligibility_status == "NOT_ELIGIBLE":
                not_eligible.append({
                    "opportunity_id": o.opportunity_id,
                    "opportunity_name": o.opportunity_name,
                    "failed_rules": o.failed,
                })

        # Status buckets for frontend tabs. NOT_ELIGIBLE is deliberately outside recommendations.
        eligible = [x for x in recommendations if x["eligibility_status"] == "ELIGIBLE"]
        potentially = [x for x in recommendations if x["eligibility_status"] == "POTENTIALLY_ELIGIBLE"]
        return {
            "recommendations": recommendations,
            "eligible": eligible,
            "potentially_eligible": potentially,
            "needs_verification": sorted(needs_verification, key=lambda x: x["opportunity_name"].lower()),
            "not_eligible": sorted(not_eligible, key=lambda x: x["opportunity_name"].lower()),
            "summary": {
                "recommendations": len(recommendations),
                "eligible": len(eligible),
                "potentially_eligible": len(potentially),
                "needs_verification": len(needs_verification),
                "not_eligible": len(not_eligible),
            },
            "safety_note": "M4 ranks only M2-recommendable ACTIVE opportunities. It never converts NOT_ELIGIBLE or NEEDS_VERIFICATION into recommendations.",
        }
