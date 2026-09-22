from pathlib import Path

from fastapi.testclient import TestClient

from server.app import app
from server.adapters import sanitize_profile
from modules.M2_eligibility_graph.pathway.goal_pathway_builder import GoalPathwayBuilder
from modules.M2_eligibility_graph.graph.graph_engine import OpportunityGraph

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_profile_defaults_selected_goal_to_general_readiness():
    p = sanitize_profile({
        "age": 24,
        "state": "Tamil Nadu",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea",
    })
    assert p["selected_goal"] == "GENERAL_READINESS"
    assert p["business_goal"] is None


def test_profile_preserves_disability_and_selected_goal():
    p = sanitize_profile({
        "age": 24,
        "state": "Tamil Nadu",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea",
        "disability_status": "PERSON_WITH_DISABILITY",
        "selected_goal": "WORKING_CAPITAL",
    })
    assert p["disability_status"] == "PERSON_WITH_DISABILITY"
    assert p["selected_goal"] == "WORKING_CAPITAL"
    # Legacy compatibility for consumers that still use business_goal.
    assert p["business_goal"] == "WORKING_CAPITAL"


def test_old_business_goal_migrates_to_selected_goal():
    p = sanitize_profile({"business_goal": "START_BUSINESS"})
    assert p["selected_goal"] == "START_BUSINESS"
    assert p["business_goal"] == "START_BUSINESS"


def test_invalid_disability_is_sanitized_and_custom_goal_is_preserved():
    p = sanitize_profile({
        "disability_status": "UNKNOWN_VALUE",
        "selected_goal": "Build a rural tailoring enterprise",
    })
    assert p["disability_status"] is None
    assert p["selected_goal"] == "Build a rural tailoring enterprise"


def test_goal_pathway_uses_general_readiness_by_default_and_exposes_disability():
    res = GoalPathwayBuilder().build(profile={
        "age": 24,
        "state": "Tamil Nadu",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea",
        "disability_status": "PERSON_WITH_DISABILITY",
        "selected_goal": "GENERAL_READINESS",
    })
    assert res["pathway_type"] == "GENERAL_READINESS"
    assert res["goal"]["normalized_key"] == "GENERAL_READINESS"
    assert res["goal"]["display_label"] == "General Business Readiness"
    assert res["current_state_summary"]["disability_status"] == "PERSON_WITH_DISABILITY"
    assert res["current_state_summary"]["selected_goal"] == "GENERAL_READINESS"


def test_goal_pathway_uses_selected_goal_when_changed():
    res = GoalPathwayBuilder().build(profile={
        "age": 24,
        "state": "Tamil Nadu",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea",
        "selected_goal": "EXPORT_DEVELOPMENT",
    })
    assert res["pathway_type"] == "GOAL_SPECIFIC"
    assert res["goal"]["normalized_key"] == "EXPORT_DEVELOPMENT"
    assert res["goal"]["display_label"] == "Export development & market expansion"


def test_goal_pathway_api_respects_selected_goal_profile_field():
    res = client.post("/api/pathway/goal/generate", json={
        "profile": {
            "age": 24,
            "state": "Tamil Nadu",
            "sector": "Agriculture & Allied",
            "business_stage": "Idea",
            "disability_status": "NONE",
            "selected_goal": "WORKING_CAPITAL",
        }
    })
    assert res.status_code == 200
    body = res.json()
    assert body["goal"]["normalized_key"] == "WORKING_CAPITAL"
    assert body["current_state_summary"]["disability_status"] == "NONE"


def test_analyze_returns_new_profile_fields_without_changing_matching_contract():
    res = client.post("/api/analyze", json={
        "profile": {
            "age": 24,
            "state": "Tamil Nadu",
            "sector": "Agriculture & Allied",
            "business_stage": "Idea",
            "disability_status": "PREFER_NOT_TO_SAY",
            "selected_goal": "GENERAL_READINESS",
        }
    })
    assert res.status_code == 200
    body = res.json()
    assert body["profile"]["disability_status"] == "PREFER_NOT_TO_SAY"
    assert body["profile"]["selected_goal"] == "GENERAL_READINESS"


def test_graph_profile_and_goal_nodes_include_new_context():
    profile = {
        "age": 24,
        "gender": "Female",
        "state": "Tamil Nadu",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea",
        "disability_status": "PERSON_WITH_DISABILITY",
        "selected_goal": "WORKING_CAPITAL",
    }
    # A single candidate is enough to validate profile/goal context propagation.
    graph = OpportunityGraph().build_personalized_graph(
        profile=profile,
        candidate_evaluations=[],
        selection_mode="TOP_3",
        limit=3,
    )
    profile_node = next(n for n in graph["nodes"] if n["id"] == "node_profile")
    goal_node = next(n for n in graph["nodes"] if n["id"] == "node_goal")
    assert profile_node["metadata"]["disability_status"] == "PERSON_WITH_DISABILITY"
    assert goal_node["label"] == "Working capital assistance"


def test_profile_form_has_new_dropdowns_and_default_goal():
    src = (ROOT / "frontend" / "profile_form.js").read_text(encoding="utf-8")
    assert 'id="inpDisabilityStatus"' in src
    assert 'id="inpSelectedGoal"' in src
    assert 'value="GENERAL_READINESS"' in src
    assert "handleInput('selected_goal'" in src


def test_my_opportunities_surfaces_both_new_fields():
    src = (ROOT / "frontend" / "my_opportunities.js").read_text(encoding="utf-8")
    assert "profile.disability_status" in src
    assert "profile.selected_goal" in src
    assert "General Business Readiness" in src
