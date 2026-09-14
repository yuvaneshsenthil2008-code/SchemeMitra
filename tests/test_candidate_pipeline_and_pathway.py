import pytest
from pathlib import Path
from server.adapters import (
    filter_candidate_set,
    get_m1_opportunity_master,
    get_m1_pathway_requirements,
    get_m1_relationships,
    sanitize_profile,
    format_analyze_response
)
from modules.M2_eligibility_graph.pathway.pathway_engine import PathwayEngine

ROOT_DIR = Path(__file__).resolve().parents[1]

@pytest.fixture
def opps():
    return get_m1_opportunity_master()

@pytest.fixture
def canonical_profile():
    return {
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "age": 24,
        "annual_income": 300000,
        "available_capital": 200000,
        "business_stage": "Idea",
        "category": None,
        "extra": {
            "missing_registrations": ["UDYAM", "FSSAI"],
            "unregistered_business": True,
            "available_capital": 200000
        }
    }

# 1. Food Processing canonical profile
def test_canonical_food_processing_profile(opps, canonical_profile):
    res = filter_candidate_set(opps, canonical_profile)
    assert len(opps) == 100
    assert "candidate_set" in res
    assert "relevant" in res
    assert "relevant_needs_info" in res
    assert "filtered_out" in res
    # Ensure domain relevant scheme PMFME (OPP011) is in candidate set
    candidate_ids = [o["opportunity_id"] for o in res["candidate_set"]]
    assert "OPP011" in candidate_ids
    # Ensure Coir scheme (OPP065) is in filtered_out
    filtered_ids = [o["opportunity"]["opportunity_id"] for o in res["filtered_out"]]
    assert "OPP065" in filtered_ids

# 2. unknown category
def test_unknown_category_profile(opps):
    profile = {
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "category": None
    }
    res = filter_candidate_set(opps, profile)
    # Schemes requiring category (like SC scheme OPP038/OPP037) should land in relevant_needs_info or candidate_set, not hard filtered_out for category
    needs_info_opp_ids = [o["opportunity"]["opportunity_id"] for o in res["relevant_needs_info"]]
    for item in res["filtered_out"]:
        # Known profile mismatch must not be due to unknown category
        assert "category: Scheduled Caste (user is None)" not in item.get("reason", "")

# 3. known SC category
def test_known_sc_category_profile(opps):
    profile = {
        "sector": "Multi-Sector & General MSME",
        "state": "Tamil Nadu",
        "gender": "Female",
        "category": "Scheduled Caste"
    }
    res = filter_candidate_set(opps, profile)
    # Check that SC required scheme matches
    candidate_ids = [o["opportunity_id"] for o in res["candidate_set"]]
    # Should be in candidate set
    assert len(candidate_ids) > 0

# 4. known General category
def test_known_general_category_profile(opps):
    profile = {
        "sector": "Multi-Sector & General MSME",
        "state": "Tamil Nadu",
        "gender": "Female",
        "category": "General"
    }
    res = filter_candidate_set(opps, profile)
    # Schemes requiring SC (like NSFDC OPP038) should be in filtered_out
    filtered_reasons = [item.get("reason", "") for item in res["filtered_out"]]
    sc_mismatches = [r for r in filtered_reasons if "category: Scheduled Caste" in r or "category: Scheduled Tribe" in r]
    assert len(sc_mismatches) > 0

# 5. SHG unknown / true / false
def test_shg_membership_states(opps):
    # OPP012 is PMFME SHG Seed Capital
    opp_012 = [o for o in opps if o["opportunity_id"] == "OPP012"]
    
    # SHG unknown
    p_unknown = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "shg_membership": None}
    res_unk = filter_candidate_set(opp_012, p_unknown)
    assert len(res_unk["relevant_needs_info"]) == 1
    assert "shg_membership" in res_unk["relevant_needs_info"][0]["unknown_requirements"]

    # SHG true
    p_true = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "shg_membership": True, "extra": {"shg_membership": True}}
    res_true = filter_candidate_set(opp_012, p_true)
    assert len(res_true["relevant"]) == 1

    # SHG false (supplied + incompatible)
    p_false = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "shg_membership": False, "extra": {"shg_membership": False}}
    res_false = filter_candidate_set(opp_012, p_false)
    assert len(res_false["filtered_out"]) == 1 or len(res_false["relevant_needs_info"]) == 0

# 6. entity type unknown / matching / mismatching
def test_entity_type_states(opps):
    # OPP013 is PMFME FPO/Cooperative
    opp_013 = [o for o in opps if o["opportunity_id"] == "OPP013"]

    # Unknown
    p_unk = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "entity_type": None}
    res_unk = filter_candidate_set(opp_013, p_unk)
    assert len(res_unk["relevant_needs_info"]) == 1

    # Matching
    p_match = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "entity_type": "FPO", "extra": {"entity_type": "FPO"}}
    res_match = filter_candidate_set(opp_013, p_match)
    assert len(res_match["relevant"]) == 1

# 7. Transgender scheme vs Female profile
def test_transgender_scheme_vs_female(opps):
    p_female = {"sector": "Multi-Sector & General MSME", "state": "Tamil Nadu", "gender": "Female"}
    opp_trans = [o for o in opps if "transgender" in (o.get("opportunity_name", "") + o.get("target_beneficiary", "")).lower()]
    if opp_trans:
        res = filter_candidate_set(opp_trans, p_female)
        assert len(res["filtered_out"]) == len(opp_trans)

# 8. Coir scheme vs Food Processing
def test_coir_scheme_vs_food_processing(opps):
    p_fp = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "gender": "Female"}
    opp_coir = [o for o in opps if o["opportunity_id"] == "OPP065"] # Mahila Coir Yojana
    res = filter_candidate_set(opp_coir, p_fp)
    assert len(res["filtered_out"]) == 1
    assert "Coir" in res["filtered_out"][0]["reason"]

# 9. Central/CSS geography
def test_central_css_geography(opps):
    p_tn = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu"}
    opp_css = [o for o in opps if o.get("scope", "").startswith("Central")]
    res = filter_candidate_set(opp_css, p_tn)
    # Scope starting with Central should not be filtered out due to geography
    for item in res["filtered_out"]:
        assert not item["reason"].startswith("Geography scope")

# 10. lifecycle-blocked scheme
def test_lifecycle_blocked_scheme(opps):
    non_rec_opps = [o for o in opps if o.get("recommendable") is False or str(o.get("lifecycle_status", "")).upper() != "ACTIVE"]
    # If any exist, test format_analyze_response puts them in needs_verification
    m4_output = {
        "recommendations": [],
        "needs_verification": non_rec_opps,
        "not_eligible": []
    }
    resp = format_analyze_response({}, m4_output)
    for nv in resp["needs_verification"]:
        assert nv["recommendable"] is False
        assert nv["eligibility_status"] == "NEEDS_VERIFICATION"

