"""Canonical document requirements stay; the separate reusable-artifact feature does not."""
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app
from server.adapters import get_m1_pathway_requirements

client = TestClient(app)

SAMPLE_PROFILE = {
    "age": 28,
    "gender": "Female",
    "state": "Tamil Nadu",
    "sector": "Food Processing & Agri Value Addition",
    "annual_income": 150000,
    "business_goal": "START_BUSINESS",
    "business_stage": "Idea",
}


def test_generic_and_specific_document_requirements_remain_in_m1():
    reqs = get_m1_pathway_requirements()
    types = {r.get("requirement_type") for r in reqs}
    assert "DOCUMENT" in types
    assert "DPR" in types
    assert "IDENTITY_PROOF" in types


def test_generic_document_requirements_remain_in_pathway_ledger():
    client_id = f"test_doc_client_{uuid.uuid4()}"
    res = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS",
    })
    assert res.status_code == 200
    sections = res.json().get("sections", [])
    sec_b = next(s for s in sections if "requirements" in s.get("section_id", ""))
    doc_steps = [s for s in sec_b.get("steps", []) if s.get("requirement_type") in {"DOCUMENT", "DOCUMENTATION"}]
    assert doc_steps
    assert all(s["node_id"].startswith("REQ") for s in doc_steps)


def test_goal_pathway_has_no_artifact_payload():
    res = client.post("/api/pathway/goal/generate", json={
        "client_id": f"test_no_art_{uuid.uuid4()}",
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS",
    })
    assert res.status_code == 200
    assert "user_artifacts" not in res.json()


def test_total_steps_still_represents_real_pathway_steps():
    res = client.post("/api/pathway/goal/generate", json={
        "client_id": f"test_total_steps_{uuid.uuid4()}",
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS",
    })
    assert res.status_code == 200
    pathway = res.json()
    summary = pathway.get("summary", {})
    assert summary.get("total_steps", 0) > 0
    assert summary["total_steps"] == sum(len(s.get("steps", [])) for s in pathway.get("sections", []))
