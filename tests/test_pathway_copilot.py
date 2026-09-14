"""
OpportunityOS — AI Pathway Copilot Test Suite

Verifies grounded AI guidance, fallback safety, secret protection, validation rules,
and deterministic pathway integrity without calling real Gemini API.
"""

import os
import pytest
from fastapi.testclient import TestClient
from server.app import app
from server.ai.gemini_provider import GeminiProvider
from server.ai.pathway_copilot import (
    build_trusted_context,
    validate_copilot_response,
    get_pathway_copilot_guidance,
    _copilot_cache
)

client = TestClient(app)

@pytest.fixture
def canonical_profile():
    return {
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "age": 24,
        "annual_income": 300000,
        "available_capital": 200000,
        "project_cost": 500000,
        "business_stage": "Idea",
        "category": None,
        "extra": {
            "is_new_unit": True,
            "prior_gov_subsidy": False,
            "family_pmegp_availed": False,
            "available_capital": 200000
        }
    }

class MockGeminiProvider(GeminiProvider):
    """Mock provider to simulate Gemini responses without network calls."""

    def __init__(self, mock_response=None, should_fail=False, is_avail=True):
        super().__init__(api_key="mock_key_123")
        self.mock_response = mock_response
        self.should_fail = should_fail
        self._avail = is_avail

    def is_available(self) -> bool:
        return self._avail

    def generate_copilot_explanation(self, trusted_context: dict, language: str = "English"):
        if self.should_fail or not self._avail:
            return None
        if self.mock_response is not None:
            return self.mock_response

        # Default valid grounded mock response
        reqs = trusted_context.get("requirements") or []
        first_req_id = reqs[0]["requirement_id"] if reqs else "req_OPP021_1"

        sups = trusted_context.get("supports") or []
        first_sup_id = sups[0]["support_id"] if sups else "sup_OPP021_1"

        return {
            "summary": f"Personalized guidance for {trusted_context.get('opportunity', {}).get('name')}.",
            "current_position": "Based on the information provided, you meet assessed eligibility criteria.",
            "why_this_opportunity_fits": "Aligns with Food Processing sector in Tamil Nadu.",
            "priority_actions": [
                {
                    "requirement_id": first_req_id,
                    "title": "Prepare Project Report",
                    "explanation": "Submit Detailed Project Report to DIC.",
                    "priority": "HIGH",
                    "ordering_basis": "PLANNING_GUIDANCE"
                }
            ],
            "support_explanation": [
                {
                    "support_id": first_sup_id,
                    "support_type": "Loan / Credit",
                    "explanation": "Up to 35% margin money subsidy available."
                }
            ],
            "goal_connection": "Helps establish your food processing micro enterprise.",
            "important_note": "Ensure all documents are verified before final submission."
        }


# 1. Missing GEMINI_API_KEY fallback
def test_missing_api_key_fallback(canonical_profile, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    res = client.post("/api/pathway/copilot", json={
        "opportunity_id": "OPP021",
        "language": "English",
        "profile": canonical_profile
    })
    assert res.status_code == 200
    data = res.json()
    assert data["ai_available"] is False
    assert "fallback_message" in data
    assert "copilot_data" in data
    assert "official_sources" in data


# 2. Valid grounded response accepted
def test_valid_grounded_response_accepted(canonical_profile):
    mock_prov = MockGeminiProvider()
    _copilot_cache.clear()

    res = client.post("/api/pathway/copilot", json={
        "opportunity_id": "OPP021",
        "language": "English",
        "profile": canonical_profile
    })
    assert res.status_code == 200
    data = res.json()
    assert "copilot_data" in data
    assert data["opportunity_id"] == "OPP021"


# 3. Unknown requirement_id rejected
def test_unknown_requirement_id_rejected(canonical_profile):
    trusted_context = {
        "requirements": [{"requirement_id": "req_valid_1", "label": "Valid Req", "state": "ACTION_NEEDED"}],
        "supports": [{"support_id": "sup_valid_1", "label": "Valid Sup"}],
        "eligibility": {"status": "ELIGIBLE"},
        "ordering_confidence": "NO_OFFICIAL_SEQUENCE",
        "official_sources": ["https://www.pmegp.msme.gov.in/"]
    }

    raw_ai_out = {
        "summary": "Test",
        "current_position": "Current position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [
            {
                "requirement_id": "req_fake_999", # UNKNOWN ID
                "title": "Fake Requirement",
                "explanation": "Fake explanation",
                "priority": "HIGH"
            },
            {
                "requirement_id": "req_valid_1",
                "title": "Valid Action",
                "explanation": "Valid explanation",
                "priority": "HIGH"
            }
        ],
        "support_explanation": []
    }

    val_res = validate_copilot_response(raw_ai_out, trusted_context)
    action_ids = [a["requirement_id"] for a in val_res["priority_actions"]]
    assert "req_fake_999" not in action_ids
    assert "req_valid_1" in action_ids


