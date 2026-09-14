import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
from server.adapters import get_m1_opportunity_master
from modules.M2_eligibility_graph.main import build_engines
from server.ai.pathway_copilot import build_trusted_context

ROOT_DIR = Path(__file__).resolve().parents[1]

# Canonical profile
prof = {
    "sector": "Food Processing & Agri Value Addition",
    "state": "Tamil Nadu",
    "gender": "Female",
    "age": 24,
    "annual_income": 300000,
    "available_capital": 200000,
    "project_cost": 500000,
    "business_stage": "Idea",
    "category": None,
    "extra": {
        "is_new_unit": True,
        "prior_gov_subsidy": False,
        "family_pmegp_availed": False,
        "available_capital": 200000
    }
}

master = get_m1_opportunity_master()
opp021 = next(x for x in master if x["Opportunity_ID"] == "OPP021")

print("=== M1 MASTER RECORD FOR OPP021 ===")
print(json.dumps(opp021, indent=2))

m2_engines = build_engines()

ctx = build_trusted_context(prof, "OPP021", master, m2_engines)
print("\n=== TRUSTED CONTEXT GENERATED FOR OPP021 ===")
print(json.dumps(ctx, indent=2))
