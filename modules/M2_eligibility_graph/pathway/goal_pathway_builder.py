"""
SchemeMitra — Deterministic Goal Pathway Builder Module
Assembles multi-stage, goal-oriented pathways using M1 verified data, M2 eligibility/gaps, M4 recommendations, and frontend user-progress overlay.
"""

from __future__ import annotations
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from ..models.profile import EntrepreneurProfile
from ..engine.eligibility_engine import EligibilityEngine
from ..engine.gap_analysis import GapAnalyzer
from ..graph.graph_engine import OpportunityGraph
from .requirement_presentation import format_requirement_presentation

GOAL_MAP = {
    "GENERAL_READINESS": "General Business Readiness",
    "START_BUSINESS": "Start a new business",
    "ESTABLISH_ENTERPRISE": "Establish a new micro-enterprise",
    "EXPAND_BUSINESS": "Expand existing business unit",
    "GROW_BUSINESS": "Expand existing business unit",
    "UPGRADE_UNIT": "Upgrade micro enterprise unit",
    "TECH_INNOVATION": "Technology innovation & commercialization",
    "EXPORT_DEVELOPMENT": "Export development & market expansion",
    "WORKING_CAPITAL": "Working capital assistance"
}

VAGUE_GOALS = {"make money", "help me", "grow", "business", "money", "success", "earn", "income"}

def format_business_goal_label(goal: Optional[str]) -> tuple[str, str]:
    """Returns (normalized_key, display_label). If vague, flags for clarification."""
    if not goal:
        return ("NONE", "General Business Readiness")
    
    g_str = str(goal).strip()
    g_lower = g_str.lower()
    
    if g_lower in VAGUE_GOALS or len(g_str) < 3:
        return ("NEEDS_CLARIFICATION", g_str)
        
    g_upper = g_str.upper()
    if g_upper in GOAL_MAP:
        return (g_upper, GOAL_MAP[g_upper])
        
    for k, label in GOAL_MAP.items():
        if k.lower() in g_lower or label.lower() in g_lower:
            return (k, label)
            
    if g_str.isupper() and "_" in g_str:
        return (g_upper, g_str.replace("_", " ").title())
        
    return ("CUSTOM_GOAL", g_str)