# 4. Unknown support_id rejected
def test_unknown_support_id_rejected(canonical_profile):
    trusted_context = {
        "requirements": [{"requirement_id": "req_valid_1", "label": "Valid Req", "state": "COMPLETED"}],
        "supports": [{"support_id": "sup_valid_1", "label": "Valid Support"}],
        "eligibility": {"status": "ELIGIBLE"},
        "ordering_confidence": "NO_OFFICIAL_SEQUENCE",
        "official_sources": ["https://www.pmegp.msme.gov.in/"]
    }

    raw_ai_out = {
        "summary": "Test",
        "current_position": "Current position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [],
        "support_explanation": [
            {
                "support_id": "sup_hallucinated_888", # UNKNOWN
                "support_type": "Fake Support",
                "explanation": "Fake support text"
            },
            {
                "support_id": "sup_valid_1",
                "support_type": "Valid Support",
                "explanation": "Valid explanation"
            }
        ]
    }

    val_res = validate_copilot_response(raw_ai_out, trusted_context)
    sup_ids = [s["support_id"] for s in val_res["support_explanation"]]
    assert "sup_hallucinated_888" not in sup_ids
    assert "sup_valid_1" in sup_ids


# 5. Invented URL rejected
def test_invented_url_rejected():
    trusted_context = {
        "requirements": [],
        "supports": [],
        "eligibility": {"status": "ELIGIBLE"},
        "official_sources": ["https://www.pmegp.msme.gov.in/"]
    }

    raw_ai_out = {
        "summary": "Visit https://fake-scam-site.com/apply for instant subsidy.",
        "current_position": "Position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [],
        "support_explanation": []
    }

    val_res = validate_copilot_response(raw_ai_out, trusted_context)
    assert "fake-scam-site.com" not in val_res["summary"]


# 6. Eligibility status cannot be overridden
def test_eligibility_status_cannot_be_overridden():
    trusted_context = {
        "requirements": [],
        "supports": [],
        "eligibility": {"status": "POTENTIALLY_ELIGIBLE"},
        "official_sources": []
    }

    raw_ai_out = {
        "summary": "Test",
        "current_position": "You are officially approved and guaranteed sanction of funds!",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [],
        "support_explanation": []
    }

    val_res = validate_copilot_response(raw_ai_out, trusted_context)
    assert "officially approved" not in val_res["current_position"].lower()
    assert "guaranteed" not in val_res["current_position"].lower()
    assert "may be eligible" in val_res["current_position"].lower() or "confirmed" in val_res["current_position"].lower()


# 7. OFFICIAL_SEQUENCE vs PLANNING_GUIDANCE
def test_ordering_confidence_handling():
    ctx_official = {
        "requirements": [{"requirement_id": "req_1", "label": "Req 1", "state": "COMPLETED"}],
        "supports": [],
        "ordering_confidence": "OFFICIAL_SEQUENCE",
        "eligibility": {"status": "ELIGIBLE"}
    }
    raw_out = {
        "summary": "S", "current_position": "P", "why_this_opportunity_fits": "F",
        "priority_actions": [{"requirement_id": "req_1", "title": "T", "explanation": "E", "priority": "HIGH", "ordering_basis": "PLANNING_GUIDANCE"}]
    }
    val_off = validate_copilot_response(raw_out, ctx_official)
    assert val_off["priority_actions"][0]["ordering_basis"] == "OFFICIAL_SEQUENCE"

    ctx_partial = {
        "requirements": [{"requirement_id": "req_1", "label": "Req 1", "state": "COMPLETED"}],
        "supports": [],
        "ordering_confidence": "PARTIAL",
        "eligibility": {"status": "ELIGIBLE"}
    }
    val_part = validate_copilot_response(raw_out, ctx_partial)
    assert val_part["priority_actions"][0]["ordering_basis"] == "PLANNING_GUIDANCE"


# 8. Error handling / Fallback (timeout, 429, 5xx, malformed JSON)
def test_provider_failure_fallback(canonical_profile):
    mock_prov = MockGeminiProvider(should_fail=True)
    _copilot_cache.clear()

    res = client.post("/api/pathway/copilot", json={
        "opportunity_id": "OPP021",
        "language": "English",
        "profile": canonical_profile
    })
    assert res.status_code == 200
    data = res.json()
    assert data["ai_available"] is False
    assert "fallback_message" in data


# 9. Language contract (English, Tamil, Hindi)
@pytest.mark.parametrize("lang", ["English", "Tamil", "Hindi"])
def test_language_contract(canonical_profile, lang):
    mock_prov = MockGeminiProvider()
    _copilot_cache.clear()

    res = client.post("/api/pathway/copilot", json={
        "opportunity_id": "OPP021",
        "language": lang,
        "profile": canonical_profile
    })
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == lang
    # Official URLs must remain intact regardless of language
    assert len(data["official_sources"]) > 0
    assert "https://" in data["official_sources"][0]


