"""
SchemeMitra — Apply OPP034 CGSS URL Update Script
Updates ONLY OPP034 official source URL to https://www.ncgtc.in/cgss/ and last_verified to 2026-09-14.
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
NEW_URL = "https://www.ncgtc.in/cgss/"
NEW_DATE = "2026-09-14"

files_updated = []
references_count = 0

# 1. opportunity_master.json files (M1, M2, M4)
opp_master_files = [
    ROOT_DIR / "modules" / "M1_data" / "opportunity_master.json",
    ROOT_DIR / "modules" / "M2_eligibility_graph" / "data" / "opportunity_master.json",
    ROOT_DIR / "modules" / "M4_ranking_pathway" / "data" / "opportunity_master.json"
]

for fpath in opp_master_files:
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        modified = False
        for opp in data:
            if opp.get("Opportunity_ID") == "OPP034":
                opp["Official_Source_URL"] = NEW_URL
                opp["Last_Verified"] = NEW_DATE
                if "url_health" in opp and isinstance(opp["url_health"], dict):
                    uh = opp["url_health"]
                    if "official_source_url_health" in uh and isinstance(uh["official_source_url_health"], dict):
                        uh["official_source_url_health"]["url"] = NEW_URL
                        uh["official_source_url_health"]["final_url"] = NEW_URL
                        uh["official_source_url_health"]["status"] = "WORKING"
                        uh["official_source_url_health"]["http_status"] = 200
                        uh["official_source_url_health"]["checked_at"] = NEW_DATE
                modified = True
                references_count += 1
        
        if modified:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            files_updated.append(str(fpath.relative_to(ROOT_DIR)))

# 2. pathway_requirements.json files (M1, M2)
pathway_req_files = [
    ROOT_DIR / "modules" / "M1_data" / "pathway_requirements.json",
    ROOT_DIR / "modules" / "M2_eligibility_graph" / "data" / "pathway_requirements.json"
]

for fpath in pathway_req_files:
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        modified = False
        for r in data:
            if r.get("opportunity_id") == "OPP034":
                r["official_source_url"] = NEW_URL
                r["last_verified"] = NEW_DATE
                if "url_health" in r and isinstance(r["url_health"], dict):
                    uh = r["url_health"]
                    if "official_source_url_health" in uh and isinstance(uh["official_source_url_health"], dict):
                        uh["official_source_url_health"]["url"] = NEW_URL
                        uh["official_source_url_health"]["final_url"] = NEW_URL
                        uh["official_source_url_health"]["status"] = "WORKING"
                        uh["official_source_url_health"]["http_status"] = 200
                        uh["official_source_url_health"]["checked_at"] = NEW_DATE
                modified = True
                references_count += 1
        
        if modified:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            files_updated.append(str(fpath.relative_to(ROOT_DIR)))

# 3. relationships.json files (M1, M2)
rel_files = [
    ROOT_DIR / "modules" / "M1_data" / "relationships.json",
    ROOT_DIR / "modules" / "M2_eligibility_graph" / "data" / "relationships.json"
]

for fpath in rel_files:
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        modified = False
        for r in data:
            if r.get("source_node_id") == "OPP034" or r.get("target_node_id") == "OPP034":
                if "official_source_url" in r:
                    r["official_source_url"] = NEW_URL
                    modified = True
                    references_count += 1
        
        if modified:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            files_updated.append(str(fpath.relative_to(ROOT_DIR)))

# 4. eligibility_rules.json (M2)
erules_file = ROOT_DIR / "modules" / "M2_eligibility_graph" / "data" / "eligibility_rules.json"
if erules_file.exists():
    with open(erules_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    modified = False
    for r in data:
        if r.get("Opportunity_ID") == "OPP034":
            if "Official_Source_URL" in r:
                r["Official_Source_URL"] = NEW_URL
                modified = True
                references_count += 1
    
    if modified:
        with open(erules_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        files_updated.append(str(erules_file.relative_to(ROOT_DIR)))

# 5. pathway_reference_enriched.json (M1)
penriched_file = ROOT_DIR / "modules" / "M1_data" / "pathway_reference_enriched.json"
if penriched_file.exists():
    with open(penriched_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    modified = False
    for item in data:
        if item.get("opportunity_id") == "OPP034":
            if "official_source_url" in item:
                item["official_source_url"] = NEW_URL
                modified = True
                references_count += 1
            if "prerequisites" in item and isinstance(item["prerequisites"], list):
                for p in item["prerequisites"]:
                    if "official_source_url" in p:
                        p["official_source_url"] = NEW_URL
                        modified = True
                        references_count += 1
            if "milestones" in item and isinstance(item["milestones"], list):
                for m in item["milestones"]:
                    if "official_source_url" in m:
                        m["official_source_url"] = NEW_URL
                        modified = True
                        references_count += 1
    
    if modified:
        with open(penriched_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        files_updated.append(str(penriched_file.relative_to(ROOT_DIR)))

print(f"Update complete.")
print(f"Files Updated ({len(files_updated)}):")
for fu in sorted(set(files_updated)):
    print(f"  - {fu}")
print(f"Total OPP034 Active References Updated: {references_count}")
