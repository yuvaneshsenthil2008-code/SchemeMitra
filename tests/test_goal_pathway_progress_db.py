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

def test_valid_requirement_completion_persists_to_db():
    client_id = f"test_client_{uuid.uuid4()}"
    req_id = "REQ0086"  # Valid canonical requirement ID from M1

    res = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_id
    })
    assert res.status_code == 200
    data = res.json()
    assert data["client_id"] == client_id
    assert data["requirement_id"] == req_id
    assert data["status"] == "COMPLETED"
    assert data["confirmed_by_user"] is True
    assert "completed_at" in data

    # Verify directly in DB
    completed_ids = progress_db.get_completed_requirement_ids(client_id)
    assert req_id in completed_ids

def test_invalid_req_id_rejected():
    client_id = f"test_client_{uuid.uuid4()}"
    invalid_req_id = "INVALID_REQ_9999"

    res = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": invalid_req_id
    })
    assert res.status_code == 400
    assert "Invalid requirement_id" in res.json()["detail"]

def test_completed_action_appears_in_completed_actions_endpoint():
    client_id = f"test_client_{uuid.uuid4()}"
    req_id = "REQ0086"

    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_id
    })

    res = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 1
    actions = data["completed_actions"]
    found = [a for a in actions if a["requirement_id"] == req_id]
    assert len(found) == 1
    item = found[0]
    assert item["status"] == "COMPLETED"
    assert item["basis"] == "CONFIRMED_USER_PROGRESS"
    assert "title" in item
    assert "source_opportunity_name" in item
    assert item["title"] != ""

def get_section(pathway: dict, section_id: str) -> dict:
    sections = pathway.get("sections", [])
    if isinstance(sections, list):
        for s in sections:
            if isinstance(s, dict) and (s.get("section_id") == section_id or section_id in s.get("section_id", "")):
                return s
    elif isinstance(sections, dict):
        return sections.get(section_id, {})
    return {}

def test_completed_requirement_excluded_from_next_actions():
    client_id = f"test_client_{uuid.uuid4()}"

    # First generate pathway to get a valid requirement from next actions
    res1 = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    assert res1.status_code == 200
    pathway1 = res1.json()
    
    # Locate next_actions list
    next_actions = pathway1.get("next_actions", [])
    assert len(next_actions) > 0
    target_req_id = next_actions[0]["node_id"]

    # Mark completed
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": target_req_id
    })

    # Regenerate pathway with same client_id
    res2 = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    pathway2 = res2.json()
    next_req_ids = [s["node_id"] for s in pathway2.get("next_actions", [])]

    assert target_req_id not in next_req_ids

def test_completed_requirement_remains_in_requirement_progress():
    client_id = f"test_client_{uuid.uuid4()}"

    res1 = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    pathway1 = res1.json()
    target_req_id = pathway1["next_actions"][0]["node_id"]

    # Mark completed
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": target_req_id
    })

    # Regenerate pathway
    res2 = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    pathway2 = res2.json()
    sec_b = get_section(pathway2, "sec_requirements")
    req_progress_steps = sec_b.get("steps", [])

    found = [s for s in req_progress_steps if s["node_id"] == target_req_id]
    assert len(found) == 1
    assert found[0]["status"] == "COMPLETED"
    assert found[0]["basis"] == "CONFIRMED_USER_PROGRESS"

def test_reopened_requirement_removed_from_completed_actions():
    client_id = f"test_client_{uuid.uuid4()}"
    req_id = "REQ0086"

    # Complete
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_id
    })

    # Reopen
    res_reopen = client.post("/api/pathway/goal/progress/reopen", json={
        "client_id": client_id,
        "requirement_id": req_id
    })
    assert res_reopen.status_code == 200

    # Verify completed actions list is empty
    res = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res.status_code == 200
    assert res.json()["count"] == 0

def test_reopen_restores_underlying_m2_state():
    client_id = f"test_client_{uuid.uuid4()}"

    res1 = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    pathway1 = res1.json()
    target_req = pathway1["next_actions"][0]
    target_req_id = target_req["node_id"]
    original_status = target_req["status"]

    # Mark complete
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": target_req_id
    })

    # Reopen
    client.post("/api/pathway/goal/progress/reopen", json={
        "client_id": client_id,
        "requirement_id": target_req_id
    })

    # Regenerate pathway
    res3 = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    pathway3 = res3.json()
    sec_b3 = get_section(pathway3, "sec_requirements")
    restored_req = [s for s in sec_b3.get("steps", []) if s["node_id"] == target_req_id][0]

    assert restored_req["status"] == original_status
    assert restored_req["status"] in ["ACTION_NEEDED", "NEEDS_CONFIRMATION"]

