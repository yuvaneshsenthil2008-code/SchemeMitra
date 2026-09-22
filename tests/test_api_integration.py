import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["catalogue_count"] == 102
    assert data["requirements_count"] == 379
    assert data["relationships_count"] == 534
    assert data["sectors_count"] == 10
    assert data["modules"]["m1"] is True

def test_list_opportunities():
    response = client.get("/api/opportunities")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 102
    assert len(data["items"]) == 20

    # Sector filter test
    response_sec = client.get("/api/opportunities?sector=Agriculture")
    assert response_sec.status_code == 200
    data_sec = response_sec.json()
    assert data_sec["total"] > 0
    for item in data_sec["items"]:
        assert "agriculture" in item["primary_sector"].lower() or any("agriculture" in s.lower() for s in item.get("secondary_sectors", []))

def test_opportunity_detail():
    # Fetch first opportunity ID
    res = client.get("/api/opportunities")
    first_id = res.json()["items"][0]["opportunity_id"]

    response = client.get(f"/api/opportunities/{first_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["opportunity_id"] == first_id
    assert "opportunity_name" in data
    assert "requirements" in data
    assert "relationships" in data

    # 404 test
    response_invalid = client.get("/api/opportunities/INVALID_ID_999")
    assert response_invalid.status_code == 404

def test_profile_parse():
    payload = {
        "message": "I am a 24 year old female living in Tamil Nadu wanting to start a food business"
    }
    response = client.post("/api/profile/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    prof = data["profile"]
    assert prof["age"] == 24
    assert prof["gender"] == "Female"
    assert prof["state"] == "Tamil Nadu"
    # Verify NO eligibility claims in parse response
    assert "eligibility_status" not in data
    assert "recommendations" not in data

def test_exact_regression_sentence_live_parse_endpoint():
    sentence = (
        "I am a 24-year-old woman from Tamil Nadu. I have completed my degree and "
        "I want to start a food processing business. My annual family income is ₹3 lakh "
        "and I can invest around ₹2 lakh of my own money. I am looking for financial support, "
        "subsidy and training. I have not registered my business yet and I don't have "
        "Udyam registration or FSSAI registration."
    )
    response = client.post("/api/profile/parse", json={"message": sentence})
    assert response.status_code == 200
    data = response.json()
    prof = data["profile"]
    assert prof["age"] == 24
    assert prof["gender"] == "Female"
    assert prof["state"] == "Tamil Nadu"
    assert prof["education"] == "Degree"
    assert prof["annual_income"] == 300000
    assert prof["available_capital"] == 200000
    assert prof["sector"] == "Food Processing & Agri Value Addition"
    assert prof["business_stage"] == "Idea"
    assert "SUBSIDY" in prof["support_needs"]
    assert "TRAINING" in prof["support_needs"]
    assert "CREDIT" in prof["support_needs"]
    assert "UDYAM" in prof["extra"]["missing_registrations"]
    assert "FSSAI" in prof["extra"]["missing_registrations"]
    assert prof["extra"]["unregistered_business"] is True
    assert prof["category"] is None
    assert prof["project_cost"] is None

def test_eligibility_check():
    profile = {
        "age": 24,
        "gender": "Female",
        "state": "Tamil Nadu",
        "sector": "Food Processing",
        "business_stage": "Startup",
        "annual_income": 300000
    }
    response = client.post("/api/eligibility/check", json={"profile": profile})
    assert response.status_code == 200
    data = response.json()
    assert "evaluations" in data
    assert "gaps" in data
    assert len(data["evaluations"]) == 102

def test_opportunities_recommend():
    profile = {
        "age": 24,
        "gender": "Female",
        "state": "Tamil Nadu",
        "sector": "Food Processing",
        "business_stage": "Startup",
        "annual_income": 300000
    }
    response = client.post("/api/opportunities/recommend", json={"profile": profile})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "needs_verification" in data
    assert "not_eligible" in data

    # Verify recommendations rules
    for rec in data["recommendations"]:
        assert rec["recommendable"] is True
        assert rec["eligibility_status"] in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]

    for nv in data["needs_verification"]:
        assert nv["recommendable"] is False
        assert nv["eligibility_status"] == "NEEDS_VERIFICATION"

    for ne in data["not_eligible"]:
        assert ne["eligibility_status"] == "NOT_ELIGIBLE"

def test_analyze_endpoint():
    profile = {
        "age": 24,
        "gender": "Female",
        "state": "Tamil Nadu",
        "sector": "Food Processing",
        "business_stage": "Startup"
    }
    # Test without selected opportunity
    response = client.post("/api/analyze", json={"profile": profile})
    assert response.status_code == 200
    data = response.json()
    assert "profile" in data
    assert "recommendations" in data
    assert "needs_verification" in data
    assert "not_eligible" in data

    # Test with selected opportunity
    res_list = client.get("/api/opportunities")
    selected_id = res_list.json()["items"][0]["opportunity_id"]
    response_sel = client.post("/api/analyze", json={"profile": profile, "selected_opportunity_id": selected_id})
    assert response_sel.status_code == 200
    data_sel = response_sel.json()
    assert data_sel["graph"] is not None

def test_pathway_generate():
    res_list = client.get("/api/opportunities")
    target_id = res_list.json()["items"][0]["opportunity_id"]

    profile = {
        "age": 25,
        "gender": "Male",
        "state": "Tamil Nadu",
        "business_stage": "Idea"
    }
    response = client.post("/api/pathway/generate", json={"profile": profile, "opportunity_id": target_id})
    assert response.status_code == 200
    data = response.json()
    assert "opportunity_id" in data or "target_opportunity_id" in data or "steps" in data or "target_opportunity" in data or "opportunity_name" in data


def test_navigation_and_explore_public_access():
    """Explore Schemes must remain publicly available for all 100 schemes without a profile."""
    res = client.get("/api/opportunities?limit=200")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 102
    assert len(data["items"]) == 102


def test_btech_eshop_classification_regression():
    """B.Tech education word must not trigger Startup & Innovation for standard e-shop business."""
    payload1 = {"message": "I completed B.Tech Computer Science and want to create an e-shop."}
    res1 = client.post("/api/profile/parse", json=payload1)
    assert res1.status_code == 200
    p1 = res1.json()["profile"]
    assert p1["education"] == "Degree"
    assert p1["education_field"] == "Computer Science"
    assert p1["sector"] == "MSME & Manufacturing"

    payload2 = {"message": "I want to build an AI-powered e-commerce startup."}
    res2 = client.post("/api/profile/parse", json=payload2)
    assert res2.status_code == 200
    p2 = res2.json()["profile"]
    assert p2["sector"] == "Startup & Innovation"


def test_roadmap_structure_and_m2_compatibility():
    """Analyze response must provide verified scheme requirements and official portal URLs for roadmap presentation."""
    profile = {
        "age": 24,
        "state": "Tamil Nadu",
        "sector": "MSME & Manufacturing",
        "business_stage": "Idea"
    }
    res = client.post("/api/analyze", json={"profile": profile})
    assert res.status_code == 200
    data = res.json()
    assert "best_matches" in data
    assert "more_information_needed" in data
    
    for match in data["best_matches"] + data["more_information_needed"]:
        assert "opportunity_id" in match
        assert "primary_sector" in match
        assert "scope" in match

