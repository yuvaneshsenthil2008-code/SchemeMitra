"""Regression tests for removal of the Prepared Documents/reusable-artifact feature.

Canonical document requirements remain intact and user progress is represented only
through requirement completion / Completed Actions.
"""
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app
from server.adapters import get_m1_opportunity_master, get_m1_pathway_requirements, get_m1_relationships

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


def test_canonical_document_requirements_remain_separate():
    reqs = get_m1_pathway_requirements()
    for req_type in ("DPR", "IDENTITY_PROOF", "DOCUMENT"):
        typed = [r for r in reqs if r.get("requirement_type") == req_type]
        assert typed, f"Expected canonical {req_type} requirements to remain"
        ids = [r["requirement_node_id"] for r in typed]
        assert len(ids) == len(set(ids))


def test_artifact_api_routes_are_removed():
    active = {(route.path, tuple(sorted(getattr(route, "methods", []) or []))) for route in app.routes}
    assert not any(path == "/api/pathway/artifacts" for path, _ in active)
    assert not any(path == "/api/pathway/artifacts/mark-available" for path, _ in active)
    assert not any(path == "/api/pathway/artifacts/remove" for path, _ in active)


def test_goal_pathway_no_longer_returns_user_artifacts():
    client_id = f"test_no_artifacts_{uuid.uuid4()}"
    res = client.post("/api/pathway/goal/generate", json={
        "client_id": client_id,
        "profile": SAMPLE_PROFILE,
        "business_goal": "START_BUSINESS",
    })
    assert res.status_code == 200
    assert "user_artifacts" not in res.json()


def test_requirement_completion_is_the_only_progress_model():
    client_id = f"test_req_progress_{uuid.uuid4()}"
    reqs = get_m1_pathway_requirements()
    req_id = next(r["requirement_node_id"] for r in reqs if r.get("requirement_type") in {"DPR", "IDENTITY_PROOF", "DOCUMENT"})

    complete = client.post("/api/pathway/goal/progress/complete", json={
        "client_id": client_id,
        "requirement_id": req_id,
    })
    assert complete.status_code == 200

    actions = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert actions.status_code == 200
    ids = {a["requirement_id"] for a in actions.json()["completed_actions"]}
    assert req_id in ids

    reopen = client.post("/api/pathway/goal/progress/reopen", json={
        "client_id": client_id,
        "requirement_id": req_id,
    })
    assert reopen.status_code == 200
    actions_after = client.get(f"/api/pathway/goal/completed-actions?client_id={client_id}")
    assert req_id not in {a["requirement_id"] for a in actions_after.json()["completed_actions"]}


def test_m1_files_unchanged():
    assert len(get_m1_opportunity_master()) == 102
    assert len(get_m1_pathway_requirements()) == 379
    assert len(get_m1_relationships()) == 534
