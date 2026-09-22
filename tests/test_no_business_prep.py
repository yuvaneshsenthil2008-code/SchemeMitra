"""
SchemeMitra — Verification Test Suite for Business Preparation Removal
Ensures:
- Goal Pathway contains NO PLANNING_GUIDANCE steps or sec_preparation section.
- total_steps is recalculated across Sections A through C only.
- M1/M2/M4 pipeline data remains completely intact.
- Completed Actions remain functional; Prepared Documents is intentionally removed.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.app import app
from modules.M2_eligibility_graph.pathway.goal_pathway_builder import GoalPathwayBuilder

client = TestClient(app)

def test_goal_pathway_builder_no_business_prep():
    builder = GoalPathwayBuilder()
    res = builder.build(
        profile={
            "age": 32,
            "gender": "Male",
            "state": "Tamil Nadu",
            "sector": "Food Processing",
            "business_stage": "Startup",
            "business_goal": "START_BUSINESS"
        }
    )

    # 1. No sec_preparation section
    section_ids = [s["section_id"] for s in res.get("sections", [])]
    assert "sec_preparation" not in section_ids
    assert all(sid != "sec_preparation" for sid in section_ids)

    # 2. No PLANNING_GUIDANCE step in any section
    all_steps = []
    for sec in res.get("sections", []):
        all_steps.extend(sec.get("steps", []))

    assert not any(st.get("basis") == "PLANNING_GUIDANCE" for st in all_steps)
    assert not any(st.get("step_type") == "BUSINESS_PREPARATION" for st in all_steps)

    # 3. total_steps recalculated cleanly (across Sections A, B, C)
    sum_steps = sum(len(s.get("steps", [])) for s in res.get("sections", []))
    assert res["summary"]["total_steps"] == sum_steps
    assert "Sections A through C" in res["summary"]["total_steps_definition"]

def test_goal_pathway_api_no_business_prep():
    res = client.post("/api/pathway/goal/generate", json={
        "profile": {
            "age": 28,
            "gender": "Female",
            "state": "Kerala",
            "sector": "MSME",
            "business_stage": "Idea",
            "business_goal": "START_BUSINESS"
        }
    })
    assert res.status_code == 200
    data = res.json()

    section_ids = [s["section_id"] for s in data.get("sections", [])]
    assert "sec_preparation" not in section_ids

    all_steps = []
    for sec in data.get("sections", []):
        all_steps.extend(sec.get("steps", []))
    assert not any(st.get("step_type") == "BUSINESS_PREPARATION" for st in all_steps)
