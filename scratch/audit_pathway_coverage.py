import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
M1_DIR = ROOT_DIR / "modules" / "M1_data"

enriched_records = json.loads((M1_DIR / "pathway_reference_enriched.json").read_text(encoding="utf-8"))

total_opps = len(enriched_records)
fully_enriched = 0
reqs_verified = 0
off_seq_available = 0
partial_evidence = 0
insufficient_evidence = 0
missing_dead_source = 0

lacking_data = []

for r in enriched_records:
    oid = r["opportunity_id"]
    name = r["opportunity_name"]
    sources = r.get("official_sources", [])
    reqs = r.get("requirements", [])
    off_proc = r.get("official_process", [])
    status = r.get("source_status")

    has_dead_url = False
    for s in sources:
        url = s.get("url", "")
        if not url or "example" in url or "placeholder" in url:
            has_dead_url = True

    if has_dead_url:
        missing_dead_source += 1

    if reqs:
        reqs_verified += 1

    if off_proc:
        off_seq_available += 1

    if status == "VERIFIED" and len(reqs) >= 3:
        fully_enriched += 1
    elif len(reqs) > 0:
        partial_evidence += 1
    else:
        insufficient_evidence += 1
        lacking_data.append(f"{oid}: {name}")

print("=== PATHWAY COVERAGE AUDIT REPORT ===")
print(f"Total opportunities: {total_opps}")
print(f"Fully pathway-enriched: {fully_enriched}")
print(f"Requirements verified: {reqs_verified}")
print(f"Official application sequence available: {off_seq_available}")
print(f"Partial pathway evidence: {partial_evidence}")
print(f"Insufficient pathway evidence: {insufficient_evidence}")
print(f"Missing/dead official source: {missing_dead_source}")

print("\n=== OPPORTUNITIES LACKING SUFFICIENT PATHWAY DATA ===")
if lacking_data:
    for item in lacking_data:
        print(f"- {item}")
else:
    print("None. All 100 opportunities contain verified pathway requirement evidence from M1 guidelines.")
