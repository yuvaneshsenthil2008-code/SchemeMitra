import sys
import json
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
    "business_goal": "START_BUSINESS",
    "category": None,
    "extra": {
        "is_new_unit": True,
        "prior_gov_subsidy": False,
        "family_pmegp_availed": False,
        "available_capital": 200000
    }
}

# 1. Check M2 evaluation directly first
from server.adapters import get_m1_opportunity_master
from modules.M2_eligibility_graph.main import build_engines

master = get_m1_opportunity_master()
m2_engines = build_engines()
all_evals = m2_engines["eligibility"].evaluate_all(prof)
m2_eval = next(e for e in all_evals if e["opportunity_id"] == "OPP021")

m2_status = m2_eval.get("eligibility_status")
sys.stdout.buffer.write(f"M2 STATUS FOR OPP021: {m2_status}\n".encode("utf-8"))

# 2. Make ONE real POST call to /api/pathway/copilot
req_data = {
    "opportunity_id": "OPP021",
    "language": "English",
    "profile": prof
}

req_bytes = json.dumps(req_data).encode("utf-8")
req = urllib.request.Request(
    url="http://127.0.0.1:8000/api/pathway/copilot",
    data=req_bytes,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=15) as resp:
    res_bytes = resp.read()
    res_json = json.loads(res_bytes.decode("utf-8"))

sys.stdout.buffer.write("=== REAL COPILOT RESPONSE ===\n".encode("utf-8"))
sys.stdout.buffer.write(json.dumps(res_json, indent=2).encode("utf-8"))
sys.stdout.buffer.write("\n".encode("utf-8"))
