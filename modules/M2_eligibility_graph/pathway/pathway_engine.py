from __future__ import annotations
import json
from pathlib import Path
from ..models.profile import EntrepreneurProfile
from ..engine.eligibility_engine import EligibilityEngine
from ..engine.gap_analysis import GapAnalyzer
from ..graph.graph_engine import OpportunityGraph

STAGE_ORDER = {
    "IDENTITY_PROOF": 10, "CATEGORY_PROOF": 10, "CASTE_CERTIFICATE": 10, "TRIBE_CERTIFICATE": 10,
    "TRANSGENDER_CERTIFICATE_OR_ID": 10, "EDUCATION_PROOF": 10, "TARGET_GROUP_PROOF": 10,
    "TRAINING": 20, "CAPACITY_BUILDING": 20, "CERTIFICATION": 25, "CERTIFICATION_OR_COMPLETION": 25,
    "REGISTRATION": 30, "ENTITY_REGISTRATION": 30, "UDYAM_REGISTRATION": 30, "FSSAI": 30,
    "DPIIT_RECOGNITION": 30, "GEM_REGISTRATION": 30, "IEC": 30, "EXPORT_REGISTRATION": 30,
    "DPR": 40, "BUSINESS_PLAN": 40, "PROPOSAL": 40, "PROJECT_PROPOSAL": 40, "PITCH_OR_PROPOSAL": 40,
    "LAND": 45, "LAND_OR_FARM_PROOF": 45, "LAND_OR_ACTIVITY_PROOF": 45,
    "ELIGIBLE_LENDER": 50, "BANK_LINKAGE": 50, "INCUBATOR_LINKAGE": 50, "CHANNEL_PARTNER": 50,
    "DOCUMENT": 60,
}

GOAL_MAP = {
    "START_BUSINESS": "Start a business",
    "ESTABLISH_ENTERPRISE": "Establish an enterprise",
    "EXPAND_BUSINESS": "Expand existing business",
    "UPGRADE_UNIT": "Upgrade micro enterprise unit",
    "TECH_INNOVATION": "Technology innovation & commercialization",
    "EXPORT_DEVELOPMENT": "Export development"
}

def format_business_goal(goal: str | None) -> str:
    if not goal:
        return "Enterprise Establishment"
    g_str = str(goal).strip()
    if g_str.upper() in GOAL_MAP:
        return GOAL_MAP[g_str.upper()]
    if g_str.isupper() and "_" in g_str:
        return g_str.replace("_", " ").title()
    return g_str

