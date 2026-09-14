import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
from server.adapters import get_m1_opportunity_master, load_json_file, M2_DATA_DIR

m2_rules = {r["Opportunity_ID"]: r for r in load_json_file(M2_DATA_DIR / "eligibility_rules.json")}
opps = {o["opportunity_id"]: o for o in get_m1_opportunity_master()}

target_ids = ["OPP011", "OPP012", "OPP013", "OPP034", "OPP041", "OPP042", "OPP044"]

for tid in target_ids:
    opp = opps.get(tid, {})
    m2 = m2_rules.get(tid, {})
    print(f"=== {tid}: {opp.get('opportunity_name')} ===")
    print("  Target Beneficiary:", opp.get("target_beneficiary"))
    print("  Eligibility Summary:", opp.get("eligibility_summary"))
    print("  Prerequisite Types:", opp.get("prerequisite_types"))
    print("  M2 Rule Fields:")
    for k, v in m2.items():
        if any(w in k.lower() for w in ["stage", "type", "entity", "business", "registration", "shg", "startup", "incubator", "existing"]):
            print(f"    {k}: {v}")
