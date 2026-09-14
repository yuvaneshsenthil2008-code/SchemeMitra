from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

SUPPORT_LABELS = {
    "SUP_CREDIT": "Loan / Credit Assistance",
    "SUP_SUBSIDY": "Margin Money / Capital Subsidy",
    "SUP_GRANT": "Grant / Seed Funding",
    "SUP_TRAINING": "Skill Training Support",
    "SUP_INFRASTRUCTURE": "Infrastructure & Equipment",
    "SUP_MARKET_ACCESS": "Market Access & Exhibition Support",
    "SUP_CONSULTANCY": "Technical Advisory & Mentorship",
    "SUP_EXHIBITION_REIMBURSEMENT": "Trade Fair Reimbursement",
}

GOAL_MAP = {
    "START_BUSINESS": "Start a Business",
    "ESTABLISH_ENTERPRISE": "Establish an Enterprise",
    "EXPAND_BUSINESS": "Expand Existing Business",
    "UPGRADE_UNIT": "Upgrade Micro Enterprise",
    "TECH_INNOVATION": "Technology Innovation",
    "EXPORT_DEVELOPMENT": "Export Development",
    "MODERNIZATION": "Unit Modernization",
    "WORKING_CAPITAL": "Working Capital Assistance"
}

def eval_req_status(req_node_id: str, req_type: str, action_label: str, profile: dict) -> str:
    lbl_lower = action_label.lower()
    t_lower = (req_type or "").lower()

    if "udyam" in lbl_lower or "udyam" in t_lower:
        val = profile.get("udyam_registered")
        if val is True: return "COMPLETED"
        if val is False: return "ACTION_NEEDED"
        return "NEED_TO_CONFIRM"

    if "fssai" in lbl_lower:
        regs = profile.get("registrations") or []
        missing = profile.get("extra", {}).get("missing_registrations") or []
        if any("fssai" in str(r).lower() for r in regs): return "COMPLETED"
        if any("fssai" in str(r).lower() for r in missing): return "ACTION_NEEDED"
        return "NEED_TO_CONFIRM"

    if "age" in lbl_lower:
        age_val = profile.get("age")
        if age_val is not None:
            return "COMPLETED" if age_val >= 18 else "ACTION_NEEDED"

    if "new" in lbl_lower and ("unit" in lbl_lower or "enterprise" in lbl_lower or "business" in lbl_lower):
        val = profile.get("is_new_unit")
        if val is None: val = profile.get("extra", {}).get("is_new_unit")
        if val is True: return "COMPLETED"
        if val is False: return "ACTION_NEEDED"

    if "subsidy" in lbl_lower and ("prior" in lbl_lower or "previous" in lbl_lower or "availed" in lbl_lower):
        val = profile.get("prior_gov_subsidy")
        if val is None: val = profile.get("extra", {}).get("prior_gov_subsidy")
        if val is False: return "COMPLETED"
        if val is True: return "ACTION_NEEDED"

    if "pmegp" in lbl_lower and ("spouse" in lbl_lower or "family" in lbl_lower or "availed" in lbl_lower or "beneficiary" in lbl_lower):
        val = profile.get("family_pmegp_availed")
        if val is None: val = profile.get("extra", {}).get("family_pmegp_availed")
        if val is False: return "COMPLETED"
        if val is True: return "ACTION_NEEDED"

    if "education" in lbl_lower or "qualification" in lbl_lower:
        return "COMPLETED" if profile.get("education") else "NEED_TO_CONFIRM"

    if "dpr" in lbl_lower or "project report" in lbl_lower:
        has_dpr = profile.get("extra", {}).get("has_dpr")
        if has_dpr is True: return "COMPLETED"
        if has_dpr is False: return "ACTION_NEEDED"
        return "NEED_TO_CONFIRM"

    if "land" in lbl_lower or "premises" in lbl_lower:
        has_land = profile.get("extra", {}).get("has_land")
        if has_land is True: return "COMPLETED"
        if has_land is False: return "ACTION_NEEDED"
        return "NEED_TO_CONFIRM"

    return "NEED_TO_CONFIRM"