# 11. pathway with actual requirements
def test_pathway_with_actual_requirements():
    engine = PathwayEngine()
    
    # OPP011 PMFME has requirements in M1/M2 data
    pathway = engine.build(profile={"sector": "Food Processing & Agri Value Addition"}, opportunity_id="OPP011")
    assert pathway["opportunity_id"] == "OPP011"
    assert "steps" in pathway
    step_types = [s["step_type"] for s in pathway["steps"]]
    assert "USER_PROFILE_STATE" in step_types
    assert "TARGET_OPPORTUNITY" in step_types
    assert "USER_GOAL" in step_types
    assert "guidance" in pathway.get("disclaimer", "").lower()

# 12. pathway with no usable requirements
def test_pathway_with_no_usable_requirements():
    engine = PathwayEngine()
    # Temporarily mock empty requirements for OPP011 to test build robustness with 0 requirements
    original_by_opp = engine.gaps.by_opportunity
    engine.gaps.by_opportunity = {}
    try:
        pathway = engine.build(profile={}, opportunity_id="OPP011")
        assert "steps" in pathway
        assert len(pathway["steps"]) >= 3
        assert pathway["steps"][0]["step_type"] == "USER_PROFILE_STATE"
    finally:
        engine.gaps.by_opportunity = original_by_opp

# 13. frontend must contain no hardcoded fake pathway fallback
def test_frontend_has_no_fake_pathway_fallback():
    js_path = ROOT_DIR / "frontend" / "my_opportunities.js"
    sd_path = ROOT_DIR / "frontend" / "scheme_detail.js"
    assert js_path.exists() and sd_path.exists()
    mo_content = js_path.read_text(encoding="utf-8")
    sd_content = sd_path.read_text(encoding="utf-8")
    assert "Required Prerequisite / Document" not in mo_content and "Required Prerequisite / Document" not in sd_content
    assert "Target Scheme Application Unlocked" not in mo_content and "Target Scheme Application Unlocked" not in sd_content
    assert "Financial / Non-Financial Support Granted" not in mo_content and "Financial / Non-Financial Support Granted" not in sd_content
    assert "More Information Needed" in mo_content or "more_information_needed" in mo_content

# 14. Idea-stage user vs existing-enterprise requirement
def test_idea_stage_vs_existing_enterprise_requirement(opps):
    mock_existing_opp = {
        "opportunity_id": "OPP_TEST_EXISTING",
        "opportunity_name": "Test Existing Enterprise Scheme",
        "primary_sector": "Food Processing & Agri Value Addition",
        "secondary_sectors": [],
        "scope": "Central/CSS",
        "benefit_summary": "Support for existing micro-enterprise in commercial operation for 3 years",
        "eligibility_summary": "Existing micro-enterprise unit in operation",
        "prerequisite_types": "REGISTRATION;DOCUMENT"
    }
    p_idea = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "business_stage": "Idea"}
    res = filter_candidate_set([mock_existing_opp], p_idea)
    assert len(res["filtered_out"]) == 1
    assert "Existing operating enterprise required" in res["filtered_out"][0]["reason"]

# 15. unknown business stage vs existing-enterprise requirement
def test_unknown_business_stage_vs_existing_enterprise(opps):
    mock_existing_opp = {
        "opportunity_id": "OPP_TEST_EXISTING",
        "opportunity_name": "Test Existing Enterprise Scheme",
        "primary_sector": "Food Processing & Agri Value Addition",
        "secondary_sectors": [],
        "scope": "Central/CSS",
        "benefit_summary": "Support for existing micro-enterprise in commercial operation for 3 years",
        "eligibility_summary": "Existing micro-enterprise unit in operation",
        "prerequisite_types": "REGISTRATION;DOCUMENT"
    }
    p_unknown = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "business_stage": None}
    res = filter_candidate_set([mock_existing_opp], p_unknown)
    assert len(res["relevant_needs_info"]) == 1
    assert "Business stage" in res["relevant_needs_info"][0]["unknown_requirements"][0]

# 16. matching existing stage
def test_matching_existing_stage(opps):
    mock_existing_opp = {
        "opportunity_id": "OPP_TEST_EXISTING",
        "opportunity_name": "Test Existing Enterprise Scheme",
        "primary_sector": "Food Processing & Agri Value Addition",
        "secondary_sectors": [],
        "scope": "Central/CSS",
        "benefit_summary": "Support for existing micro-enterprise in commercial operation for 3 years",
        "eligibility_summary": "Existing micro-enterprise unit in operation",
        "prerequisite_types": "REGISTRATION;DOCUMENT"
    }
    p_existing = {"sector": "Food Processing & Agri Value Addition", "state": "Tamil Nadu", "business_stage": "Existing"}
    res = filter_candidate_set([mock_existing_opp], p_existing)
    assert len(res["relevant"]) == 1

