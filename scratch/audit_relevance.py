import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.adapters import filter_candidate_set, get_m1_opportunity_master, load_json_file, M2_DATA_DIR

opps = {o["opportunity_id"]: o for o in get_m1_opportunity_master()}
m2_rules = {r["Opportunity_ID"]: r for r in load_json_file(M2_DATA_DIR / "eligibility_rules.json")}

p_canon = {
    "sector": "Food Processing & Agri Value Addition",
    "state": "Tamil Nadu",
    "gender": "Female",
    "age": 24,
    "annual_income": 300000,
    "available_capital": 200000,
    "business_stage": "Idea",
    "category": None
}

target_ids = ["OPP011", "OPP012", "OPP013", "OPP034", "OPP041", "OPP042", "OPP044"]

print("=== SCHEME AUDIT TABLE ===")
for tid in target_ids:
    opp = opps[tid]
    m2 = m2_rules.get(tid, {})
    res = filter_candidate_set([opp], p_canon)
    
    rel_state = "FILTERED_OUT"
    reason = ""
    unknown_reqs = []
    
    if res["relevant"]:
        rel_state = "RELEVANT"
        reason = res["relevant"][0]["reason"]
    elif res["relevant_needs_info"]:
        rel_state = "RELEVANT_NEEDS_PROFILE_INFO"
        reason = res["relevant_needs_info"][0]["reason"]
        unknown_reqs = res["relevant_needs_info"][0].get("unknown_requirements", [])
    elif res["filtered_out"]:
        rel_state = "FILTERED_OUT"
        reason = res["filtered_out"][0]["reason"]

    print(f"\nScheme ID: {tid} - {opp['opportunity_name']}")
    print(f"  Required Stage/Entity Facts: {opp.get('prerequisite_types')} | {m2.get('Business_or_Entity_Rule')}")
    print(f"  Source Field/Rule: M1 Prerequisite_Types & M2 Business_or_Entity_Rule")
    print(f"  User Value: stage='{p_canon.get('business_stage')}', category={p_canon.get('category')}, shg={p_canon.get('shg_membership')}")
    print(f"  Missing/Known Status: unknown_reqs={unknown_reqs}")
    print(f"  Resulting Relevance State: {rel_state}")
