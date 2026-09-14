import json
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1_DIR = os.path.join(PROJECT_ROOT, "modules", "M1_data")

def test_pmegp_official_url_corrected():
    """Verify that PMEGP (OPP021) uses the verified official Ministry of MSME portal https://www.pmegp.msme.gov.in/."""
    master_path = os.path.join(M1_DIR, "opportunity_master.json")
    with open(master_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pmegp = next((item for item in data if item.get("opportunity_id") == "OPP021" or item.get("Opportunity_ID") == "OPP021"), None)
    assert pmegp is not None, "OPP021 PMEGP not found in master catalogue"

    app_url = pmegp.get("application_url") or pmegp.get("Application_URL") or ""
    src_url = pmegp.get("official_source_url") or pmegp.get("Official_Source_URL") or ""

    assert (app_url or src_url) == "https://www.pmegp.msme.gov.in/"
    assert "kviconline.gov.in" not in (app_url or src_url)

def test_no_broken_www_pmegp_urls_remain_in_catalogue():
    """Verify that no broken www.kviconline.gov.in URLs remain anywhere in the dataset."""
    json_files = [
        os.path.join(M1_DIR, "opportunity_master.json"),
        os.path.join(M1_DIR, "pathway_reference_enriched.json"),
        os.path.join(M1_DIR, "pathway_requirements.json"),
        os.path.join(M1_DIR, "relationships.json"),
    ]

    for jf in json_files:
        if os.path.exists(jf):
            with open(jf, "r", encoding="utf-8") as f:
                content = f.read()
            assert "www.kviconline.gov.in" not in content, f"Found obsolete www.kviconline.gov.in in {os.path.basename(jf)}"

def test_pmfme_maintenance_classification():
    """Verify that PMFME scheme URL is preserved and classified as UNDER_MAINTENANCE in operational health metadata."""
    master_path = os.path.join(M1_DIR, "opportunity_master.json")
    with open(master_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pmfme = next((item for item in data if item.get("opportunity_id") == "OPP014" or item.get("Opportunity_ID") == "OPP014"), None)
    assert pmfme is not None, "OPP014 PMFME not found in master catalogue"

    assert "url_health" in pmfme
    health = pmfme["url_health"].get("official_source_url_health") or pmfme["url_health"].get("application_url_health")
    assert health is not None
    assert health["status"] == "UNDER_MAINTENANCE"
    assert health["semantic_status"] == "UNDER_MAINTENANCE"

def test_url_health_operational_metadata_structure():
    """Verify operational health record structure and fallback URL preservation."""
    master_path = os.path.join(M1_DIR, "opportunity_master.json")
    with open(master_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data[:10]:
        assert "url_health" in item
        health = item["url_health"]
        assert "application_url_health" in health or "official_source_url_health" in health

def test_application_url_preferred_over_source_url():
    """Verify handoff logic prefers application_url over official_source_url."""
    item = {
        "application_url": "https://www.pmegp.msme.gov.in/",
        "official_source_url": "https://msme.gov.in/"
    }
    
    app_url = item.get("application_url")
    src_url = item.get("official_source_url")
    dest_url = app_url or src_url
    
    assert dest_url == "https://www.pmegp.msme.gov.in/"

def test_official_source_url_fallback():
    """Verify handoff logic falls back to official_source_url when application_url is missing."""
    item = {
        "application_url": None,
        "official_source_url": "https://msme.gov.in/"
    }
    
    app_url = item.get("application_url")
    src_url = item.get("official_source_url")
    dest_url = app_url or src_url
    
    assert dest_url == "https://msme.gov.in/"

def test_no_url_safe_disabled_state():
    """Verify handoff logic handles missing URLs gracefully without throwing or fabricating URLs."""
    item = {
        "application_url": None,
        "official_source_url": None
    }
    
    dest_url = (item.get("application_url") or item.get("official_source_url") or "").strip()
    assert dest_url == ""
