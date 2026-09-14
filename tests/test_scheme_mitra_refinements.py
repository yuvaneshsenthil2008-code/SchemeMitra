from pathlib import Path

from fastapi.testclient import TestClient

from server.app import app
from server.adapters import SUPPORT_FAMILY_MAP
from modules.M3_nlp_ai.nlp.rule_extractor import RuleExtractor

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_public_support_filter_is_simplified_but_covers_all_raw_types():
    assert set(SUPPORT_FAMILY_MAP) == {
        "LOAN_CREDIT",
        "SUBSIDY_GRANT",
        "TRAINING_SKILL",
        "INFRASTRUCTURE_EQUIPMENT",
        "MARKET_EXPORT",
        "OTHER_SUPPORT",
    }
    response = client.get("/api/opportunities", params={"limit": 100})
    assert response.status_code == 200
    raw_types = {x for item in response.json()["items"] for x in item.get("support_types", [])}
    covered = set().union(*SUPPORT_FAMILY_MAP.values())
    assert raw_types <= covered


def test_under18_profile_is_saved_but_not_personally_matched():
    response = client.post("/api/analyze", json={
        "profile": {
            "age": 1,
            "state": "Tamil Nadu",
            "sector": "MSME & Manufacturing",
            "business_stage": "Idea",
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert data["profile"]["age"] == 1
    assert data["best_matches"] == []
    assert data["recommendations"] == []
    assert data["applicability"]["personalized_matching_available"] is False
    assert data["applicability"]["minimum_age"] == 18


def test_location_course_and_ecommerce_extraction_is_evidence_first():
    ext = RuleExtractor()

    profile = ext.extract("I live in Mysuru and I completed B.Tech in Computer Science.")
    assert profile["state"] == "Karnataka"
    assert profile["district"] == "Mysuru"
    assert profile["education"] == "Degree"
    assert profile["education_field"] == "Computer Science"

    ambiguous = ext.extract("I completed computer science.")
    assert ambiguous.get("education_field") == "Computer Science"
    assert "education" not in ambiguous

    shop = ext.extract("I am planning to build an e-shop.")
    assert shop.get("sector") == "MSME & Manufacturing"
    assert shop.get("business_type") == "Idea"


def test_scheme_mitra_brand_and_auto_hide_navigation_present():
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    voice = (ROOT / "frontend" / "profile_builder.js").read_text(encoding="utf-8")

    assert "SchemeMitra" in html
    assert "AI-powered scheme matching for entrepreneurs" in html
    assert "navRevealZone" in html
    assert "setupAutoHideNavbar" in js
    assert "translateY(calc(-100% - 2px))" in css
    assert "voiceSilenceMs = 3000" in voice
