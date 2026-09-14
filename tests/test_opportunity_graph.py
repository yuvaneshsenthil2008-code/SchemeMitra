"""
SchemeMitra — Opportunity Graph Unit & Integration Tests
Verifies requirement state mappings, status integrity, and profile state handling.
"""

import pytest
from server.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_opportunity_graph_status_mapping():
    """Verify deterministic eligibility state mapping (ELIGIBLE vs POTENTIALLY_ELIGIBLE)."""
    # 1. Profile with minimal parameters
    profile = {
        "age": 25,
        "gender": "Female",
        "state": "Tamil Nadu",
        "sector": "Manufacturing",
        "business_stage": "Idea",
        "business_goal": "START_BUSINESS"
    }

    response = client.post("/api/analyze", json={"profile": profile})
    assert response.status_code == 200
    data = response.json()

    best_matches = data.get("best_matches", [])
    more_info = data.get("more_information_needed", [])

    all_matches = best_matches + more_info
    assert len(all_matches) > 0, "Analyze endpoint should return matches"

    for scheme in all_matches:
        status = scheme.get("eligibility_status") or scheme.get("status")
        # Ensure status is one of official canonical values
        assert status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE", "NEEDS_VERIFICATION", "NOT_ELIGIBLE"], (
            f"Invalid eligibility status: {status}"
        )


def test_pathway_generation_for_graph_panel():
    """Verify pathway generation API for Opportunity Graph requirement panels."""
    profile = {
        "age": 30,
        "gender": "Male",
        "state": "Tamil Nadu",
        "sector": "Agriculture",
        "business_stage": "Idea",
        "business_goal": "START_BUSINESS"
    }

    # Fetch candidate set to get a valid opportunity ID
    res_analyze = client.post("/api/analyze", json={"profile": profile})
    assert res_analyze.status_code == 200
    analyze_data = res_analyze.json()
    candidates = analyze_data.get("best_matches", []) + analyze_data.get("more_information_needed", [])
    assert len(candidates) > 0

    opp_id = candidates[0]["opportunity_id"]

    # Request pathway for graph panel
    res_pathway = client.post("/api/pathway/generate", json={
        "profile": profile,
        "opportunity_id": opp_id
    })
    assert res_pathway.status_code == 200
    pathway_output = res_pathway.json()

    assert "pathway" in pathway_output
    pathway = pathway_output["pathway"]
    assert "requirements" in pathway
    
    # Check requirement states
    for req in pathway["requirements"]:
        state = str(req.get("state", "")).upper()
        assert state in ["PASSED", "COMPLETED", "GAP", "ACTION_NEEDED", "FAILED", "VERIFY", "UNCONFIRMED", "NEEDS_VERIFICATION"], (
            f"Requirement state '{state}' must map to one of the 3 standard design statuses (Completed, Action Needed, Need to Confirm)"
        )