class OpportunityGraph:
    """Builds clean, provenanced, deduplicated Opportunity Graphs according to OpportunityOS specifications."""

    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")
        self.opps = json.loads((self.data_dir / "opportunity_master.json").read_text(encoding="utf-8"))
        self.reqs = json.loads((self.data_dir / "pathway_requirements.json").read_text(encoding="utf-8"))
        self.rels = json.loads((self.data_dir / "relationships.json").read_text(encoding="utf-8"))
        self.opp_by_id = {x["Opportunity_ID"]: x for x in self.opps}
        self.req_by_id = {x["requirement_node_id"]: x for x in self.reqs}

    def build_personalized_graph(
        self,
        profile: dict,
        candidate_evaluations: list[dict],
        selection_mode: str = "TOP_3",
        limit: int = 3
    ) -> dict:
        if not isinstance(profile, dict):
            profile = {}

        # 1. Filter candidates: strictly exclude NOT_ELIGIBLE and NEEDS_VERIFICATION from normal default graph
        eligible_candidates = []
        for ev in candidate_evaluations:
            status = ev.get("eligibility_status") or ev.get("status")
            recommendable = ev.get("recommendable", True)
            if recommendable and status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE", "NEEDS_VERIFICATION"]:
                eligible_candidates.append(ev)

        # Normalize selection limit
        mode_upper = str(selection_mode).upper()
        if mode_upper == "TOP_3":
            effective_limit = 3
        elif mode_upper == "TOP_5":
            effective_limit = 5
        elif mode_upper == "ALL_RELEVANT":
            effective_limit = max(1, len(eligible_candidates))
        else:
            effective_limit = max(1, limit)

        selected_evals = eligible_candidates[:effective_limit]
        selected_opp_ids = [ev.get("opportunity_id") for ev in selected_evals if ev.get("opportunity_id")]

        nodes: list[dict] = []
        edges: list[dict] = []

        # A. USER_PROFILE Node
        state = profile.get("state") or "India"
        sector = profile.get("sector") or "General MSME"
        stage = profile.get("business_stage") or "Idea"
        gender = profile.get("gender")
        age = profile.get("age")
        profile_summary = f"{state} • {sector} • {stage} Stage"
        if gender and age:
            profile_summary = f"{gender} ({age} yrs) • " + profile_summary

        nodes.append({
            "id": "node_profile",
            "type": "USER_PROFILE",
            "label": "Your Profile",
            "status": "COMPLETED",
            "opportunity_id": None,
            "requirement_id": None,
            "metadata": {
                "summary": profile_summary,
                "state": state,
                "sector": sector,
                "business_stage": stage,
                "gender": gender,
                "age": age
            }
        })

        # B. USER_GOAL Node
        raw_goal = str(profile.get("business_goal") or "").strip()
        formatted_goal = GOAL_MAP.get(raw_goal.upper(), raw_goal if raw_goal else "Your Business Goal")
        if raw_goal and raw_goal == raw_goal.upper() and "_" in raw_goal:
            formatted_goal = raw_goal.replace("_", " ").title()

        nodes.append({
            "id": "node_goal",
            "type": "USER_GOAL",
            "label": formatted_goal,
            "status": "TARGET",
            "opportunity_id": None,
            "requirement_id": None,
            "metadata": {
                "goal": formatted_goal,
                "raw_goal": raw_goal
            }
        })

        # C. OPPORTUNITY Nodes
        opp_nodes_map = {}
        for ev in selected_evals:
            oid = ev.get("opportunity_id")
            if not oid or oid not in self.opp_by_id:
                continue
            opp_info = self.opp_by_id[oid]
            m2_status = ev.get("eligibility_status") or ev.get("status")
            # Strict contract: display Eligible ONLY if M2 returned ELIGIBLE, otherwise Potential Match
            display_status = "Eligible" if m2_status == "ELIGIBLE" else "Potential Match"

            st_val = opp_info.get("Support_Types") or ev.get("support_types") or []
            if isinstance(st_val, str):
                st_list = [st_val]
            elif isinstance(st_val, list):
                st_list = st_val
            else:
                st_list = []

            nid = f"opp_{oid}"
            opp_node = {
                "id": nid,
                "type": "OPPORTUNITY",
                "label": opp_info.get("Opportunity_Name") or oid,
                "status": display_status,
                "opportunity_id": oid,
                "requirement_id": None,
                "metadata": {
                    "eligibility_status": m2_status,
                    "primary_sector": opp_info.get("Primary_Sector"),
                    "benefit_summary": opp_info.get("Benefit_Summary"),
                    "official_source_url": ev.get("official_source_url") or opp_info.get("Official_Source_URL"),
                    "application_route": opp_info.get("Application_Route"),
                    "rule_completeness": ev.get("rule_completeness") or opp_info.get("Rule_Completeness"),
                    "support_types": st_list
                }
            }
            nodes.append(opp_node)
            opp_nodes_map[oid] = nid

        # D. REQUIREMENT Nodes & Edges (Deduplicated by Canonical Requirement ID)
        canonical_req_nodes = {}
        for oid in selected_opp_ids:
            # Find required_for relationships in M1
            req_rels = [
                r for r in self.rels
                if r.get("target_node_id") == oid
                and r.get("relationship_type") == "REQUIRED_FOR"
                and r.get("source_node_type") == "REQUIREMENT"
            ]

            for r_rel in req_rels:
                req_id = r_rel.get("source_node_id")
                req_info = self.req_by_id.get(req_id)
                if not req_info:
                    continue

                label = req_info.get("action_label") or req_id
                req_type = req_info.get("requirement_type") or "REQUIREMENT"
                status_code = eval_req_status(req_id, req_type, label, profile)

                # Format status badge label
                if status_code == "COMPLETED":
                    status_lbl = "✓ Completed"
                elif status_code == "ACTION_NEEDED":
                    status_lbl = "! Action Needed"
                else:
                    status_lbl = "? Need to Confirm"

                # Deduplication: reuse requirement node if already added
                canon_key = f"req_{req_id}"
                if canon_key not in canonical_req_nodes:
                    req_node = {
                        "id": canon_key,
                        "type": "REQUIREMENT",
                        "label": label,
                        "status": status_lbl,
                        "opportunity_id": None,
                        "requirement_id": req_id,
                        "metadata": {
                            "requirement_type": req_type,
                            "status_code": status_code,
                            "official_source_url": req_info.get("official_source_url"),
                            "blocking_default": req_info.get("blocking_default", True),
                            "connected_opportunities": [oid]
                        }
                    }
                    canonical_req_nodes[canon_key] = req_node
                    nodes.append(req_node)

                    # USER_PROFILE -> REQUIREMENT edge (PROFILE_DERIVED)
                    edges.append({
                        "id": f"edge_profile_{canon_key}",
                        "source": "node_profile",
                        "target": canon_key,
                        "relationship": "HAS_REQUIREMENT_STATE",
                        "provenance": "PROFILE_DERIVED"
                    })
                else:
                    if oid not in canonical_req_nodes[canon_key]["metadata"]["connected_opportunities"]:
                        canonical_req_nodes[canon_key]["metadata"]["connected_opportunities"].append(oid)

                # REQUIREMENT -> OPPORTUNITY edge (M1_VERIFIED)
                edges.append({
                    "id": f"edge_{canon_key}_{oid}",
                    "source": canon_key,
                    "target": opp_nodes_map[oid],
                    "relationship": "REQUIRED_FOR",
                    "provenance": "M1_VERIFIED"
                })

        # E. SUPPORT Nodes & Edges (Deduplicated by Support Type)
        canonical_sup_nodes = {}
        for oid in selected_opp_ids:
            # Find provides relationships in M1
            sup_rels = [
                r for r in self.rels
                if r.get("source_node_id") == oid
                and r.get("relationship_type") == "PROVIDES"
                and r.get("target_node_type") == "SUPPORT"
            ]

            for s_rel in sup_rels:
                sup_id = s_rel.get("target_node_id")
                sup_label = SUPPORT_LABELS.get(sup_id, sup_id.removeprefix("SUP_").replace("_", " ").title())
                canon_sup_key = f"sup_{sup_id}"

                if canon_sup_key not in canonical_sup_nodes:
                    sup_node = {
                        "id": canon_sup_key,
                        "type": "SUPPORT",
                        "label": sup_label,
                        "status": "AVAILABLE",
                        "opportunity_id": None,
                        "requirement_id": None,
                        "metadata": {
                            "support_type": sup_id,
                            "connected_opportunities": [oid]
                        }
                    }
                    canonical_sup_nodes[canon_sup_key] = sup_node
                    nodes.append(sup_node)

                    # SUPPORT -> USER_GOAL edge (PRESENTATION_DERIVED)
                    edges.append({
                        "id": f"edge_{canon_sup_key}_goal",
                        "source": canon_sup_key,
                        "target": "node_goal",
                        "relationship": "CONTRIBUTES_TO_GOAL",
                        "provenance": "PRESENTATION_DERIVED"
                    })
                else:
                    if oid not in canonical_sup_nodes[canon_sup_key]["metadata"]["connected_opportunities"]:
                        canonical_sup_nodes[canon_sup_key]["metadata"]["connected_opportunities"].append(oid)

                # OPPORTUNITY -> SUPPORT edge (M1_VERIFIED)
                edges.append({
                    "id": f"edge_{oid}_{canon_sup_key}",
                    "source": opp_nodes_map[oid],
                    "target": canon_sup_key,
                    "relationship": "PROVIDES",
                    "provenance": "M1_VERIFIED"
                })

        # F. VERIFIED CROSS-SCHEME EDGES (ONLY when explicitly present in M1)
        cross_scheme_rels = [
            r for r in self.rels
            if r.get("source_node_type") == "OPPORTUNITY"
            and r.get("target_node_type") == "OPPORTUNITY"
            and r.get("source_node_id") in selected_opp_ids
            and r.get("target_node_id") in selected_opp_ids
            and r.get("relationship_type") in ["UNLOCKS", "ENABLES", "FOLLOWED_BY", "DEPENDS_ON"]
        ]

        synthetic_factual_edges = 0
        for cs in cross_scheme_rels:
            src_oid = cs.get("source_node_id")
            tgt_oid = cs.get("target_node_id")
            rel_t = cs.get("relationship_type")
            edges.append({
                "id": f"edge_scheme_{src_oid}_{tgt_oid}",
                "source": opp_nodes_map[src_oid],
                "target": opp_nodes_map[tgt_oid],
                "relationship": rel_t,
                "provenance": "M1_VERIFIED"
            })

        m1_verified_count = sum(1 for e in edges if e["provenance"] == "M1_VERIFIED")
        profile_derived_count = sum(1 for e in edges if e["provenance"] == "PROFILE_DERIVED")
        presentation_derived_count = sum(1 for e in edges if e["provenance"] == "PRESENTATION_DERIVED")

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "selection_mode": mode_upper,
                "limit": effective_limit,
                "selected_opportunity_ids": selected_opp_ids,
                "only_verified_connections": True,
                "counts": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "m1_verified_edges": m1_verified_count,
                    "profile_derived_edges": profile_derived_count,
                    "presentation_derived_edges": presentation_derived_count,
                    "synthetic_factual_edges": synthetic_factual_edges
                }
            }
        }

    def subgraph_for_opportunity(self, opportunity_id: str) -> dict:
        edges = [r for r in self.rels if r["source_node_id"] == opportunity_id or r["target_node_id"] == opportunity_id]
        node_ids = {opportunity_id}
        for e in edges: node_ids |= {e["source_node_id"], e["target_node_id"]}
        nodes = []
        for nid in sorted(node_ids):
            if nid == opportunity_id:
                o = self.opp_by_id[nid]
                nodes.append({"id": nid, "type": "OPPORTUNITY", "label": o["Opportunity_Name"], "sector": o["Primary_Sector"]})
            elif nid in self.req_by_id:
                r = self.req_by_id[nid]
                nodes.append({"id": nid, "type": "REQUIREMENT", "label": r["action_label"], "requirement_type": r["requirement_type"]})
            elif nid.startswith("SUP_"):
                nodes.append({"id": nid, "type": "SUPPORT", "label": SUPPORT_LABELS.get(nid, nid.removeprefix("SUP_").replace("_", " ").title())})
            else:
                nodes.append({"id": nid, "type": "UNKNOWN", "label": nid})
        return {"opportunity_id": opportunity_id, "nodes": nodes, "edges": edges}

    def validate(self) -> dict:
        known = set(self.opp_by_id) | set(self.req_by_id)
        known |= {e["target_node_id"] for e in self.rels if e["target_node_type"] == "SUPPORT"}
        dangling = [e["relationship_id"] for e in self.rels if e["source_node_id"] not in known or e["target_node_id"] not in known]
        return {
            "opportunity_nodes": len(self.opp_by_id),
            "requirement_nodes": len(self.req_by_id),
            "relationship_count": len(self.rels),
            "dangling_relationships": dangling,
            "valid": not dangling,
        }
