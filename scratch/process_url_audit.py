import json
import os

with open(r"d:\SCHOOL\Yuvan studies\OppoOS\OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE\scratch\url_audit_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

urls_data = data.get("urls", {})
sources_data = data.get("sources", {})

by_class = {}
for url, info in urls_data.items():
    cls = info["classification"]
    if cls not in by_class:
        by_class[cls] = []
    by_class[cls].append(info)

print(f"Total Unique URLs Checked: {len(urls_data)}")
for cls, items in sorted(by_class.items()):
    print(f"\n--- {cls} ({len(items)}) ---")
    for item in items[:10]:
        print(f"  URL: {item['original_url']} -> Final: {item['final_url']} (Status: {item['http_status']}, Error: {item['error']})")
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more")
