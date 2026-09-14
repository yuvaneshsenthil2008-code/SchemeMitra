import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.ai.gemini_provider import GeminiProvider, load_local_dotenv
from server.ai.pathway_copilot import build_trusted_context, validate_copilot_response
from server.adapters import get_m1_opportunity_master
from modules.M2_eligibility_graph.main import build_engines

load_local_dotenv()

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

master = get_m1_opportunity_master()
m2_engines = build_engines()
ctx = build_trusted_context(prof, "OPP021", master, m2_engines)

print("=== TRUSTED CONTEXT ELIGIBILITY STATUS ===")
print(ctx["eligibility"])

provider = GeminiProvider()
print("\n=== INVOKING GEMINI PROVIDER FOR OPP021 ===")
raw_out = provider.generate_copilot_explanation(ctx, language="English")

print("\n=== RAW GEMINI OUTPUT ===")
print(json.dumps(raw_out, indent=2))

if raw_out:
    val_out = validate_copilot_response(raw_out, ctx)
    print("\n=== VALIDATED GEMINI OUTPUT ===")
    print(json.dumps(val_out, indent=2))
