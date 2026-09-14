"""
SchemeMitra — Test Suite for Goal Pathway Builder & API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from server.app import app
from modules.M2_eligibility_graph.pathway.goal_pathway_builder import GoalPathwayBuilder

client = TestClient(app)

def test_goal_pathway_builder_direct_build():
    builder = GoalPathwayBuilder()
    
    # 1. Goal specific build
    res = builder.build(
        profile={
            "age": 30,
            "gender": "Female",
            "state": "Tamil Nadu",
            "sector": "Food Processing",
            "business_stage": "Idea",
            "business_goal": "START_BUSINESS"
        }
    )
    assert res["pathway_type"] == "GOAL_SPECIFIC"
    assert res["goal"]["normalized_key"] == "START_BUSINESS"
    assert "sections" in res
    assert len(res["sections"]) > 0

def test_goal_pathway_vague_goal_clarification():
    builder = GoalPathwayBuilder()
    
    res = builder.build(
        profile={
            "business_goal": "money"
        }
    )
    assert res["pathway_type"] == "NEEDS_CLARIFICATION"
    assert "clarification_prompt" in res
    assert len(res["clarification_prompt"]["options"]) > 0

def test_goal_pathway_api_generate_and_update():
    prof = {
        "age": 28,
        "gender": "Male",
        "state": "Kerala",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea",
        "business_goal": "START_BUSINESS"
    }

    # 1. Generate endpoint
    gen_res = client.post("/api/pathway/goal/generate", json={
        "profile": prof,
        "business_goal": "START_BUSINESS"
    })
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["pathway_type"] == "GOAL_SPECIFIC"

    # 2. Update endpoint — invalid requirement ID must return 400 Bad Request
    invalid_up = client.post("/api/pathway/goal/update", json={
        "profile": prof,
        "business_goal": "START_BUSINESS",
        "completed_requirement_id": "REQ_UDYAM_001",
        "action": "COMPLETE"
    })
    assert invalid_up.status_code == 400
    assert "Invalid requirement_id" in invalid_up.json()["detail"]

    # 3. Update endpoint — mark canonical requirement REQ0086 completed
    up_res = client.post("/api/pathway/goal/update", json={
        "profile": prof,
        "business_goal": "START_BUSINESS",
        "completed_requirement_id": "REQ0086",
        "action": "COMPLETE"
    })
    assert up_res.status_code == 200
    up_data = up_res.json()
    assert "user_progress_overlay" in up_data
    completed = up_data["user_progress_overlay"].get("completed_requirements", [])
    assert any(c["requirement_id"] == "REQ0086" for c in completed)

    # 4. Update endpoint — reopen requirement REQ0086
    reopen_res = client.post("/api/pathway/goal/update", json={
        "profile": prof,
        "business_goal": "START_BUSINESS",
        "user_progress_overlay": up_data["user_progress_overlay"],
        "completed_requirement_id": "REQ0086",
        "action": "REOPEN"
    })
    assert reopen_res.status_code == 200
    reopen_data = reopen_res.json()
    reopened = reopen_data["user_progress_overlay"].get("completed_requirements", [])
    assert not any(c["requirement_id"] == "REQ0086" for c in reopened)