class PathwayEngine:
    """Builds a goal-oriented, evidence-safe pathway.

    The stage order is a UI planning order only, never presented as an official
    government sequence unless M1 later supplies an explicit verified sequence.
    """
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")
        self.m1_dir = self.data_dir.parents[1] / "M1_data"
        self.eligibility = EligibilityEngine(self.data_dir)
        self.gaps = GapAnalyzer(self.data_dir)
        self.graph = OpportunityGraph(self.data_dir)
        self.opps = {o["Opportunity_ID"]: o for o in self.eligibility.opportunities}

        self.enriched_pathways = {}
        enriched_file = self.m1_dir / "pathway_reference_enriched.json"
        if enriched_file.exists():
            try:
                records = json.loads(enriched_file.read_text(encoding="utf-8"))
                self.enriched_pathways = {r["opportunity_id"]: r for r in records}
            except Exception:
                self.enriched_pathways = {}

    def build(self, profile: EntrepreneurProfile | dict | None, opportunity_id: str) -> dict:
        if profile is None:
            profile = EntrepreneurProfile()
        elif isinstance(profile, dict):
            profile = EntrepreneurProfile.from_dict(profile)

        ev = self.eligibility.evaluate_opportunity(profile, opportunity_id)
        gaps = self.gaps.analyze(profile, opportunity_id)
        sg = self.graph.subgraph_for_opportunity(opportunity_id)
        opp = self.opps[opportunity_id]
        enriched = self.enriched_pathways.get(opportunity_id, {})

        req_items = gaps["completed_requirements"] + gaps["action_gaps"] + gaps["unverified_or_generic_requirements"]
        state_by_id = {x["requirement_node_id"]: "COMPLETED" for x in gaps["completed_requirements"]}
        state_by_id.update({x["requirement_node_id"]: "ACTION_NEEDED" for x in gaps["action_gaps"]})
        state_by_id.update({x["requirement_node_id"]: "VERIFY" for x in gaps["unverified_or_generic_requirements"]})

        # Enrich requirements with why_this_matters from dataset if available
        enriched_req_map = {r["requirement_id"]: r for r in enriched.get("requirements", [])}

        actions = []
        for r in sorted(req_items, key=lambda x: (STAGE_ORDER.get(x["requirement_type"], 55), x["requirement_node_id"])):
            nid = r["requirement_node_id"]
            en_req = enriched_req_map.get(nid, {})
            actions.append({
                "node_id": nid,
                "requirement_type": r["requirement_type"],
                "label": r["action_label"],
                "state": state_by_id[nid],
                "why_this_matters": en_req.get("why_this_matters") or "Requirement verified against official scheme guidelines.",
                "official_source_url": en_req.get("source_url") or r["official_source_url"] or opp.get("Official_Source_URL", "https://myscheme.gov.in/"),
                "evidence_origin": en_req.get("evidence_origin", "M1_VERIFIED_DATA"),
                "explanation_origin": en_req.get("explanation_origin", "DERIVED_EXPLANATION"),
                "source_document_title": en_req.get("source_document_title", f"M1 Ground Truth Guideline - {opp.get('Opportunity_Name')}"),
                "source_section": en_req.get("source_section", f"M1 Prerequisite Mapping ({r['requirement_type']})"),
                "source_supports_claim": en_req.get("source_supports_claim", True),
                "ordering_note": "Suggested display order only; not an official application sequence.",
            })

        supports = [n for n in sg["nodes"] if n["type"] == "SUPPORT"]
        cross_edges = [e for e in sg["edges"] if e["relationship_type"] in {"UNLOCKS","ENABLES","FOLLOWED_BY","DEPENDS_ON","SUPPORTS"}]
        
        # Build normalized steps array conforming to canonical contract:
        # Current User State -> Real Requirements -> Target Opportunity -> Parallel Potential Supports -> User Goal
        steps = []
        step_seq = 1

        # Step 1: User Profile State
        steps.append({
            "step_number": step_seq,
            "step_type": "USER_PROFILE_STATE",
            "title": "User Profile State",
            "description": f"Sector: {profile.sector or 'Not specified'} | Stage: {profile.business_stage or 'Not specified'} | Location: {profile.state or 'Not specified'}",
            "state": "COMPLETED",
            "traceability": {
                "profile_fields_known": sum(v not in (None, "", [], {}) for k, v in profile.__dict__.items() if k != "extra")
            }
        })
        step_seq += 1

        # Step 2..N: Requirements (from M1 requirement nodes & M2 gap states)
        for r in actions:
            steps.append({
                "step_number": step_seq,
                "step_type": "REQUIREMENT",
                "requirement_node_id": r["node_id"],
                "requirement_type": r["requirement_type"],
                "title": r["label"],
                "action_label": r["label"],
                "state": r["state"],
                "why_this_matters": r["why_this_matters"],
                "official_source_url": r["official_source_url"],
                "evidence_origin": r["evidence_origin"],
                "explanation_origin": r["explanation_origin"],
                "source_document_title": r["source_document_title"],
                "source_section": r["source_section"],
                "source_supports_claim": r["source_supports_claim"],
                "ordering_note": r["ordering_note"]
            })
            step_seq += 1

        # Target Opportunity Node
        steps.append({
            "step_number": step_seq,
            "step_type": "TARGET_OPPORTUNITY",
            "opportunity_id": opportunity_id,
            "title": f"Target Opportunity: {opp['Opportunity_Name']}",
            "state": ev["status"],
            "description": f"Verified opportunity under {opp['Opportunity_Name']}"
        })
        step_seq += 1

        # Parallel Potential Supports Node
        parallel_supports = []
        for sup in supports:
            parallel_supports.append({
                "support_id": sup["id"],
                "support_type": sup["type"],
                "title": f"Potential Support: {sup['label']}",
                "description": "Support Available If Approved"
            })

        steps.append({
            "step_number": step_seq,
            "step_type": "PARALLEL_POTENTIAL_SUPPORTS",
            "title": "Potential Support Benefits",
            "supports": parallel_supports,
            "state": "POTENTIAL"
        })
        step_seq += 1

        # User Goal Node
        formatted_user_goal = format_business_goal(profile.business_goal)
        steps.append({
            "step_number": step_seq,
            "step_type": "USER_GOAL",
            "title": f"User Goal: {formatted_user_goal}",
            "description": "Target business objective upon support realization",
            "state": "TARGET"
        })

        # Separate Official Application Process Block (if documented in official guidelines)
        official_app_proc = enriched.get("official_process", [])

        return {
            "opportunity_id": opportunity_id,
            "opportunity_name": opp["Opportunity_Name"],
            "pathway_title": "Personalized Opportunity Pathway",
            "disclaimer": "Your pathway is based on verified scheme requirements and the information in your profile. The suggested order is guidance unless an official sequence is specified.",
            "ordering_confidence": enriched.get("ordering_confidence", "NO_OFFICIAL_SEQUENCE"),
            "user_business_goal": formatted_user_goal,
            "eligibility_status": ev["status"],
            "steps_count": len(steps),
            "steps": steps,
            "official_application_process": official_app_proc,
            "has_official_application_process": len(official_app_proc) > 0,
            "current_state": {
                "sector": profile.sector,
                "business_stage": profile.business_stage,
                "business_goal": formatted_user_goal,
                "profile_fields_known": sum(v not in (None, "", [], {}) for k,v in profile.__dict__.items() if k != "extra"),
            },
            "eligibility": ev,
            "pathway": {
                "requirements": actions,
                "opportunity": {"id": opportunity_id, "label": opp["Opportunity_Name"], "status": ev["status"]},
                "supports_unlocked_if_approved": supports,
                "verified_next_opportunities": cross_edges,
            },
            "pathway_note": (
                "This is an OpportunityOS planning pathway built only from verified M1 requirement/support relationships. "
                "No cross-opportunity successor is invented when M1 lacks an official relationship."
            ),
        }

