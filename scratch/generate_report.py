import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)
payload = {
    "profile": {
        "sector": "Food Processing & Agri Value Addition",
        "state": "Tamil Nadu",
        "gender": "Female",
        "age": 24,
        "annual_income": 300000,
        "available_capital": 200000,
        "business_stage": "Idea",
        "category": None,
        "extra": {
            "missing_registrations": ["UDYAM", "FSSAI"],
            "unregistered_business": True,
            "available_capital": 200000
        }
    },
    "selected_opportunity_id": "OPP011"
}

resp = client.post("/api/analyze", json=payload)
data = resp.json()

summary = data.get("summary", {})
rel_summary = summary.get("relevance", {})

print("=== CANONICAL PROFILE ANALYZE REPORT ===")
print("total public catalogue:", rel_summary.get("catalogue_count"))
print("relevant candidates:", rel_summary.get("relevant_count"))
print("relevant-needs-profile-info:", rel_summary.get("relevant_needs_info_count"))
print("filtered-out:", rel_summary.get("filtered_out_count"))
print("candidate set count:", rel_summary.get("candidate_set_count"))

recs = data.get("recommendations", [])
needs = data.get("needs_verification", [])
not_elig = data.get("not_eligible", [])

m2_counts = {
    "ELIGIBLE": len([r for r in recs if r["eligibility_status"] == "ELIGIBLE"]),
    "POTENTIALLY_ELIGIBLE": len([r for r in recs if r["eligibility_status"] == "POTENTIALLY_ELIGIBLE"]),
    "NEEDS_VERIFICATION": len(needs),
    "NOT_ELIGIBLE": len(not_elig)
}

print("\nM2 status distribution within the candidate set:", json.dumps(m2_counts))
print("recommendations count:", len(recs))
print("needs-verification count:", len(needs))

print("\n=== FIRST 10 RECOMMENDATION NAMES + REASONS ===")
for i, r in enumerate(recs[:10], 1):
    name = r.get("name") or r.get("opportunity_name")
    status_str = r.get("eligibility_status")
    reasons = r.get("why_match") or []
    missing = r.get("missing_requirements") or []
    print(f"{i}. {name} [{status_str}]")
    print(f"   Why Match: {reasons}")
    if missing:
        print(f"   Missing Gaps: {missing}")

print("\n=== ONE FULL OPPORTUNITY PATHWAY JSON ===")
pathway = data.get("pathway")
if not pathway and recs and recs[0].get("opportunity_pathway"):
    pathway = recs[0]["opportunity_pathway"]
print(json.dumps(pathway, indent=2))
