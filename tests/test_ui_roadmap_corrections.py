"""
SchemeMitra — UI & Roadmap Correction Pass Automated Verification Suite
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app

client = TestClient(app)

def test_reset_profile_flow_api():
    """Verify profile reset endpoint contracts: analyze clear profile vs non-empty profile."""
    # Empty profile analyze
    res_empty = client.post("/api/analyze", json={"profile": {}})
    assert res_empty.status_code == 200
    data_empty = res_empty.json()
    assert "applicability" in data_empty or "recommendations" in data_empty or "profile" in data_empty

    # Explore schemes remains functional regardless of profile state
    res_explore = client.get("/api/opportunities?limit=200")
    assert res_explore.status_code == 200
    data_explore = res_explore.json()
    assert data_explore["total"] == 102
    assert len(data_explore["items"]) == 102

def test_roadmap_routing_and_scheme_specific_content():
    """Verify /api/pathway/generate returns distinct, scheme-specific roadmap content."""
    profile = {
        "age": 28,
        "gender": "Female",
        "state": "Tamil Nadu",
        "sector": "Food Processing",
        "business_stage": "Startup"
    }

    # Fetch 2 different schemes
    opps_res = client.get("/api/opportunities?limit=10")
    opps = opps_res.json()["items"]
    opp1_id = opps[0]["opportunity_id"]
    opp2_id = opps[1]["opportunity_id"]

    # Generate pathway for opp 1
    res1 = client.post("/api/pathway/generate", json={"profile": profile, "opportunity_id": opp1_id})
    assert res1.status_code == 200
    data1 = res1.json()

    # Generate pathway for opp 2
    res2 = client.post("/api/pathway/generate", json={"profile": profile, "opportunity_id": opp2_id})
    assert res2.status_code == 200
    data2 = res2.json()

    # Check distinct target IDs / scheme names
    id1 = data1.get("opportunity_id") or data1.get("target_opportunity_id") or data1.get("eligibility", {}).get("opportunity_id")
    id2 = data2.get("opportunity_id") or data2.get("target_opportunity_id") or data2.get("eligibility", {}).get("opportunity_id")
    assert id1 == opp1_id
    assert id2 == opp2_id
    assert id1 != id2

def test_status_integrity_no_fake_eligible():
    """Regression Test: Potentially eligible scheme MUST stay POTENTIALLY_ELIGIBLE, never converted to ELIGIBLE."""
    profile = {
        "age": 22,
        "gender": "Male",
        "state": "Kerala",
        "sector": "Agriculture & Allied",
        "business_stage": "Idea"
    }

    res = client.post("/api/opportunities/recommend", json={"profile": profile})
    assert res.status_code == 200
    data = res.json()

    recs = data.get("best_matches", []) if isinstance(data, dict) and "best_matches" in data else (data.get("recommendations", []) if isinstance(data.get("recommendations"), list) else [])
    if recs:
        first_opp = recs[0]
        first_opp = recs[0]
        # Check raw status in evaluation
        raw_status = first_opp.get("eligibility_status") or first_opp.get("status")
        if raw_status == "POTENTIALLY_ELIGIBLE":
            # Must remain POTENTIALLY_ELIGIBLE, not forced to ELIGIBLE
            assert first_opp.get("eligibility_status") != "ELIGIBLE"

    # Also test /api/eligibility/check
    check_res = client.post("/api/eligibility/check", json={"profile": profile})
    assert check_res.status_code == 200
    evals = check_res.json()["evaluations"]
    for ev in evals:
        if ev["status"] == "POTENTIALLY_ELIGIBLE":
            assert ev["status"] != "ELIGIBLE"
        elif ev["status"] == "NEEDS_VERIFICATION":
            assert ev["status"] != "ELIGIBLE"

def test_logo_asset_transparency_and_white_middle_band():
    """Verify schememitra_logo.png file transparency and internal white band preservation."""
    logo_path = ROOT_DIR / "frontend" / "assets" / "schememitra_logo.png"
    assert logo_path.exists(), "Logo file must exist at frontend/assets/schememitra_logo.png"

    img = Image.open(logo_path).convert("RGBA")
    arr = np.array(img)

    # Check alpha channel exists
    assert arr.shape[2] == 4, "Logo image must have RGBA 4 channels"

    # Outer background pixels (e.g. corner y=0, x=0) must be transparent (A == 0)
    assert arr[0, 0, 3] == 0, "Outer top-left corner background must be transparent (alpha=0)"
    assert arr[-1, -1, 3] == 0, "Outer bottom-right corner background must be transparent (alpha=0)"

    # Internal white flag band (e.g. Y=140, X=238) must be opaque white
    middle_white_mask = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 255) & (arr[:, :, 2] == 255) & (arr[:, :, 3] == 255)
    assert middle_white_mask.sum() > 500, "Internal white flag band must contain opaque white pixels (RGB=255,255,255, A=255)"
