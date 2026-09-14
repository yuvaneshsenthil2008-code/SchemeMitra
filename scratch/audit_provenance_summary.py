import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
M1_DIR = ROOT_DIR / "modules" / "M1_data"

records = json.loads((M1_DIR / "pathway_reference_enriched.json").read_text(encoding="utf-8"))

total_opps = len(records)
audited_web_verified_opps = 0
m1_ground_truth_opps = 0

req_counts = {
    "OFFICIAL_SOURCE_VERIFIED": 0,
    "M1_VERIFIED_DATA": 0,
    "DERIVED_EXPLANATION": 0
}

audited_ids = ["OPP001", "OPP011", "OPP012", "OPP013", "OPP021", "OPP031", "OPP034", "OPP041", "OPP042", "OPP044", "OPP093"]

print("=== PROVENANCE CLASSIFICATION SUMMARY (100 SCHEMES) ===")
for r in records:
    audit_lvl = r.get("provenance_summary", {}).get("audit_level")
    if audit_lvl == "OFFICIAL_SOURCE_VERIFIED":
        audited_web_verified_opps += 1
    else:
        m1_ground_truth_opps += 1

    for req in r.get("requirements", []):
        origin = req.get("evidence_origin", "M1_VERIFIED_DATA")
        req_counts[origin] = req_counts.get(origin, 0) + 1

print(f"Total Opportunities: {total_opps}")
print(f"Independently Web-Reverified Schemes (OFFICIAL_SOURCE_VERIFIED): {audited_web_verified_opps}")
print(f"M1-Backed Ground Truth Schemes (M1_VERIFIED_DATA): {m1_ground_truth_opps}")
print("\nRequirement Evidence Breakdown:")
for k, v in req_counts.items():
    print(f"  - {k}: {v}")

print("\n=== DEEP AUDIT OF 11 TARGETED SCHEMES ===")
for tid in audited_ids:
    r = [rec for rec in records if rec["opportunity_id"] == tid][0]
    meta = r.get("provenance_summary", {})
    print(f"\nScheme ID: {tid} - {r['opportunity_name']}")
    print(f"  Audit Level: {meta.get('audit_level')}")
    print(f"  Official Guideline Document: {meta.get('document_title')}")
    print(f"  Section: {meta.get('section')}")
    print(f"  Benefit Claim Verified: {meta.get('benefit_claim_checked')}")
    print(f"  Source Supports Claim: {meta.get('source_supports_claim')}")
    print(f"  Requirements ({len(r['requirements'])}):")
    for req in r['requirements']:
        print(f"    • [{req['evidence_origin']}] {req['type']}: {req['label']}")
        print(f"      Source: {req['source_document_title']} | {req['source_section']}")

print("\n=== SPECIFIC DEEP VERIFICATION OF OPP011 (PMFME INDIVIDUAL) ===")
opp11 = [rec for rec in records if rec["opportunity_id"] == "OPP011"][0]

print("OPP011 Requirements Verification:")
for req in opp11["requirements"]:
    print(f"  • Requirement [{req['type']}]: '{req['label']}'")
    print(f"    Origin: {req['evidence_origin']}")
    print(f"    Document: {req['source_document_title']}")
    print(f"    Section: {req['source_section']}")
    print(f"    URL: {req['source_url']}")
    print(f"    Supports Claim: {req['source_supports_claim']}")

print("\nOPP011 Subsidy & Benefit Verification:")
meta11 = opp11["provenance_summary"]
print(f"  • Claim: '{meta11['benefit_claim_checked']}'")
print(f"    Document: {meta11['document_title']} | {meta11['section']}")
print(f"    Supports Claim: {meta11['source_supports_claim']}")

print("\nOPP011 Official Process Steps Verification:")
for proc in opp11["official_process"]:
    print(f"  Step {proc['sequence']}: '{proc['label']}'")
    print(f"    Origin: {proc['evidence_origin']} | Document: {proc['source_document_title']}")
    print(f"    URL: {proc['source_url']} | Supports Claim: {proc['source_supports_claim']}")