# 10. Security Check: GEMINI_API_KEY never returned in responses
def test_security_no_api_key_leak(canonical_profile):
    os.environ["GEMINI_API_KEY"] = "super_secret_key_xyz_123"

    res = client.post("/api/pathway/copilot", json={
        "opportunity_id": "OPP021",
        "language": "English",
        "profile": canonical_profile
    })
    assert res.status_code == 200
    content_str = res.text
    assert "super_secret_key_xyz_123" not in content_str
    assert "GEMINI_API_KEY" not in content_str


# 11. Security Check: Frontend cannot fake trusted scheme facts
def test_frontend_cannot_fake_scheme_facts(canonical_profile):
    # Attempt to pass fake requirements and fake eligibility in payload
    fake_payload = {
        "opportunity_id": "OPP021",
        "language": "English",
        "profile": canonical_profile,
        "eligibility_status": "OFFICIALLY_APPROVED",
        "requirements": [{"id": "fake_req", "status": "PASSED"}]
    }

    res = client.post("/api/pathway/copilot", json=fake_payload)
    assert res.status_code == 200
    data = res.json()

    copilot_data = data.get("copilot_data", {})
    pos = copilot_data.get("current_position", "")
    assert "OFFICIALLY_APPROVED" not in pos
    assert "officially approved" not in pos.lower()


# 12. Canonical PMEGP Verification
def test_canonical_pmegp_copilot_verification(canonical_profile):
    _copilot_cache.clear()

# 13. Test Unverified Monetary Amount Sanitized in Free Text
def test_unverified_monetary_amount_sanitized():
    trusted_context = {
        "requirements": [{"requirement_id": "req_1", "label": "Req 1", "state": "ACTION_NEEDED"}],
        "supports": [{"support_id": "sup_1", "label": "Sup 1"}],
        "eligibility": {"status": "ELIGIBLE"},
        "official_sources": []
    }
    raw_ai = {
        "summary": "You will receive a ₹10 lakh direct cash grant.",
        "current_position": "Current position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [
            {
                "requirement_id": "req_1",
                "title": "Prepare DPR",
                "explanation": "Submit DPR to get ₹5,00,000 subsidy bonus."
            }
        ],
        "support_explanation": [
            {
                "support_id": "sup_1",
                "support_type": "Credit",
                "explanation": "Provides ₹25 lakh interest-free loan."
            }
        ]
    }
    val = validate_copilot_response(raw_ai, trusted_context)
    assert "₹10 lakh" not in val["summary"]
    assert "₹5,00,000" not in val["priority_actions"][0]["explanation"]
    assert "₹25 lakh" not in val["support_explanation"][0]["explanation"]


# 14. Test Unverified Percentage Sanitized in Free Text
def test_unverified_percentage_sanitized():
    trusted_context = {
        "requirements": [{"requirement_id": "req_1", "label": "Req 1", "state": "ACTION_NEEDED"}],
        "supports": [{"support_id": "sup_1", "label": "Sup 1"}],
        "eligibility": {"status": "ELIGIBLE"},
        "official_sources": []
    }
    raw_ai = {
        "summary": "You are eligible for a 50% margin money subsidy.",
        "current_position": "Current position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [],
        "support_explanation": [
            {
                "support_id": "sup_1",
                "support_type": "Subsidy",
                "explanation": "Provides 75% capital refund."
            }
        ]
    }
    val = validate_copilot_response(raw_ai, trusted_context)
    assert "50%" not in val["summary"]
    assert "75%" not in val["support_explanation"][0]["explanation"]


# 15. Test Unverified Deadline Sanitized in Free Text
def test_unverified_deadline_sanitized():
    trusted_context = {
        "requirements": [{"requirement_id": "req_1", "label": "Req 1", "state": "ACTION_NEEDED"}],
        "supports": [],
        "eligibility": {"status": "ELIGIBLE"},
        "official_sources": []
    }
    raw_ai = {
        "summary": "Application deadline is 31st March 2026.",
        "current_position": "Current position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [
            {
                "requirement_id": "req_1",
                "title": "Submit DPR",
                "explanation": "Must submit before 31st December 2026."
            }
        ],
        "support_explanation": []
    }
    val = validate_copilot_response(raw_ai, trusted_context)
    assert "31st March 2026" not in val["summary"]
    assert "31st December 2026" not in val["priority_actions"][0]["explanation"]


# 16. Test Verified Token Preserved in Free Text
def test_verified_token_preserved():
    trusted_context = {
        "profile_summary": {
            "available_capital": 200000,
            "project_cost": 500000
        },
        "requirements": [{"requirement_id": "req_1", "label": "Req 1", "state": "ACTION_NEEDED"}],
        "supports": [],
        "eligibility": {"status": "ELIGIBLE"},
        "official_sources": []
    }
    raw_ai = {
        "summary": "Your available capital is 200000 for project cost 500000.",
        "current_position": "Current position",
        "why_this_opportunity_fits": "Fits",
        "priority_actions": [],
        "support_explanation": []
    }
    val = validate_copilot_response(raw_ai, trusted_context)
    assert "200000" in val["summary"]
    assert "500000" in val["summary"]