class GoalPathwayBuilder:
    """Builds a deterministic, evidence-grounded Goal Pathway for SchemeMitra."""

    def __init__(self, data_dir: Optional[Path | str] = None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")
        self.m1_dir = self.data_dir.parents[1] / "M1_data"
        self.eligibility = EligibilityEngine(self.data_dir)
        self.gaps = GapAnalyzer(self.data_dir)
        self.graph = OpportunityGraph(self.data_dir)
        self.opps = {o["Opportunity_ID"]: o for o in self.eligibility.opportunities}

        self.pathway_reqs_by_opp = {}
        reqs_file = self.m1_dir / "pathway_requirements.json"
        if reqs_file.exists():
            try:
                records = json.loads(reqs_file.read_text(encoding="utf-8"))
                for r in records:
                    oid = r.get("opportunity_id")
                    if oid:
                        if oid not in self.pathway_reqs_by_opp:
                            self.pathway_reqs_by_opp[oid] = []
                        self.pathway_reqs_by_opp[oid].append(r)
            except Exception:
                self.pathway_reqs_by_opp = {}

    def build(
        self,
        profile: Optional[EntrepreneurProfile | dict] = None,
        candidate_evaluations: Optional[List[Dict[str, Any]]] = None,
        user_progress_overlay: Optional[Dict[str, Any]] = None,
        force_general: bool = False,
        business_goal: Optional[str] = None,
        m4_data_dir: Optional[Path | str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Assembles the complete Goal Pathway response conforming to approved contract."""

        if profile is None:
            ep = EntrepreneurProfile()
        elif isinstance(profile, dict):
            ep = EntrepreneurProfile.from_dict(profile)
        else:
            ep = profile

        if business_goal:
            ep.selected_goal = business_goal
            ep.business_goal = None if business_goal == "GENERAL_READINESS" else business_goal

        raw_profile_dict = ep.to_dict() if hasattr(ep, "to_dict") else {}

        # 1. Goal Resolution & Clarification Check
        raw_goal = ep.selected_goal or ep.business_goal or (raw_profile_dict.get("extra") or {}).get("selected_goal") or (raw_profile_dict.get("extra") or {}).get("business_goal") or "GENERAL_READINESS"
        goal_key, goal_label = format_business_goal_label(raw_goal)

        if goal_key == "NEEDS_CLARIFICATION" and not force_general:
            return {
                "pathway_id": "pathway_needs_clarification",
                "pathway_type": "NEEDS_CLARIFICATION",
                "goal": {
                    "raw_text": raw_goal,
                    "normalized_key": "NEEDS_CLARIFICATION",
                    "status": "NEEDS_CLARIFICATION"
                },
                "clarification_prompt": {
                    "question": "What are you hoping to do next?",
                    "options": [
                        {"key": "START_BUSINESS", "label": "Start a new business"},
                        {"key": "EXPAND_BUSINESS", "label": "Expand existing business unit"},
                        {"key": "WORKING_CAPITAL", "label": "Seek funding or working capital"},
                        {"key": "EXPORT_DEVELOPMENT", "label": "Explore export opportunities"}
                    ]
                },
                "disclaimer": "Please clarify your primary business objective to generate a goal-specific pathway."
            }

        is_general = force_general or goal_key in ("NONE", "GENERAL_READINESS")

        # 2. Extract Overlay State
        completed_overlay_ids: Set[str] = set()
        if user_progress_overlay and isinstance(user_progress_overlay, dict):
            comp_list = user_progress_overlay.get("completed_requirements") or []
            for item in comp_list:
                if isinstance(item, dict):
                    rid = item.get("requirement_id")
                    st = item.get("status")
                    if rid and (st == "COMPLETED" or item.get("confirmed_by_user")):
                        completed_overlay_ids.add(rid)

        # 3. Candidate Evaluation Selection (M4 order preserved)
        if not candidate_evaluations:
            all_evals = self.eligibility.evaluate_all(ep)
            candidate_evaluations = [e for e in all_evals if e.get("status") != "NOT_ELIGIBLE"]

        # Limit to top 3 matched candidates for MVP pathway representation
        matched_candidates = candidate_evaluations[:3]

        # 4. Construct Sections
        section_a_steps = []
        section_b_steps = []
        section_c_steps = []
        next_actions_list = []

        seen_b_req_ids = set()

        # Section A: Matched Opportunities
        for ev in matched_candidates:
            opp_id = ev.get("opportunity_id")
            opp_info = self.opps.get(opp_id) or {}
            opp_name = opp_info.get("Opportunity_Name") or ev.get("opportunity_name") or opp_id
            st_code = ev.get("status") or ev.get("eligibility_status") or "POTENTIALLY_ELIGIBLE"
            
            st_label = "Eligible" if st_code == "ELIGIBLE" else ("Needs Verification" if st_code == "NEEDS_VERIFICATION" else "Potential Match")
            
            sups = opp_info.get("Support_Types") or []
            if isinstance(sups, str):
                sups = [s.strip() for s in sups.split(";") if s.strip()]

            section_a_steps.append({
                "step_id": f"step_opp_{opp_id.lower()}",
                "opportunity_id": opp_id,
                "opportunity_name": opp_name,
                "source_opportunity_id": opp_id,
                "source_opportunity_name": opp_name,
                "step_type": "SCHEME",
                "title": opp_name,
                "status": st_code,
                "status_label": st_label,
                "basis": "MATCHED_OPPORTUNITY",
                "ui_label": "Matched Opportunity",
                "relationship_classification": "RELEVANT_SUPPORT_OPTIONS",
                "verified_support_types": sups,
                "verified_benefit_summary": opp_info.get("Benefit_Summary") or "Government scheme assistance under official guidelines.",
                "official_source_url": opp_info.get("Official_Source_URL") or opp_info.get("Application_URL") or "https://myscheme.gov.in/"
            })

            # Section B: Requirement Progress (M2 Gap Evaluation)
            gaps = self.gaps.analyze(ep, opp_id)
            m2_req_items = self.pathway_reqs_by_opp.get(opp_id) or []

            # Build base state lookup from M2 Gap Analyzer
            m2_state_map = {}
            for x in gaps.get("completed_requirements", []):
                m2_state_map[x["requirement_node_id"]] = "COMPLETED"
            for x in gaps.get("action_gaps", []):
                m2_state_map[x["requirement_node_id"]] = "ACTION_NEEDED"
            for x in gaps.get("unverified_or_generic_requirements", []):
                m2_state_map[x["requirement_node_id"]] = "NEEDS_CONFIRMATION"

            for r_node in m2_req_items:
                nid = r_node.get("requirement_node_id")
                if not nid or nid in seen_b_req_ids:
                    continue
                seen_b_req_ids.add(nid)

                base_st = m2_state_map.get(nid, "NEEDS_CONFIRMATION")
                is_overlay = nid in completed_overlay_ids

                if is_overlay:
                    final_st = "COMPLETED"
                    final_st_label = "✓ Completed"
                    final_basis = "CONFIRMED_USER_PROGRESS"
                    final_ui_label = "User-Confirmed Completion"
                else:
                    final_st = base_st
                    final_st_label = "! Action Needed" if base_st == "ACTION_NEEDED" else ("✓ Completed" if base_st == "COMPLETED" else "? Need to Confirm")
                    final_basis = "VERIFIED_REQUIREMENT"
                    final_ui_label = "Verified Scheme Requirement"

                req_type_val = r_node.get("requirement_type", "DOCUMENT")
                pres = format_requirement_presentation(r_node)
                canonical_title = pres["canonical_title"]
                display_title = pres["display_title"]
                supporting_text = pres["supporting_text"]

                step_item = {
                    "step_id": f"step_req_{nid.lower()}",
                    "node_id": nid,
                    "requirement_id": nid,
                    "opportunity_id": opp_id,
                    "opportunity_name": opp_name,
                    "source_opportunity_id": opp_id,
                    "source_opportunity_name": opp_name,
                    "step_type": "REQUIREMENT",
                    "requirement_type": req_type_val,
                    "canonical_title": canonical_title,
                    "display_title": display_title,
                    "title": display_title,
                    "supporting_text": supporting_text,
                    "status": final_st,
                    "status_label": final_st_label,
                    "basis": final_basis,
                    "ui_label": final_ui_label,
                    "source_scope": "OPPORTUNITY_OFFICIAL_SOURCE",
                    "official_source_url": r_node.get("official_source_url") or opp_info.get("Official_Source_URL") or "https://myscheme.gov.in/"
                }

                section_b_steps.append(step_item)

                # Next Actions list (Unresolved Actions Only)
                if final_st in ("ACTION_NEEDED", "NEEDS_CONFIRMATION"):
                    next_actions_list.append({
                        "step_id": f"step_req_{nid.lower()}",
                        "node_id": nid,
                        "requirement_id": nid,
                        "opportunity_id": opp_id,
                        "opportunity_name": opp_name,
                        "source_opportunity_id": opp_id,
                        "source_opportunity_name": opp_name,
                        "requirement_type": req_type_val,
                        "canonical_title": canonical_title,
                        "display_title": display_title,
                        "title": display_title,
                        "supporting_text": supporting_text,
                        "status": final_st,
                        "status_label": final_st_label,
                        "basis": final_basis,
                        "official_source_url": step_item["official_source_url"]
                    })

            # Section C: Verified Support / Benefits
            for st_code in sups:
                disp_label = "Credit Support" if st_code == "CREDIT" else ("Subsidy Support" if st_code == "SUBSIDY" else f"{st_code.replace('_', ' ').title()} Support")
                section_c_steps.append({
                    "step_id": f"step_sup_{opp_id.lower()}_{st_code.lower()}",
                    "step_type": "SUPPORT_BENEFIT",
                    "source_opportunity_id": opp_id,
                    "source_opportunity_name": opp_name,
                    "opportunity_name": opp_name,
                    "support_type": st_code,
                    "display_label": disp_label,
                    "benefit_summary": opp_info.get("Benefit_Summary") or "Verified support under official scheme guidelines.",
                    "basis": "VERIFIED_RELATIONSHIP",
                    "ui_label": "Verified Relationship",
                    "source_scope": "OPPORTUNITY_OFFICIAL_SOURCE",
                    "official_source_url": opp_info.get("Official_Source_URL") or "https://myscheme.gov.in/"
                })

        # Prefer ACTION_NEEDED items before NEEDS_CONFIRMATION in Next Actions list
        next_actions_list.sort(key=lambda x: 0 if x.get("status") == "ACTION_NEEDED" else 1)

        # Calculate Total Section Steps (Unique section steps across A, B, C)
        total_section_steps = len(section_a_steps) + len(section_b_steps) + len(section_c_steps)

        sections = []
        if section_a_steps:
            sections.append({
                "section_id": "sec_matched_opportunities",
                "title": "Section A: Matched Opportunities",
                "ordering_basis": "MATCHED_RECOMMENDATION",
                "steps": section_a_steps
            })
        if section_b_steps:
            sections.append({
                "section_id": "sec_requirements",
                "title": "Section B: Requirement Progress",
                "ordering_basis": "VERIFIED_REQUIREMENTS",
                "steps": section_b_steps
            })
        if section_c_steps:
            sections.append({
                "section_id": "sec_support",
                "title": "Section C: Verified Support / Benefits",
                "ordering_basis": "VERIFIED_RELATIONSHIP",
                "steps": section_c_steps
            })

        return {
            "pathway_id": f"pathway_goal_{(goal_key.lower() if not is_general else 'general')}",
            "pathway_type": "GENERAL_READINESS" if is_general else "GOAL_SPECIFIC",
            "goal": {
                "raw_text": raw_goal or "General Business Readiness",
                "normalized_key": goal_key,
                "display_label": goal_label,
                "status": "CONFIRMED"
            },
            "current_state_summary": {
                "business_stage": ep.business_stage or "Idea",
                "sector": ep.sector or "Not specified",
                "available_capital": ep.available_capital,
                "disability_status": ep.disability_status,
                "selected_goal": ep.selected_goal or "GENERAL_READINESS",
                "known_facts_count": sum(
                    v not in (None, "", [], {})
                    for k, v in ep.__dict__.items()
                    if k not in {"extra", "selected_goal"} or (k == "selected_goal" and v not in (None, "", "GENERAL_READINESS"))
                )
            },
            "summary": {
                "total_steps": total_section_steps,
                "total_steps_definition": "Total count of unique section steps across Sections A through C",
                "unresolved_actions_count": len(next_actions_list),
                "matched_schemes_count": len(matched_candidates),
                "ordering_basis": "VERIFIED_REQUIREMENTS",
                "ordering_disclaimer": "Pathway sections generated from verified M1 datasets and M2 eligibility evaluations."
            },
            "next_actions": next_actions_list,
            "sections": sections
        }
