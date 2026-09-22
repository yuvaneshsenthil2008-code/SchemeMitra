import json
from pathlib import Path

from fastapi.testclient import TestClient

from server.app import app
from server.adapters import get_m1_opportunity_master, get_m1_pathway_requirements, get_m1_relationships
from modules.M2_eligibility_graph.engine.eligibility_engine import EligibilityEngine

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def _opp(oid: str):
    return next(o for o in get_m1_opportunity_master() if o["opportunity_id"] == oid)


def test_dataset_counts_after_verified_demographic_expansion():
    assert len(get_m1_opportunity_master()) == 102
    assert len(get_m1_pathway_requirements()) == 379
    assert len(get_m1_relationships()) == 534


def test_every_opportunity_has_demographic_metadata():
    for opp in get_m1_opportunity_master():
        assert isinstance(opp.get("eligible_genders"), list) and opp["eligible_genders"]
        assert isinstance(opp.get("eligible_social_categories"), list) and opp["eligible_social_categories"]
        assert opp.get("disability_eligibility") in {"ANY", "PERSON_WITH_DISABILITY"}
        assert isinstance(opp.get("demographic_benefit_variants"), list)


def test_twees_accepts_female_and_transgender_not_male():
    eng = EligibilityEngine()
    for gender in ("Female", "Transgender"):
        result = eng.evaluate_opportunity({"gender": gender, "state": "Tamil Nadu"}, "OPP061")
        assert not any(x["field"] == "gender" for x in result["failed"])
    result = eng.evaluate_opportunity({"gender": "Male", "state": "Tamil Nadu"}, "OPP061")
    assert result["status"] == "NOT_ELIGIBLE"
    assert any(x["field"] == "gender" for x in result["failed"])


def test_aabcs_is_sc_st_targeted():
    eng = EligibilityEngine()
    for category in ("SC", "ST"):
        result = eng.evaluate_opportunity({"category": category, "state": "Tamil Nadu"}, "OPP071")
        assert not any(x["field"] == "category" for x in result["failed"])
    result = eng.evaluate_opportunity({"category": "General", "state": "Tamil Nadu"}, "OPP071")
    assert result["status"] == "NOT_ELIGIBLE"


def test_nmdfc_fills_verified_minority_coverage_gap():
    opp = _opp("OPP101")
    assert opp["eligible_social_categories"] == ["Minority"]
    assert opp["official_source_url"] == "https://nmdfc.org/credit-2"
    eng = EligibilityEngine()
    eligible = eng.evaluate_opportunity({"category": "Minority", "annual_income": 600000}, "OPP101")
    assert not eligible["failed"]
    general = eng.evaluate_opportunity({"category": "General", "annual_income": 600000}, "OPP101")
    assert general["status"] == "NOT_ELIGIBLE"


def test_ndfdc_fills_verified_disability_coverage_gap():
    opp = _opp("OPP102")
    assert opp["disability_eligibility"] == "PERSON_WITH_DISABILITY"
    assert "ndfdc.nic.in" in opp["official_source_url"]
    eng = EligibilityEngine()
    pwd = eng.evaluate_opportunity({"age": 25, "disability_status": "PERSON_WITH_DISABILITY"}, "OPP102")
    assert not pwd["failed"]
    non_pwd = eng.evaluate_opportunity({"age": 25, "disability_status": "NONE"}, "OPP102")
    assert non_pwd["status"] == "NOT_ELIGIBLE"


def test_pmegp_has_verified_profile_specific_special_category_terms():
    opp = _opp("OPP021")
    variants = opp["demographic_benefit_variants"]
    assert variants
    variant = variants[0]
    assert "5%" in variant["benefit_summary"]
    assert "25%" in variant["benefit_summary"]
    assert "35%" in variant["benefit_summary"]
    assert "kviconline.gov.in" in variant["source_url"]


def test_public_scheme_api_exposes_demographic_metadata_and_all_102_records():
    listing = client.get("/api/opportunities", params={"limit": 200})
    assert listing.status_code == 200
    assert listing.json()["total"] == 102
    assert len(listing.json()["items"]) == 102
    detail = client.get("/api/opportunities/OPP101")
    assert detail.status_code == 200
    body = detail.json()
    assert body["eligible_social_categories"] == ["Minority"]
    assert body["demographic_targeting"] is True


def test_demographic_targeting_reaches_analysis_without_overriding_m2():
    minority_profile = {
        "age": 30,
        "gender": "Female",
        "category": "Minority",
        "state": "Tamil Nadu",
        "sector": "MSME & Manufacturing",
        "business_stage": "Idea",
        "annual_income": 600000,
        "selected_goal": "START_BUSINESS",
    }
    response = client.post("/api/analyze", json={"profile": minority_profile})
    assert response.status_code == 200
    body = response.json()
    surfaced = (body.get("recommendations") or []) + (body.get("more_information_needed") or [])
    ids = {item.get("opportunity_id") for item in surfaced}
    assert "OPP101" in ids


def test_goal_pathway_ui_hides_total_steps_but_backend_contract_remains():
    js = (ROOT / "frontend" / "my_opportunities.js").read_text(encoding="utf-8")
    assert "Total Pathway Steps" not in js
    # Backend summary may retain total_steps for compatibility; only the UI card is intentionally removed.


def test_second_extraction_replaces_prior_auto_detected_fields_only():
    js = (ROOT / "frontend" / "profile_builder.js").read_text(encoding="utf-8")
    assert "priorDetectedFields" in js
    assert "extractionBaseProfile" in js
    assert "previousDetected.forEach" in js
    assert "nextProfile._detectedFields = detectedSet" in js


def test_scheme_detail_supports_demographic_labels_and_conditional_profile_benefit():
    js = (ROOT / "frontend" / "scheme_detail.js").read_text(encoding="utf-8")
    assert "getPersonalizedDemographicBenefit" in js
    assert "demographicVariantMatches" in js
    assert "detail_profile_specific_benefit" in js
    assert "eligible_genders" in js
    assert "eligible_social_categories" in js
    assert "personalizedDemographicBenefit ?" in js


def test_home_fallback_counts_updated_and_catalogue_fetch_can_return_all_records():
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    assert 'id="statSchemes">102<' in html
    assert 'id="statRequirements">379<' in html
    assert 'id="statRelationships">534<' in html
    assert '/api/opportunities?limit=200' in js
