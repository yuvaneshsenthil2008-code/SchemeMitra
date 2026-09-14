"""
Verification script for OPP034 CGSS URL update isolation.
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

json_files = [
    "modules/M1_data/opportunity_master.json",
    "modules/M2_eligibility_graph/data/opportunity_master.json",
    "modules/M4_ranking_pathway/data/opportunity_master.json",
    "modules/M1_data/pathway_requirements.json",
    "modules/M2_eligibility_graph/data/pathway_requirements.json",
    "modules/M1_data/relationships.json",
    "modules/M2_eligibility_graph/data/relationships.json"
]

import json

print("=== 1. VERIFYING OPP034 URL IN DATASETS ===")
for path in json_files:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "opportunity_master.json" in path:
        opp34 = next(o for o in data if o.get("Opportunity_ID") == "OPP034")
        print(f"[{path}] OPP034 URL: {opp34['Official_Source_URL']} | Verified: {opp34['Last_Verified']}")
        assert opp34["Official_Source_URL"] == "https://www.ncgtc.in/cgss/"
        assert opp34["Last_Verified"] == "2026-09-14"
    
    if "pathway_requirements.json" in path:
        req34 = [r for r in data if r.get("opportunity_id") == "OPP034"]
        print(f"[{path}] OPP034 Requirements ({len(req34)} items):")
        for r in req34:
            print(f"   Node: {r.get('requirement_node_id')} | URL: {r.get('official_source_url')} | Verified: {r.get('last_verified')}")
            assert r["official_source_url"] == "https://www.ncgtc.in/cgss/"
            assert r["last_verified"] == "2026-09-14"

print("\n=== 2. VERIFYING OPP067, OPP074, OPP075 UNCHANGED ===")
m1_master = "modules/M1_data/opportunity_master.json"
with open(m1_master, "r", encoding="utf-8") as f:
    master_data = json.load(f)

for check_id in ["OPP067", "OPP074", "OPP075"]:
    opp = next(o for o in master_data if o.get("Opportunity_ID") == check_id)
    print(f"[{check_id}] Name: {opp['Opportunity_Name'][:40]} | URL: {opp['Official_Source_URL']}")
    assert opp["Official_Source_URL"] == "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf"

print("\n=== 3. VERIFYING GOAL PATHWAY BUILDER FOR OPP034 ===")
from modules.M2_eligibility_graph.pathway.goal_pathway_builder import GoalPathwayBuilder

builder = GoalPathwayBuilder()
res = builder.build(
    profile={"age": 28, "gender": "Male", "business_stage": "Startup", "business_goal": "START_BUSINESS"},
    candidate_evaluations=[{"opportunity_id": "OPP034", "opportunity_name": "Credit Guarantee Scheme for Startups (CGSS)", "status": "NEEDS_VERIFICATION"}]
)

sec_a = next(s for s in res["sections"] if s.get("section_id") == "sec_matched_opportunities")
step034 = sec_a["steps"][0]
print(f"Goal Pathway Step OPP034 official_source_url: {step034['official_source_url']}")
assert step034["official_source_url"] == "https://www.ncgtc.in/cgss/"

print("\nALL ISOLATION AND GOAL PATHWAY VERIFICATIONS PASSED CLEANLY!")
