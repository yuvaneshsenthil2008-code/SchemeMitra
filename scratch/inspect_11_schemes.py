import json
from pathlib import Path

M1_DIR = Path("modules/M1_data")
opps = {o["Opportunity_ID"]: o for o in json.loads((M1_DIR / "opportunity_master.json").read_text(encoding="utf-8"))}
reqs = json.loads((M1_DIR / "pathway_requirements.json").read_text(encoding="utf-8"))

target_ids = ["OPP001", "OPP011", "OPP012", "OPP013", "OPP021", "OPP031", "OPP034", "OPP041", "OPP042", "OPP044", "OPP093"]

for tid in target_ids:
    opp = opps.get(tid, {})
    o_reqs = [r for r in reqs if r["opportunity_id"] == tid]
    print(f"=== {tid}: {opp.get('Opportunity_Name')} ===")
    print("  Official URL:", opp.get("Official_Source_URL"))
    print("  Benefit Summary:", opp.get("Benefit_Summary"))
    print("  Prerequisites:", opp.get("Prerequisite_Types"))
    print("  Requirements:", [f"{r['requirement_type']}: {r.get('action_label')}" for r in o_reqs])