def test_cross_client_isolation():
    client_a = f"test_client_A_{uuid.uuid4()}"
    client_b = f"test_client_B_{uuid.uuid4()}"
    req_id = "REQ0086"

    # Client A completes
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_a,
        "requirement_id": req_id
    })

    # Client B should have 0 completed actions
    res_b = client.get(f"/api/pathway/goal/completed-actions?client_id={client_b}")
    assert res_b.json()["count"] == 0

    # Client A should have 1 completed action
    res_a = client.get(f"/api/pathway/goal/completed-actions?client_id={client_a}")
    assert res_a.json()["count"] == 1

def test_m1_json_files_remain_unchanged():
    from server.adapters import get_m1_opportunity_master, get_m1_pathway_requirements, get_m1_relationships
    
    master = get_m1_opportunity_master()
    reqs = get_m1_pathway_requirements()
    rels = get_m1_relationships()

    assert len(master) == 100
    assert len(reqs) == 371
    assert len(rels) == 522

def test_duplicate_complete_request_is_idempotent():
    client_id = f"test_client_{uuid.uuid4()}"
    req_id = "REQ0086"

    res1 = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_id
    })
    assert res1.status_code == 200

    res2 = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_id
    })
    assert res2.status_code == 200

    # Check count in DB is still 1
    res_list = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_list.json()["count"] == 1

def test_server_restart_persistence():
    client_id = f"test_client_restart_{uuid.uuid4()}"
    req_id = "REQ0086"

    # Save progress
    progress_db.complete_requirement(client_id, req_id)

    # Re-initialize DB connection to simulate restart
    progress_db.init_db()

    completed_ids = progress_db.get_completed_requirement_ids(client_id)
    assert req_id in completed_ids


def test_exact_pmegp_flow_requirement_8():
    client_id = f"test_pmegp_client_{uuid.uuid4()}"
    dpr_req = "REQ0088"      # PMEGP DPR requirement
    training_req = "REQ0090" # PMEGP Training requirement

    # First, generate initial pathway to get active requirement node IDs from pathway next_actions
    res_init = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    assert res_init.status_code == 200
    pathway_init = res_init.json()
    next_actions_init = pathway_init.get("next_actions", [])
    assert len(next_actions_init) >= 2

    active_req1 = next_actions_init[0]["node_id"]
    active_req2 = next_actions_init[1]["node_id"]

    # 1. Mark first active requirement completed
    r1 = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": active_req1
    })
    assert r1.status_code == 200

    # 2. Mark second active requirement completed
    r2 = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": active_req2
    })
    assert r2.status_code == 200

    # Also complete PMEGP canonical requirements REQ0088 and REQ0090
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": dpr_req
    })
    client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": training_req
    })

    # 3. Verify Completed Actions count button includes persisted records
    res_actions = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_actions.status_code == 200
    actions_data = res_actions.json()
    assert actions_data["count"] == 4
    completed_ids = [a["requirement_id"] for a in actions_data["completed_actions"]]
    assert active_req1 in completed_ids
    assert active_req2 in completed_ids
    assert dpr_req in completed_ids
    assert training_req in completed_ids

    # 4. Verify Goal Pathway generation shows active completed requirements as COMPLETED
    res_pathway = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    assert res_pathway.status_code == 200
    pathway = res_pathway.json()
    sec_b = get_section(pathway, "sec_requirements")
    req_steps = sec_b.get("steps", [])

    completed_in_pathway = [s for s in req_steps if s["node_id"] in [active_req1, active_req2] and s["status"] == "COMPLETED"]
    assert len(completed_in_pathway) == 2

    # 5. Refresh simulation (fetching completed actions & pathway again)
    res_refresh = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_refresh.json()["count"] == 4

    # 6. Restart server simulation (re-init DB schema & connection)
    progress_db.init_db()
    res_restart = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_restart.json()["count"] == 4

    # 7. Reopen active_req1 requirement
    res_reopen = client.post("/api/pathway/goal/progress/reopen", json={
        "client_id": client_id,
        "requirement_id": active_req1
    })
    assert res_reopen.status_code == 200

    # 8. Verify Completed Actions button count decreases to 3
    res_after_reopen = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_after_reopen.json()["count"] == 3

    # 9. Verify Goal Pathway generation shows 1 active Completed requirement remaining
    res_pathway_after = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS"
    })
    pathway_after = res_pathway_after.json()
    sec_b_after = get_section(pathway_after, "sec_requirements")
    req_steps_after = sec_b_after.get("steps", [])

    completed_after = [s for s in req_steps_after if s["node_id"] in [active_req1, active_req2] and s["status"] == "COMPLETED"]
    assert len(completed_after) == 1
    assert completed_after[0]["node_id"] == active_req2


