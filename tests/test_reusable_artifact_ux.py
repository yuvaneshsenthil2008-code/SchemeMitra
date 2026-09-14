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

def test_shared_artifact_names_does_not_contain_technical_enums():
    for key, name in progress_db.SHARED_ARTIFACT_NAMES.items():
        assert not name.startswith("Mark ")
        assert "_" not in name or "KYC" in name or "DPR" in name

def test_reusable_artifacts_end_to_end():
    client_id = f"test_ux_{uuid.uuid4()}"

    # Mark DPR available
    r_dpr = client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "DPR"
    })
    assert r_dpr.status_code == 200

    # Mark IDENTITY_PROOF available
    r_id = client.post("/api/pathway/artifacts/mark-available", json={
        "client_id": client_id,
        "artifact_type": "IDENTITY_PROOF"
    })
    assert r_id.status_code == 200

    # Fetch user artifacts
    r_list = client.get(f"/api/pathway/artifacts?client_id={client_id}")
    assert r_list.status_code == 200
    artifacts = r_list.json()["artifacts"]
    types = [a["artifact_type"] for a in artifacts]

    assert "DPR" in types
    assert "IDENTITY_PROOF" in types
    assert "DOCUMENT" not in types