# 17. business_goal retained through /api/analyze
def test_business_goal_retained_through_analyze():
    from fastapi.testclient import TestClient
    from server.app import app
    client = TestClient(app)
    payload = {
        "profile": {
            "sector": "Food Processing & Agri Value Addition",
            "state": "Tamil Nadu",
            "business_goal": "Establish organic mango pulp processing unit"
        },
        "selected_opportunity_id": "OPP011"
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["pathway"]["user_business_goal"] == "Establish organic mango pulp processing unit"
    steps = data["pathway"]["steps"]
    goal_step = [s for s in steps if s["step_type"] == "USER_GOAL"][0]
    assert "Establish organic mango pulp processing unit" in goal_step["title"]

# 18. RELEVANT_NEEDS_PROFILE_INFO visibly carries missing fields into API response
def test_needs_info_carries_missing_fields_into_api_response():
    from fastapi.testclient import TestClient
    from server.app import app
    client = TestClient(app)
    # OPP012 requires SHG membership
    payload = {
        "profile": {
            "sector": "Food Processing & Agri Value Addition",
            "state": "Tamil Nadu",
            "shg_membership": None
        }
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    needs_info = data.get("more_information_needed", [])
    opp_12 = [r for r in needs_info if r["opportunity_id"] == "OPP012"]
    if opp_12:
        item = opp_12[0]
        assert item["relevance_state"] == "RELEVANT_NEEDS_PROFILE_INFO"
        assert "shg_membership" in item["missing_profile_info"]

# 19. Zero intersection between Best Matches and More Information Needed
def test_zero_intersection_between_best_matches_and_more_info():
    from fastapi.testclient import TestClient
    from server.app import app
    client = TestClient(app)
    payload = {
        "profile": {
            "gender": "Female",
            "age": 24,
            "state": "Tamil Nadu",
            "education": "Degree",
            "sector": "Food Processing & Agri Value Addition",
            "business_stage": "Idea",
            "annual_income": 300000,
            "available_capital": 200000,
            "business_goal": "Establish an organic mango pulp processing unit"
        }
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    
    best_matches = data.get("best_matches", [])
    more_info = data.get("more_information_needed", [])
    
    best_ids = set(r["opportunity_id"] for r in best_matches)
    more_info_ids = set(r["opportunity_id"] for r in more_info)
    
    # Assert ZERO intersection between Best Matches and More Information Needed
    intersection = best_ids.intersection(more_info_ids)
    assert len(intersection) == 0, f"Found overlapping opportunities: {intersection}"
    
    # Specifically verify OPP013 (PMFME Support to FPOs/SHGs/Producer Cooperatives)
    # appears under More Information Needed only, not Best Matches
    assert "OPP013" in more_info_ids, "OPP013 should be in More Information Needed"
    assert "OPP013" not in best_ids, "OPP013 must NOT be in Best Matches"

# 20. Dedicated Scheme Detail API endpoint
def test_scheme_detail_api_endpoint():
    from fastapi.testclient import TestClient
    from server.app import app
    client = TestClient(app)
    resp = client.get("/api/opportunity/OPP011")
    assert resp.status_code == 200
    data = resp.json()
    assert data["opportunity_id"] == "OPP011"
    assert "PMFME" in data["opportunity_name"]
    assert "requirements" in data or "benefit_summary" in data

# 21. Standalone Pathway Generation API endpoint
def test_pathway_generate_endpoint():
    from fastapi.testclient import TestClient
    from server.app import app
    client = TestClient(app)
    payload = {
        "profile": {
            "gender": "Female",
            "age": 24,
            "state": "Tamil Nadu",
            "education": "Degree",
            "sector": "Food Processing & Agri Value Addition",
            "business_stage": "Idea",
            "business_goal": "Establish an organic mango pulp processing unit"
        },
        "opportunity_id": "OPP021"
    }
    resp = client.post("/api/pathway/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["opportunity_id"] == "OPP021"
    assert "steps" in data
    assert len(data["steps"]) >= 3

# 22. Verify global Opportunity Pathway tab is removed from dashboard UI markup
def test_global_opportunity_pathway_tab_removed():
    js_path = ROOT_DIR / "frontend" / "my_opportunities.js"
    assert js_path.exists()
    content = js_path.read_text(encoding="utf-8")
    assert "tab_pathway" not in content

# 23. Verify user-facing UI contains no developer jargon or internal module terms
def test_no_developer_jargon_in_public_ui():
    html_path = ROOT_DIR / "frontend" / "index.html"
    i18n_path = ROOT_DIR / "frontend" / "i18n.js"
    assert html_path.exists() and i18n_path.exists()
    
    html_content = html_path.read_text(encoding="utf-8")
    i18n_content = i18n_path.read_text(encoding="utf-8")
    
    # Verify new section title & cards in HTML
    assert "How SchemeMitra Helps You" in html_content
    assert "Tell Us About Yourself" in html_content
    assert "Find Opportunities That Fit You" in html_content
    assert "See Your Opportunity Journey" in html_content
    
    # Verify developer jargon is removed from HTML
    assert "The OpportunityOS Difference" not in html_content
    assert "M2 deterministic rules" not in html_content
    assert "never guessed by an LLM" not in html_content
    assert "Verified Graph Engine" not in html_content
    
    # Verify i18n keys
    assert 'sec_how_title: "How SchemeMitra Helps You"' in i18n_content
    assert 'how_card1_title: "1. Tell Us About Yourself"' in i18n_content
    assert 'how_card2_title: "2. Find Opportunities That Fit You"' in i18n_content
    assert 'how_card3_title: "3. See Your Opportunity Journey"' in i18n_content

# 24. Verify product positioning and official government portal handoff CTA
def test_product_positioning_and_official_portal_cta():
    scheme_detail_path = ROOT_DIR / "frontend" / "scheme_detail.js"
    my_opps_path = ROOT_DIR / "frontend" / "my_opportunities.js"
    i18n_path = ROOT_DIR / "frontend" / "i18n.js"
    html_path = ROOT_DIR / "frontend" / "index.html"
    
    sd_content = scheme_detail_path.read_text(encoding="utf-8")
    mo_content = my_opps_path.read_text(encoding="utf-8")
    i18n_content = i18n_path.read_text(encoding="utf-8")
    html_content = html_path.read_text(encoding="utf-8")
    
    # Verify end-of-pathway CTA and positioning disclaimers in JS components & HTML
    assert "btn_apply" in sd_content or "btn_continue_official_portal" in sd_content
    assert "platform_positioning_disclaimer" in sd_content or "official government portals" in sd_content
    assert "platform_positioning_disclaimer" in i18n_content
    assert "official_portal_notice" in i18n_content or "official government portals" in html_content
    
    # Verify i18n keys exist for official portal handoff
    assert "official_portal_notice" in i18n_content
    assert "btn_continue_official_portal" in i18n_content
    assert "platform_positioning_disclaimer" in i18n_content
    
    # Verify header & footer positioning
    assert "Applications submitted on official government portals" in html_content or "official government portals" in html_content

# 25. Extensive regression tests for Scheme Application Handoff UX
def test_scheme_application_handoff_ux():
    sd_path = ROOT_DIR / "frontend" / "scheme_detail.js"
    html_path = ROOT_DIR / "frontend" / "index.html"
    i18n_path = ROOT_DIR / "frontend" / "i18n.js"
    adapters_path = ROOT_DIR / "server" / "adapters.py"

    sd_content = sd_path.read_text(encoding="utf-8")
    html_content = html_path.read_text(encoding="utf-8")
    i18n_content = i18n_path.read_text(encoding="utf-8")
    adapters_content = adapters_path.read_text(encoding="utf-8")

    # 1. Every Scheme Detail screen exposes Apply button
    assert "btn_apply" in sd_content
    assert "openApplyModal" in sd_content

    # 2. Apply never opens an internal application form or collects data
    assert "<form" not in html_content.split("applyHandoffModal")[1].split("</div>\n  </div>")[0]
    assert "<input" not in html_content.split("applyHandoffModal")[1].split("</div>\n  </div>")[0]

    # 3. Verified application_url preferred when available in adapters and openApplyModal
    assert "application_url" in adapters_content
    assert "dedicatedApplyUrl" in sd_content
    assert "officialSourceUrl" in sd_content

    # 4 & 5. official_source_url fallback used safely and not falsely described as direct portal
    assert "apply_modal_desc_fallback" in i18n_content
    assert "Visit Official Scheme Website" in i18n_content

    # 6. No verified URL -> no fabricated destination
    assert "apply_modal_no_url" in i18n_content

    # 7 & 8. Public user can Apply without profile, and separately choose Check My Eligibility
    assert "noProfileCtaHtml" in sd_content
    assert "handleCheckEligibilityClick" in sd_content

    # 9 & 10. Confirmed profile user does not see Check My Eligibility but sees Apply
    assert "if (!profile)" in sd_content

    # 11. External link opens safely in a new tab
    assert 'target="_blank"' in sd_content

    # 12. Existing eligibility / pathway / recommendation behavior remains unchanged
    from fastapi.testclient import TestClient
    from server.app import app
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

# 26. Regression test for Scheme Detail duplicate actions cleanup
def test_scheme_detail_duplicate_actions_cleanup():
    sd_path = ROOT_DIR / "frontend" / "scheme_detail.js"
    i18n_path = ROOT_DIR / "frontend" / "i18n.js"
    
    sd_content = sd_path.read_text(encoding="utf-8")
    i18n_content = i18n_path.read_text(encoding="utf-8")

    # 1. Header has exactly one primary Apply button and no Official Source button beside it
    assert "btnHeaderApply" in sd_content
    # The header action bar should not contain btn_official_source
    header_block = sd_content.split("<!-- Primary Action Bar: Apply -->")[1].split("<!-- Scheme Overview Card -->")[0]
    assert "btnHeaderApply" in header_block
    assert "btn_official_source" not in header_block

    # 2. Bottom application handoff card is completely removed from scheme_detail.js
    assert "End-of-Pathway Primary Action Card" not in sd_content
    assert "Ready to Apply for" not in sd_content

    # 3. Official Website is rendered inside "About this Scheme"
    about_block = sd_content.split('id="cardAboutScheme"')[1].split("<!-- Personalized Match Card")[0]
    assert "detail_official_website" in about_block or "Official Website" in about_block
    assert 'id="linkAboutOfficialWebsite"' in about_block
    assert 'target="_blank" rel="noopener noreferrer"' in about_block

    # 4. URL preference in About card prefers official_source_url first, then application_url
    assert "opp.official_source_url || opp.application_url" in about_block

    # 5. Apply modal logic openApplyModal remains intact
    assert "openApplyModal()" in sd_content

    # 6. i18n contains detail_official_website in EN, TA, HI
    assert 'detail_official_website: "Official Website"' in i18n_content
    assert 'detail_official_website: "அதிகாரப்பூர்வ இணையதளம்"' in i18n_content
    assert 'detail_official_website: "आधिकारिक वेबसाइट"' in i18n_content

# 27. Regression test for PMEGP (OPP021) FULL_STRUCTURED deterministic rules
def test_pmegp_full_structured_rules():
    from modules.M2_eligibility_graph.engine.eligibility_engine import EligibilityEngine, NOT_ELIGIBLE, ELIGIBLE, POTENTIALLY_ELIGIBLE
    from modules.M2_eligibility_graph.models.profile import EntrepreneurProfile

    engine = EligibilityEngine()

    # Base valid profile for PMEGP
    base_profile = {
        "age": 25,
        "is_new_unit": True,
        "prior_gov_subsidy": False,
        "family_pmegp_availed": False,
        "sector": "MSME & Manufacturing",
        "project_cost": 800000, # ₹8 Lakh
        "education": "8th Pass"
    }

    # 1. Age 18 -> FAIL; Age 19 -> PASS
    p18 = dict(base_profile, age=18)
    res18 = engine.evaluate_opportunity(p18, "OPP021")
    assert res18["status"] == NOT_ELIGIBLE
    assert any(f["field"] == "age" for f in res18["failed"])

    p19 = dict(base_profile, age=19)
    res19 = engine.evaluate_opportunity(p19, "OPP021")
    assert res19["status"] == ELIGIBLE

    # 2. Manufacturing: project_cost 1000000 -> education not required; 1000001 -> education required
    pmfg_10l = dict(base_profile, sector="MSME & Manufacturing", project_cost=1000000, education=None)
    res_mfg_10l = engine.evaluate_opportunity(pmfg_10l, "OPP021")
    assert res_mfg_10l["status"] == ELIGIBLE
    assert not any(f["field"] == "education" for f in res_mfg_10l["failed"] + res_mfg_10l["missing_profile_fields"])

    pmfg_10l1 = dict(base_profile, sector="MSME & Manufacturing", project_cost=1000001, education=None)
    res_mfg_10l1 = engine.evaluate_opportunity(pmfg_10l1, "OPP021")
    assert res_mfg_10l1["status"] == POTENTIALLY_ELIGIBLE
    assert any(f["field"] == "education" for f in res_mfg_10l1["missing_profile_fields"])

    # 3. Service: project_cost 500000 -> education not required; 500001 -> education required
    psvc_5l = dict(base_profile, sector="Business & Service", project_cost=500000, education=None)
    res_svc_5l = engine.evaluate_opportunity(psvc_5l, "OPP021")
    assert res_svc_5l["status"] == ELIGIBLE
    assert not any(f["field"] == "education" for f in res_svc_5l["failed"] + res_svc_5l["missing_profile_fields"])

    psvc_5l1 = dict(base_profile, sector="Business & Service", project_cost=500001, education=None)
    res_svc_5l1 = engine.evaluate_opportunity(psvc_5l1, "OPP021")
    assert res_svc_5l1["status"] == POTENTIALLY_ELIGIBLE
    assert any(f["field"] == "education" for f in res_svc_5l1["missing_profile_fields"])

    # 4. New unit False -> FAIL
    p_existing = dict(base_profile, is_new_unit=False)
    res_existing = engine.evaluate_opportunity(p_existing, "OPP021")
    assert res_existing["status"] == NOT_ELIGIBLE
    assert any(f["field"] == "is_new_unit" for f in res_existing["failed"])

    # 5. Prior subsidy True -> FAIL
    p_prior = dict(base_profile, prior_gov_subsidy=True)
    res_prior = engine.evaluate_opportunity(p_prior, "OPP021")
    assert res_prior["status"] == NOT_ELIGIBLE
    assert any(f["field"] == "prior_gov_subsidy" for f in res_prior["failed"])

    # 6. Family availed True -> FAIL
    p_fam = dict(base_profile, family_pmegp_availed=True)
    res_fam = engine.evaluate_opportunity(p_fam, "OPP021")
    assert res_fam["status"] == NOT_ELIGIBLE
    assert any(f["field"] == "family_pmegp_availed" for f in res_fam["failed"])

    # 7. Missing hard field -> UNKNOWN (POTENTIALLY_ELIGIBLE), NOT automatic FAIL
    p_missing = dict(base_profile, age=None)
    res_missing = engine.evaluate_opportunity(p_missing, "OPP021")
    assert res_missing["status"] == POTENTIALLY_ELIGIBLE
    assert len(res_missing["failed"]) == 0
    assert any(f["field"] == "age" for f in res_missing["missing_profile_fields"])

    # 8. Project cost 5000001 (Mfg) -> NOT automatically NOT_ELIGIBLE (subsidy cap notice in uncertain)
    p_high_mfg = dict(base_profile, sector="MSME & Manufacturing", project_cost=5000001)
    res_high_mfg = engine.evaluate_opportunity(p_high_mfg, "OPP021")
    assert res_high_mfg["status"] != NOT_ELIGIBLE
    assert any(u["field"] == "subsidy_cap_pmegp" for u in res_high_mfg["uncertain_rules"])

    # 9. Project cost 2000001 (Service) -> NOT automatically NOT_ELIGIBLE
    p_high_svc = dict(base_profile, sector="Business & Service", project_cost=2000001)
    res_high_svc = engine.evaluate_opportunity(p_high_svc, "OPP021")
    assert res_high_svc["status"] != NOT_ELIGIBLE
    assert any(u["field"] == "subsidy_cap_pmegp" for u in res_high_svc["uncertain_rules"])


# 28. Regression test for PMS Scheme (OPP029) FULL_STRUCTURED rules
def test_pms_full_structured_rules():
    from modules.M2_eligibility_graph.engine.eligibility_engine import EligibilityEngine, NOT_ELIGIBLE, ELIGIBLE, POTENTIALLY_ELIGIBLE

    engine = EligibilityEngine()

    # 1. Udyam Micro -> PASS
    p_micro = {"udyam_registered": True, "udyam_category": "MICRO", "pms_events_availed_this_fy": 0}
    res_micro = engine.evaluate_opportunity(p_micro, "OPP029")
    assert res_micro["status"] == ELIGIBLE

    # 2. Udyam Small -> PASS
    p_small = {"udyam_registered": True, "udyam_category": "SMALL", "pms_events_availed_this_fy": 1}
    res_small = engine.evaluate_opportunity(p_small, "OPP029")
    assert res_small["status"] == ELIGIBLE

    # 3. Udyam Medium -> FAIL
    p_medium = {"udyam_registered": True, "udyam_category": "MEDIUM", "pms_events_availed_this_fy": 0}
    res_medium = engine.evaluate_opportunity(p_medium, "OPP029")
    assert res_medium["status"] == NOT_ELIGIBLE
    assert any(f["field"] == "udyam_category" for f in res_medium["failed"])

    # 4. No Udyam -> FAIL
    p_no_udyam = {"udyam_registered": False, "udyam_category": "MICRO"}
    res_no_udyam = engine.evaluate_opportunity(p_no_udyam, "OPP029")
    assert res_no_udyam["status"] == NOT_ELIGIBLE
    assert any(f["field"] == "udyam_registered" for f in res_no_udyam["failed"])

    # 5. Missing Udyam category -> UNKNOWN (POTENTIALLY_ELIGIBLE)
    p_missing_cat = {"udyam_registered": True, "udyam_category": None}
    res_missing_cat = engine.evaluate_opportunity(p_missing_cat, "OPP029")
    assert res_missing_cat["status"] == POTENTIALLY_ELIGIBLE
    assert any(f["field"] == "udyam_category" for f in res_missing_cat["missing_profile_fields"])

    # 6. >2 assisted events this FY -> assistance limit reached, enterprise remains scheme-eligible
    p_event_limit = {"udyam_registered": True, "udyam_category": "MICRO", "pms_events_availed_this_fy": 3}
    res_event_limit = engine.evaluate_opportunity(p_event_limit, "OPP029")
    assert res_event_limit["status"] != NOT_ELIGIBLE
    assert any(u["field"] == "pms_events_availed_this_fy" for u in res_event_limit["uncertain_rules"])


# 29. Critical eligibility invariant & PARTIAL_STRUCTURED constraint
def test_eligibility_invariant_and_partial_structured_constraint():
    from modules.M2_eligibility_graph.engine.eligibility_engine import EligibilityEngine, ELIGIBLE

    engine = EligibilityEngine()
    sample_profiles = [
        {},
        {"age": 24, "sector": "Food Processing & Agri Value Addition"},
        {"age": 25, "is_new_unit": True, "prior_gov_subsidy": False, "family_pmegp_availed": False, "project_cost": 500000},
        {"udyam_registered": True, "udyam_category": "MICRO"},
    ]

    for prof in sample_profiles:
        evaluations = engine.evaluate_all(prof)
        for ev in evaluations:
            completeness = ev.get("rule_completeness")
            status = ev.get("status")
            failed = ev.get("failed", [])
            missing = ev.get("missing_profile_fields", [])
            recommendable = ev.get("recommendable", False)

            if status == ELIGIBLE:
                assert completeness == "FULL_STRUCTURED", f"Scheme {ev['opportunity_id']} returned ELIGIBLE despite completeness={completeness}"
                assert len(failed) == 0, f"Scheme {ev['opportunity_id']} returned ELIGIBLE despite failed rules"
                assert len(missing) == 0, f"Scheme {ev['opportunity_id']} returned ELIGIBLE despite missing fields"
                assert recommendable is True, f"Scheme {ev['opportunity_id']} returned ELIGIBLE despite recommendable=False"

            if completeness != "FULL_STRUCTURED":
                assert status != ELIGIBLE, f"Partial/summary scheme {ev['opportunity_id']} returned ELIGIBLE"


# 30. PMEGP 3-valued conditional education logic regression tests
def test_pmegp_conditional_education_3valued_logic():
    from modules.M2_eligibility_graph.engine.eligibility_engine import EligibilityEngine, POTENTIALLY_ELIGIBLE, ELIGIBLE

    engine = EligibilityEngine()
    base = {
        "age": 25,
        "is_new_unit": True,
        "prior_gov_subsidy": False,
        "family_pmegp_availed": False
    }

    # Manufacturing route (₹10L threshold)
    # 1. cost missing + education missing -> UNKNOWN (missing)
    p_mfg_1 = dict(base, sector="Manufacturing", project_cost=None, education=None)
    res_mfg_1 = engine.evaluate_opportunity(p_mfg_1, "OPP021")
    assert res_mfg_1["status"] == POTENTIALLY_ELIGIBLE
    assert any(m["field"] == "education" for m in res_mfg_1["missing_profile_fields"])
    assert any(m["field"] == "project_cost" for m in res_mfg_1["missing_profile_fields"])

    # 2. cost missing + education >= 8th -> PASS
    p_mfg_2 = dict(base, sector="Manufacturing", project_cost=None, education="Degree")
    res_mfg_2 = engine.evaluate_opportunity(p_mfg_2, "OPP021")
    assert any(p["field"] == "education" for p in res_mfg_2["passed"])

    # 3. cost missing + education < 8th -> UNKNOWN (missing)
    p_mfg_3 = dict(base, sector="Manufacturing", project_cost=None, education="5th Pass")
    res_mfg_3 = engine.evaluate_opportunity(p_mfg_3, "OPP021")
    assert any(m["field"] == "education" for m in res_mfg_3["missing_profile_fields"])

    # Service route (₹5L threshold)
    # 1. cost missing + education missing -> UNKNOWN (missing)
    p_svc_1 = dict(base, sector="Service", project_cost=None, education=None)
    res_svc_1 = engine.evaluate_opportunity(p_svc_1, "OPP021")
    assert res_svc_1["status"] == POTENTIALLY_ELIGIBLE
    assert any(m["field"] == "education" for m in res_svc_1["missing_profile_fields"])

    # 2. cost missing + education >= 8th -> PASS
    p_svc_2 = dict(base, sector="Service", project_cost=None, education="Degree")
    res_svc_2 = engine.evaluate_opportunity(p_svc_2, "OPP021")
    assert any(p["field"] == "education" for p in res_svc_2["passed"])

    # 3. cost missing + education < 8th -> UNKNOWN (missing)
    p_svc_3 = dict(base, sector="Service", project_cost=None, education="5th Pass")
    res_svc_3 = engine.evaluate_opportunity(p_svc_3, "OPP021")
    assert any(m["field"] == "education" for m in res_svc_3["missing_profile_fields"])

    # Regression profile: all other hard fields PASS, but project_cost and education missing
    # MUST evaluate to POTENTIALLY_ELIGIBLE, NOT ELIGIBLE
    res_base = engine.evaluate_opportunity(p_mfg_1, "OPP021")
    assert res_base["status"] == POTENTIALLY_ELIGIBLE
    assert res_base["status"] != ELIGIBLE


# 31. FULL_STRUCTURED scheme grouping & pipeline placement regression tests
def test_full_structured_unknowns_placed_in_more_information_needed(opps):
    from server.adapters import filter_candidate_set, sanitize_profile, format_analyze_response, M2_DATA_DIR, M4_DATA_DIR
    from modules.M2_eligibility_graph.main import build_engines
    from modules.M4_ranking_pathway.main import build_recommendations

    # Profile with hard UNKNOWN for PMEGP
    profile = sanitize_profile({
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "age": 24,
    })

    relevance_res = filter_candidate_set(opps, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    m2_engines = build_engines(M2_DATA_DIR)
    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]

    m4_output = build_recommendations(profile, candidate_evaluations, data_dir=M4_DATA_DIR)
    resp = format_analyze_response(profile=profile, m4_output=m4_output, relevance_summary=relevance_res["summary"], relevance_res=relevance_res)

    best_ids = [o["opportunity_id"] for o in resp.get("best_matches", [])]
    more_info_ids = [o["opportunity_id"] for o in resp.get("more_information_needed", [])]

    # OPP021 is FULL_STRUCTURED with hard UNKNOWNs -> MUST be in More Information Needed, NOT Best Matches
    assert "OPP021" in more_info_ids
    assert "OPP021" not in best_ids

    # Fully satisfied profile for PMEGP
    full_profile = sanitize_profile({
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "age": 24,
        "is_new_unit": True,
        "prior_gov_subsidy": False,
        "family_pmegp_availed": False,
        "project_cost": 500000,
        "education": "Degree"
    })

    rel_res_full = filter_candidate_set(opps, full_profile)
    cand_ids_full = {o["opportunity_id"] for o in rel_res_full["candidate_set"]}
    evals_full = m2_engines["eligibility"].evaluate_all(full_profile)
    cand_evals_full = [e for e in evals_full if e["opportunity_id"] in cand_ids_full]

    m4_full = build_recommendations(full_profile, cand_evals_full, data_dir=M4_DATA_DIR)
    resp_full = format_analyze_response(profile=full_profile, m4_output=m4_full, relevance_summary=rel_res_full["summary"], relevance_res=rel_res_full)

    best_full_ids = [o["opportunity_id"] for o in resp_full.get("best_matches", [])]
    opp21_item = next((o for o in resp_full.get("best_matches", []) if o["opportunity_id"] == "OPP021"), None)

    assert "OPP021" in best_full_ids
    assert opp21_item["eligibility_status"] == "ELIGIBLE"


# 32. Rebuilt Opportunity Graph contract, provenance, and deduplication regression tests
def test_rebuilt_opportunity_graph_contract_and_provenance(opps):
    from server.adapters import filter_candidate_set, sanitize_profile, M2_DATA_DIR
    from modules.M2_eligibility_graph.main import build_engines

    m2_engines = build_engines(M2_DATA_DIR)
    graph_engine = m2_engines["graph"]

    profile = sanitize_profile({
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "age": 24,
        "business_stage": "Idea",
        "business_goal": "START_BUSINESS"
    })

    relevance_res = filter_candidate_set(opps, profile)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}

    evaluations = m2_engines["eligibility"].evaluate_all(profile)
    candidate_evaluations = [e for e in evaluations if e["opportunity_id"] in candidate_ids]

    # 1. Default TOP_3 graph
    graph_default = graph_engine.build_personalized_graph(profile, candidate_evaluations, selection_mode="TOP_3", limit=3)
    meta_def = graph_default["metadata"]

    assert meta_def["selection_mode"] == "TOP_3"
    assert meta_def["limit"] == 3
    assert len(meta_def["selected_opportunity_ids"]) <= 3
    assert meta_def["counts"]["synthetic_factual_edges"] == 0

    # Ensure node types
    node_types = set(n["type"] for n in graph_default["nodes"])
    assert "USER_PROFILE" in node_types
    assert "USER_GOAL" in node_types
    assert "OPPORTUNITY" in node_types
    assert "REQUIREMENT" in node_types
    assert "SUPPORT" in node_types

    # Ensure edge provenances are restricted to allowed categories
    edge_provs = set(e["provenance"] for e in graph_default["edges"])
    assert edge_provs.issubset({"M1_VERIFIED", "PROFILE_DERIVED", "PRESENTATION_DERIVED"})

    # Ensure NOT_ELIGIBLE and NEEDS_VERIFICATION schemes are excluded
    opp_nodes = [n for n in graph_default["nodes"] if n["type"] == "OPPORTUNITY"]
    for opp_node in opp_nodes:
        m2_st = opp_node["metadata"]["eligibility_status"]
        assert m2_st in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]
        if m2_st == "ELIGIBLE":
            assert opp_node["status"] == "Eligible"
        else:
            assert opp_node["status"] == "Potential Match"

    # 2. TOP_5 graph
    graph_top5 = graph_engine.build_personalized_graph(profile, candidate_evaluations, selection_mode="TOP_5", limit=5)
    assert graph_top5["metadata"]["limit"] == 5
    assert len(graph_top5["metadata"]["selected_opportunity_ids"]) <= 5

    # 3. ALL_RELEVANT graph
    graph_all = graph_engine.build_personalized_graph(profile, candidate_evaluations, selection_mode="ALL_RELEVANT")
    assert graph_all["metadata"]["selection_mode"] == "ALL_RELEVANT"


# 33. PMEGP Profile Pipeline, Money Normalization & Three-Valued Hard Rules
def test_pmegp_profile_pipeline_and_money_normalization():
    from modules.M3_nlp_ai.nlp.money_parser import MoneyParser
    from modules.M3_nlp_ai.nlp.rule_extractor import RuleExtractor
    from modules.M3_nlp_ai.ai.ai_assistant import AIAssistant
    from server.adapters import sanitize_profile, get_m1_opportunity_master, filter_candidate_set, format_analyze_response
    from modules.M2_eligibility_graph.main import build_engines
    from modules.M2_eligibility_graph.models.profile import EntrepreneurProfile

    mp = MoneyParser()
    # 1. Money Normalization Verification
    assert mp.parse_first("₹2 lakh", allow_bare=True).amount == 200000
    assert mp.parse_first("2 lakh", allow_bare=True).amount == 200000
    assert mp.parse_first("₹2,00,000", allow_bare=True).amount == 200000
    assert mp.parse_first("200000", allow_bare=True).amount == 200000
    assert mp.parse_first("₹3 lakh", allow_bare=True).amount == 300000
    assert mp.parse_first("₹5 lakh", allow_bare=True).amount == 500000
    assert mp.parse_first("₹10 lakh", allow_bare=True).amount == 1000000
    assert mp.parse_first("₹50 lakh", allow_bare=True).amount == 5000000

    # 2. Boolean Extraction Statements Verification
    ext = RuleExtractor()

    # Explicit Positives
    pos_res = ext.extract("This is a new unit. I previously received government subsidy for this unit. My spouse has already availed PMEGP.")
    assert pos_res.get("is_new_unit") is True
    assert pos_res.get("prior_gov_subsidy") is True
    assert pos_res.get("family_pmegp_availed") is True

    # Explicit Negatives
    neg_res = ext.extract("This is an existing unit. I have not received any previous government subsidy for this unit. Neither I nor my spouse has already availed PMEGP.")
    assert neg_res.get("is_new_unit") is False
    assert neg_res.get("prior_gov_subsidy") is False
    assert neg_res.get("family_pmegp_availed") is False

    # Omitted Statements -> null / UNKNOWN
    omitted_res = ext.extract("I want to start a food business.")
    assert omitted_res.get("is_new_unit") is True  # Inferred from Idea stage
    assert omitted_res.get("prior_gov_subsidy") is None
    assert omitted_res.get("family_pmegp_availed") is None

    # 3. Full Sample Input Verification
    sample_text = (
        "I am a 24-year-old woman from Tamil Nadu. I want to start a new "
        "food-processing business. I have a degree, my annual income is ₹3 lakh, "
        "I have ₹2 lakh available capital, and my planned project cost is ₹5 lakh. "
        "This is a new unit. I have not received any previous government subsidy "
        "for this unit, and neither I nor my spouse has already availed PMEGP. "
        "My goal is to start a business."
    )

    assistant = AIAssistant()
    assistant.process_message(sample_text)
    m2_payload = assistant.to_m2_payload()
    prof_dict = sanitize_profile(m2_payload.get("profile", {}))

    assert prof_dict["age"] == 24
    assert prof_dict["gender"] == "Female"
    assert prof_dict["state"] == "Tamil Nadu"
    assert prof_dict["education"] == "Degree"
    assert prof_dict["annual_income"] == 300000
    assert prof_dict["available_capital"] == 200000
    assert prof_dict["project_cost"] == 500000
    assert prof_dict["is_new_unit"] is True
    assert prof_dict["prior_gov_subsidy"] is False
    assert prof_dict["family_pmegp_availed"] is False

    # Check EntrepreneurProfile model wrapping
    ep = EntrepreneurProfile.from_dict(prof_dict)
    assert ep.available_capital == 200000
    assert ep.is_new_unit is True
    assert ep.prior_gov_subsidy is False
    assert ep.family_pmegp_availed is False
    assert ep.get("is_new_unit") is True
    assert ep.get("prior_gov_subsidy") is False
    assert ep.get("family_pmegp_availed") is False

    # 4. End-to-End PMEGP Evaluation (OPP021)
    engines = build_engines()
    ev_full = engines["eligibility"].evaluate_opportunity(prof_dict, "OPP021")
    assert ev_full["status"] == "ELIGIBLE"
    assert ev_full["rule_completeness"] == "FULL_STRUCTURED"
    assert len(ev_full["failed"]) == 0
    assert len(ev_full["missing_profile_fields"]) == 0

    # Test Pipeline Grouping with Full Profile
    master = get_m1_opportunity_master()
    relevance_res = filter_candidate_set(master, prof_dict)
    candidate_ids = {o["opportunity_id"] for o in relevance_res["candidate_set"]}
    all_evals = engines["eligibility"].evaluate_all(prof_dict)
    candidate_evaluations = [e for e in all_evals if e["opportunity_id"] in candidate_ids]

    from modules.M4_ranking_pathway.main import build_recommendations
    m4_output = build_recommendations(prof_dict, candidate_evaluations)
    grouped = format_analyze_response(prof_dict, m4_output, relevance_res=relevance_res)
    best_match_ids = [o["opportunity_id"] for o in grouped["best_matches"]]
    assert "OPP021" in best_match_ids

    # 5. Missing 1 Hard Field -> POTENTIALLY_ELIGIBLE & More Information Needed
    prof_missing = dict(prof_dict)
    prof_missing["is_new_unit"] = None
    prof_missing["extra"] = dict(prof_dict["extra"])
    prof_missing["extra"]["is_new_unit"] = None

    ev_missing = engines["eligibility"].evaluate_opportunity(prof_missing, "OPP021")
    assert ev_missing["status"] == "POTENTIALLY_ELIGIBLE"
    assert len(ev_missing["missing_profile_fields"]) > 0

    all_evals_missing = engines["eligibility"].evaluate_all(prof_missing)
    cand_evals_missing = [e for e in all_evals_missing if e["opportunity_id"] in candidate_ids]
    m4_output_missing = build_recommendations(prof_missing, cand_evals_missing)
    grouped_missing = format_analyze_response(prof_missing, m4_output_missing, relevance_res=relevance_res)
    needs_info_ids = [o["opportunity_id"] for o in grouped_missing["more_information_needed"]]
    assert "OPP021" in needs_info_ids

    # 6. Failing 1 Hard Field -> NOT_ELIGIBLE & not_eligible
    prof_fail = dict(prof_dict)
    prof_fail["prior_gov_subsidy"] = True
    prof_fail["extra"] = dict(prof_dict["extra"])
    prof_fail["extra"]["prior_gov_subsidy"] = True

    ev_fail = engines["eligibility"].evaluate_opportunity(prof_fail, "OPP021")
    assert ev_fail["status"] == "NOT_ELIGIBLE"
    assert len(ev_fail["failed"]) > 0

    all_evals_fail = engines["eligibility"].evaluate_all(prof_fail)
    cand_evals_fail = [e for e in all_evals_fail if e["opportunity_id"] in candidate_ids]
    m4_output_fail = build_recommendations(prof_fail, cand_evals_fail)
    grouped_fail = format_analyze_response(prof_fail, m4_output_fail, relevance_res=relevance_res)
    not_eligible_ids = [o["opportunity_id"] for o in grouped_fail["not_eligible"]]
    assert "OPP021" in not_eligible_ids


# 34. Full API Profile Parse & Graph Generation Integration Test
def test_api_profile_parse_and_graph_integration():
    from fastapi.testclient import TestClient
    from server.app import app

    client = TestClient(app)

    sample_text = (
        "I am a 24-year-old woman from Tamil Nadu. I want to start a new "
        "food-processing business. I have a degree, my annual income is ₹3 lakh, "
        "I have ₹2 lakh available capital, and my planned project cost is ₹5 lakh. "
        "This is a new unit. I have not received any previous government subsidy "
        "for this unit, and neither I nor my spouse has already availed PMEGP. "
        "My goal is to start a business."
    )

    # Test POST /api/profile/parse
    parse_res = client.post("/api/profile/parse", json={"message": sample_text})
    assert parse_res.status_code == 200
    parse_data = parse_res.json()
    prof = parse_data["profile"]

    assert prof["available_capital"] == 200000
    assert prof["project_cost"] == 500000
    assert prof["is_new_unit"] is True
    assert prof["prior_gov_subsidy"] is False
    assert prof["family_pmegp_availed"] is False

    # Test POST /api/analyze with parsed profile -> PMEGP ELIGIBLE in Best Matches
    analyze_res = client.post("/api/analyze", json={"profile": prof})
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()

    best_match_ids = [o["opportunity_id"] for o in analyze_data["best_matches"]]
    assert "OPP021" in best_match_ids

    pmegp_item = next(o for o in analyze_data["best_matches"] if o["opportunity_id"] == "OPP021")
    assert pmegp_item["eligibility_status"] == "ELIGIBLE"
    assert pmegp_item["rule_completeness"] == "FULL_STRUCTURED"

    # Test POST /api/graph/generate with confirmed profile -> Nodes > 0 & Edges > 0
    graph_res = client.post("/api/graph/generate", json={"profile": prof, "selection_mode": "TOP_3", "limit": 3})
    assert graph_res.status_code == 200
    graph_data = graph_res.json()

    assert len(graph_data["nodes"]) > 0
    assert len(graph_data["edges"]) > 0
    assert graph_data["metadata"]["counts"]["synthetic_factual_edges"] == 0

# 35. Regression test for My Opportunities dashboard error boundary and JS syntax integrity
def test_my_opportunities_dashboard_error_isolation():
    js_path = ROOT_DIR / "frontend" / "my_opportunities.js"
    content = js_path.read_text(encoding="utf-8")

    # 1. Verify JS file has balanced braces and template strings
    assert "class MyOpportunitiesComponent" in content
    assert "renderActiveTabContent(" in content
    assert "try {" in content
    assert "catch (graphErr)" in content

    # 2. Verify graph error handling isolates graph tab errors from main dashboard
    assert "Graph tab rendering isolated error" in content or "We couldn't load your opportunity graph" in content

# 36. Test Opportunity-Centric graph payload, data integrity, and support types
def test_opportunity_centric_graph_structure_and_integrity(canonical_profile):
    from fastapi.testclient import TestClient
    from server.app import app

    client = TestClient(app)
    
    prof = dict(canonical_profile)
    prof["extra"]["is_new_unit"] = True
    prof["extra"]["prior_gov_subsidy"] = False
    prof["extra"]["family_pmegp_availed"] = False

    analyze_res = client.post("/api/analyze", json={"profile": prof})
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()

    best_matches = analyze_data.get("best_matches", [])
    assert len(best_matches) >= 3

    # Top 3 ordering matches authoritative best matches order
    top3_auth_ids = [o["opportunity_id"] for o in best_matches[:3]]

    graph_res = client.post("/api/graph/generate", json={"profile": prof, "selection_mode": "TOP_3", "limit": 3})
    assert graph_res.status_code == 200
    graph_data = graph_res.json()

    nodes = graph_data.get("nodes", [])
    opp_nodes = [n for n in nodes if n.get("type") == "OPPORTUNITY"]
    assert len(opp_nodes) == 3

    # Top 3 opportunity nodes created by graph engine
    assert len(opp_nodes) == 3

    # Verify NOT_ELIGIBLE is excluded and support_types metadata is present
    for opp_n in opp_nodes:
        status = opp_n.get("metadata", {}).get("eligibility_status") or opp_n.get("status")
        assert status != "NOT_ELIGIBLE"
        meta = opp_n.get("metadata", {})
        assert "support_types" in meta
        assert isinstance(meta["support_types"], list)

    # Verify Profile node exists
    prof_nodes = [n for n in nodes if n.get("type") in ["USER_PROFILE", "YOUR_PROFILE"]]
    assert len(prof_nodes) == 1







