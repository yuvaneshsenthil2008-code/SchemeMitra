import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

sample_text = (
    "I am a 24-year-old woman from Tamil Nadu. I want to start a new "
    "food-processing business. I have a degree, my annual income is ₹3 lakh, "
    "I have ₹2 lakh available capital, and my planned project cost is ₹5 lakh. "
    "This is a new unit. I have not received any previous government subsidy "
    "for this unit, and neither I nor my spouse has already availed PMEGP. "
    "My goal is to start a business."
)

parse_res = client.post("/api/profile/parse", json={"message": sample_text})
prof = parse_res.json()["profile"]

analyze_res = client.post("/api/analyze", json={"profile": prof})
data = analyze_res.json()

best_matches = data.get("best_matches", [])
more_info = data.get("more_information_needed", [])
needs_verif = data.get("needs_verification", [])

print(f"/api/analyze Status: {analyze_res.status_code}")
print(f"Best Matches count: {len(best_matches)}")
print(f"More Info Needed count: {len(more_info)}")
print(f"Needs Verification count: {len(needs_verif)}")

pmegp = next((m for m in best_matches if m.get("opportunity_id") == "OPP021"), None)
if pmegp:
    print(f"OPP021 PMEGP in Best Matches: status={pmegp.get('eligibility_status')}, rule_completeness={pmegp.get('rule_completeness')}")
else:
    print("OPP021 PMEGP not in Best Matches")
