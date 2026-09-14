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

def test_two_dpr_requirements_remain_separate_canonical_req_ids():
    # Verify M1 data pathway requirements maintain separate REQ IDs
    from server.adapters import get_m1_pathway_requirements
    reqs = get_m1_pathway_requirements()
    dpr_reqs = [r for r in reqs if r.get("requirement_type") == "DPR"]
    assert len(dpr_reqs) >= 2
    unique_ids = {r["requirement_node_id"] for r in dpr_reqs}
    assert len(unique_ids) == len(dpr_reqs)

def test_artifact_persistence_server_side():
    client_id = f"test_client_art_{uuid.uuid4()}"

    res = client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "DPR",
        "notes": "Sample DPR document"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["client_id"] == client_id
    assert data["artifact_type"] == "DPR"
    assert data["status"] == "AVAILABLE"

    # Verify via GET endpoint
    res_get = client.get(f"/api/pathway/artifacts?client_id={client_id}")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["count"] == 1
    assert get_data["artifacts"][0]["artifact_type"] == "DPR"

def test_marking_dpr_available_does_not_complete_either_requirement():
    client_id = f"test_client_{uuid.uuid4()}"

    # Mark DPR artifact available
    client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "DPR"
    })

    # Completed actions list must remain 0
    res_comp = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_comp.json()["count"] == 0

    # Generate goal pathway
    res_gen = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    assert res_gen.status_code == 200
    pathway = res_gen.json()
    
    # Requirement completion status overlay remains empty
    overlay = pathway.get("user_progress_overlay", {})
    completed_reqs = overlay.get("completed_requirements", [])
    assert len(completed_reqs) == 0

    # User artifacts array contains DPR
    artifacts = pathway.get("user_artifacts", [])
    assert any(a["artifact_type"] == "DPR" for a in artifacts)

def test_completing_pmegp_dpr_does_not_complete_operation_greens_dpr():
    client_id = f"test_client_indep_{uuid.uuid4()}"
    req_pmegp = "REQ0086"
    req_other = "REQ0088"

    # Mark REQ0086 completed
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_pmegp
    })

    # Check completed actions has only REQ0086
    res_comp = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    completed_actions = res_comp.json()["completed_actions"]
    comp_ids = {a["requirement_id"] for a in completed_actions}
    
    assert req_pmegp in comp_ids
    assert req_other not in comp_ids

def test_completing_both_works_independently():
    client_id = f"test_client_both_{uuid.uuid4()}"
    req_1 = "REQ0086"
    req_2 = "REQ0088"

    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_1
    })
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_2
    })

    res_comp = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    completed_actions = res_comp.json()["completed_actions"]
    comp_ids = {a["requirement_id"] for a in completed_actions}

    assert req_1 in comp_ids
    assert req_2 in comp_ids
    assert res_comp.json()["count"] == 2

def test_cross_client_artifact_isolation():
    client_a = f"test_client_art_A_{uuid.uuid4()}"
    client_b = f"test_client_art_B_{uuid.uuid4()}"

    client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_a,
        "artifact_type": "DPR"
    })

    res_a = client.get(f"/api/pathway/artifacts?client_id={client_a}")
    res_b = client.get(f"/api/pathway/artifacts?client_id={client_b}")

    assert res_a.json()["count"] == 1
    assert res_b.json()["count"] == 0

def test_prepared_documents_count_is_correct():
    client_id = f"test_client_count_{uuid.uuid4()}"

    client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "DPR"
    })
    client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "IDENTITY_PROOF"
    })

    res = client.get(f"/api/pathway/artifacts?client_id={client_id}")
    assert res.json()["count"] == 2

    # Remove one artifact
    client.post("/api/pathway/artifacts/remove", json={
        "client_id": client_id,
        "artifact_type": "DPR"
    })

    res_after = client.get(f"/api/pathway/artifacts?client_id={client_id}")
    assert res_after.json()["count"] == 1
    assert res_after.json()["artifacts"][0]["artifact_type"] == "IDENTITY_PROOF"

def test_completed_actions_count_unaffected_by_artifact_availability():
    client_id = f"test_client_unaffected_{uuid.uuid4()}"

    client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "DPR"
    })

    res_actions = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_actions.json()["count"] == 0

def test_m1_files_unchanged():
    from server.adapters import get_m1_opportunity_master, get_m1_pathway_requirements, get_m1_relationships
    assert len(get_m1_opportunity_master()) == 100
    assert len(get_m1_pathway_requirements()) == 371
    assert len(get_m1_relationships()) == 522
