"""
SchemeMitra — Test Suite for Entity / Organisation Registration Wording & PMEGP URL Correction
"""

import json
import os
import pytest
from modules.M2_eligibility_graph.pathway.goal_pathway_builder import GoalPathwayBuilder

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1_DIR = os.path.join(PROJECT_ROOT, "modules", "M1_data")

def test_entity_registration_wording_in_goal_pathway():
    builder = GoalPathwayBuilder()
    candidate_evals = [
        {"opportunity_id": "OPP013", "opportunity_name": "PMFME – Support to FPOs/SHGs/Producer Cooperatives", "status": "NEEDS_VERIFICATION"},
        {"opportunity_id": "OPP015", "opportunity_name": "PMFME – Branding & Marketing Support", "status": "NEEDS_VERIFICATION"}
    ]
    res = builder.build(
        profile={
            "age": 30,
            "gender": "Female",
            "state": "Tamil Nadu",
            "sector": "Food Processing",
            "business_stage": "Existing",
            "business_goal": "START_BUSINESS"
        },
        candidate_evaluations=candidate_evals
    )
    
    assert res["pathway_type"] == "GOAL_SPECIFIC"
    
    # Check Section B steps (Requirement Progress)
    sec_b_obj = next(s for s in res["sections"] if s.get("section_id") == "sec_requirements")
    sec_b_steps = sec_b_obj["steps"]
    entity_reg_steps = [s for s in sec_b_steps if s.get("requirement_type") == "ENTITY_REGISTRATION"]
    
    assert len(entity_reg_steps) > 0, "Expected at least one ENTITY_REGISTRATION requirement step"
    
    for step in entity_reg_steps:
        assert step["display_title"] == "Register your business/entity if required by this scheme"
        assert step["title"] == "Register your business/entity if required by this scheme"
        assert step["canonical_title"] == "Register the entity/organisation"
        assert step["supporting_text"] == "Exact registration type needs confirmation."
        assert "official_source_url" in step
        assert step["official_source_url"] != ""

    # Check Next Actions to Review list
    next_actions = res.get("next_actions", [])
    entity_reg_next = [a for a in next_actions if a.get("requirement_type") == "ENTITY_REGISTRATION"]
    
    for act in entity_reg_next:
        assert act["display_title"] == "Register your business/entity if required by this scheme"
        assert act["title"] == "Register your business/entity if required by this scheme"
        assert act["canonical_title"] == "Register the entity/organisation"
        assert act["supporting_text"] == "Exact registration type needs confirmation."

def test_centralized_presentation_helper():
    from modules.M2_eligibility_graph.pathway.requirement_presentation import format_requirement_presentation
    
    # 1. ENTITY_REGISTRATION exact type match
    res_entity = format_requirement_presentation({
        "requirement_type": "ENTITY_REGISTRATION",
        "action_label": "Register the entity/organisation"
    })
    assert res_entity["canonical_title"] == "Register the entity/organisation"
    assert res_entity["display_title"] == "Register your business/entity if required by this scheme"
    assert res_entity["supporting_text"] == "Exact registration type needs confirmation."
    
    # 2. Legacy fallback exact string match
    res_legacy = format_requirement_presentation({
        "requirement_type": "CUSTOM_TYPE",
        "action_label": "Register the entity/organisation"
    })
    assert res_legacy["canonical_title"] == "Register the entity/organisation"
    assert res_legacy["display_title"] == "Register your business/entity if required by this scheme"

    # 3. Exact matching safeguard: GROWER_OR_ENTITY_REGISTRATION should NOT be relabeled
    res_grower = format_requirement_presentation({
        "requirement_type": "GROWER_OR_ENTITY_REGISTRATION",
        "action_label": "Register as a Tea/Coffee Grower or Entity"
    })
    assert res_grower["canonical_title"] == "Register as a Tea/Coffee Grower or Entity"
    assert res_grower["display_title"] == "Register as a Tea/Coffee Grower or Entity"

def test_completed_actions_presentation_in_progress_db():
    from server.progress_db import complete_requirement, get_completed_actions
    client_id = "test_client_wording_safeguard"
    
    # Complete an ENTITY_REGISTRATION requirement (REQ0077 is PMKSY Entity Registration in M1)
    complete_requirement(client_id, "REQ0077")
    res = get_completed_actions(client_id)
    
    comp_item = next(item for item in res["completed_actions"] if item["requirement_id"] == "REQ0077")
    assert comp_item["canonical_title"] == "Register the entity/organisation"
    assert comp_item["display_title"] == "Register your business/entity if required by this scheme"
    assert comp_item["title"] == "Register your business/entity if required by this scheme"
    assert comp_item["supporting_text"] == "Exact registration type needs confirmation."

def test_entity_registration_not_shared_artifact():
    builder = GoalPathwayBuilder()
    candidate_evals = [
        {"opportunity_id": "OPP013", "opportunity_name": "PMFME – Support to FPOs/SHGs/Producer Cooperatives", "status": "NEEDS_VERIFICATION"},
        {"opportunity_id": "OPP015", "opportunity_name": "PMFME – Branding & Marketing Support", "status": "NEEDS_VERIFICATION"}
    ]
    res = builder.build(
        profile={
            "age": 30,
            "gender": "Female",
            "state": "Tamil Nadu",
            "sector": "Food Processing",
            "business_stage": "Existing",
            "business_goal": "START_BUSINESS"
        },
        candidate_evaluations=candidate_evals
    )
    
    sec_b_obj = next(s for s in res["sections"] if s.get("section_id") == "sec_requirements")
    sec_b_steps = sec_b_obj["steps"]
    entity_reg_steps = [s for s in sec_b_steps if s.get("requirement_type") == "ENTITY_REGISTRATION"]
    
    # Verify each scheme has its own separate canonical requirement ID and not merged
    node_ids = set(s["node_id"] for s in entity_reg_steps)
    assert len(node_ids) == len(entity_reg_steps), "Canonical requirement IDs must remain separate and unmerged"

def test_pmegp_official_url_and_verification_date():
    master_file = os.path.join(M1_DIR, "opportunity_master.json")
    with open(master_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    pmegp = next((o for o in data if o.get("Opportunity_ID") == "OPP021"), None)
    assert pmegp is not None
    assert pmegp["Official_Source_URL"] == "https://www.pmegp.msme.gov.in/"
    assert pmegp["Last_Verified"] == "2026-09-14"
    assert pmegp["url_health"]["official_source_url_health"]["final_url"] == "https://www.pmegp.msme.gov.in/"

def test_pmegp_requirement_source_links_updated():
    reqs_file = os.path.join(M1_DIR, "pathway_requirements.json")
    with open(reqs_file, "r", encoding="utf-8") as f:
        reqs = json.load(f)
    
    pmegp_reqs = [r for r in reqs if r.get("opportunity_id") == "OPP021"]
    assert len(pmegp_reqs) == 5
    for r in pmegp_reqs:
        assert r["official_source_url"] == "https://www.pmegp.msme.gov.in/"
        assert r["last_verified"] == "2026-09-14"
