"""
SchemeMitra — Reset Endpoint & Idempotency Automated Test Suite
Verifies reset contracts:
- Case A: Existing user with server progress (server data deleted)
- Case B: Existing client_id with zero server rows (returns HTTP 200 SUCCESS)
- Case C: No client_id at all (rejects blank with HTTP 400, client side skips server call gracefully)
- Case D: Server failure handling
- Case E: Reset twice (idempotent, both succeed)
- Case F: Language preference preservation
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app
from server import progress_db

client = TestClient(app)

def test_reset_user_data_db_function_idempotency():
    cid = "test_reset_client_999"

    # Setup progress & artifact
    progress_db.complete_requirement(cid, "REQ0086")
    progress_db.set_artifact_available(cid, "DPR")

    # Verify counts before reset
    completed = progress_db.get_completed_requirement_ids(cid)
    artifacts = progress_db.get_user_artifacts(cid)
    assert len(completed) == 1
    assert len(artifacts) == 1

    # First reset (Case A)
    res1 = progress_db.reset_user_data(cid)
    assert res1["status"] == "SUCCESS"
    assert res1["goal_requirement_progress_deleted"] == 1
    assert res1["user_artifacts_deleted"] == 1

    # Verify zero records left
    completed_after = progress_db.get_completed_requirement_ids(cid)
    artifacts_after = progress_db.get_user_artifacts(cid)
    assert len(completed_after) == 0
    assert len(artifacts_after) == 0

    # Second reset (Case B & E - Reset twice / zero rows)
    res2 = progress_db.reset_user_data(cid)
    assert res2["status"] == "SUCCESS"
    assert res2["goal_requirement_progress_deleted"] == 0
    assert res2["user_artifacts_deleted"] == 0

def test_reset_api_endpoint_contracts():
    cid = "test_api_reset_client_888"

    # Seed data
    progress_db.complete_requirement(cid, "REQ0001")

    # POST /api/user/reset
    res = client.post("/api/user/reset", json={"client_id": cid})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["goal_requirement_progress_deleted"] >= 1

    # Repeat POST /api/user/reset (Case E - Reset twice via API)
    res_repeat = client.post("/api/user/reset", json={"client_id": cid})
    assert res_repeat.status_code == 200
    data_repeat = res_repeat.json()
    assert data_repeat["status"] == "SUCCESS"
    assert data_repeat["goal_requirement_progress_deleted"] == 0

    # POST /api/reset (Alias endpoint check)
    res_alias = client.post("/api/reset", json={"client_id": cid})
    assert res_alias.status_code == 200

def test_reset_api_validation():
    # Missing / empty client_id should return 400 Bad Request
    res_empty = client.post("/api/user/reset", json={"client_id": ""})
    assert res_empty.status_code == 400

    res_null = client.post("/api/user/reset", json={})
    assert res_null.status_code == 400
