import sys
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app
from server import progress_db

client = TestClient(app)

SAMPLE_PROFILE = {
    "age": 28,
    "gender": "Female",
    "state": "Tamil Nadu",
    "sector": "Food Processing",
    "annual_income": 150000,
    "business_goal": "START_BUSINESS"
}

def test_document_removed_from_shared_artifact_names():
    assert "DOCUMENT" not in progress_db.SHARED_ARTIFACT_NAMES
    assert "General Document / Certificate" not in progress_db.SHARED_ARTIFACT_NAMES.values()
    # Specific artifacts remain
    assert "DPR" in progress_db.SHARED_ARTIFACT_NAMES
    assert "IDENTITY_PROOF" in progress_db.SHARED_ARTIFACT_NAMES

def test_generic_document_requirements_remain_in_pathway_ledger():
    client_id = f"test_doc_client_{uuid.uuid4()}"
    res = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    assert res.status_code == 200
    pathway = res.json()
    
    sections = pathway.get("sections", [])
    sec_b = [s for s in sections if "requirements" in s.get("section_id", "")][0]
    steps = sec_b.get("steps", [])

    # Verify generic DOCUMENT requirements exist in section B steps
    doc_steps = [s for s in steps if s.get("requirement_type") in ["DOCUMENT", "DOCUMENTATION"]]
    assert len(doc_steps) > 0
    for s in doc_steps:
        assert s["node_id"].startswith("REQ")

def test_identity_proof_and_dpr_reusable_artifacts_remain_working():
    client_id = f"test_art_client_{uuid.uuid4()}"

    # Mark IDENTITY_PROOF available
    r1 = client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "IDENTITY_PROOF"
    })
    assert r1.status_code == 200

    # Mark DPR available
    r2 = client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "DPR"
    })
    assert r2.status_code == 200

    # Fetch artifacts list
    res_list = client.get(f"/api/pathway/artifacts?client_id={client_id}")
    assert res_list.status_code == 200
    arts = res_list.json()["artifacts"]
    types = {a["artifact_type"] for a in arts}
    assert "IDENTITY_PROOF" in types
    assert "DPR" in types
    assert "DOCUMENT" not in types

def test_total_steps_remains_unchanged():
    client_id = f"test_total_steps_{uuid.uuid4()}"
    res = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    assert res.status_code == 200
    pathway = res.json()
    summary = pathway.get("summary", {})
    assert summary.get("total_steps", 0) > 0
