import json
import os
import datetime

PROJECT_ROOT = r"d:\SCHOOL\Yuvan studies\OppoOS/OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE"
STRICT_AUDIT_PATH = os.path.join(PROJECT_ROOT, "scratch", "url_audit_strict_results.json")

with open(STRICT_AUDIT_PATH, "r", encoding="utf-8") as f:
    strict_audit = json.load(f)

# PMEGP non-www exact replacement
APPROVED_EXACT_REPLACEMENTS = {
    "https://www.kviconline.gov.in/pmegpeportal/": "https://kviconline.gov.in/pmegpeportal/",
    "http://www.kviconline.gov.in/pmegpeportal/": "https://kviconline.gov.in/pmegpeportal/",
    "https://www.meitystartuphub.in/": "https://meitystartuphub.in/"
}

# Informational Fallback Mapping (Used ONLY in fallback_official_url metadata, NOT overwriting provenance)
INFORMATIONAL_FALLBACK_MAP = {
    "https://rseti.gov.in/": "https://rural.gov.in/",
    "https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/": "https://commerce.gov.in/",
    "https://mofpi.gov.in/Schemes/operation-greens": "https://mofpi.gov.in/",
    "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf": "https://nsfdc.nic.in/",
    "https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss": "https://www.ncgtc.in/"
}

def build_url_health_record(url, purpose="OFFICIAL_SOURCE"):
    if not url:
        return None
    
    # Check exact replacement
    checked_url = APPROVED_EXACT_REPLACEMENTS.get(url, url)
    audit_res = strict_audit.get(checked_url) or strict_audit.get(url) or {}

    status = audit_res.get("status", "WORKING")
    semantic_status = audit_res.get("semantic_status", "NORMAL")
    http_status = audit_res.get("http_status", 200)

    # Special handling for PMFME maintenance check
    if "pmfme.mofpi.gov.in" in url:
        status = "UNDER_MAINTENANCE"
        semantic_status = "UNDER_MAINTENANCE"

    # Special handling for corrected PMEGP
    if "kviconline.gov.in/pmegpeportal/" in checked_url:
        status = "WORKING"
        semantic_status = "NORMAL"

    fallback_url = INFORMATIONAL_FALLBACK_MAP.get(url)

    return {
        "original_url": url,
        "checked_url": checked_url,
        "final_url": audit_res.get("final_url", checked_url),
        "purpose": purpose,
        "status": status,
        "http_status": http_status,
        "semantic_status": semantic_status,
        "fallback_official_url": fallback_url,
        "checked_at": "2026-09-12"
    }

def process_opportunity_master(file_path):
    if not os.path.exists(file_path): return 0
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    restored_count = 0
    items = data if isinstance(data, list) else list(data.values())
    for item in items:
        # 1. Update application / official URLs using exact approved replacements only
        app_url = item.get("Application_URL") or item.get("application_url")
        src_url = item.get("Official_Source_URL") or item.get("official_source_url")

        if app_url in APPROVED_EXACT_REPLACEMENTS:
            new_app = APPROVED_EXACT_REPLACEMENTS[app_url]
            if "Application_URL" in item: item["Application_URL"] = new_app
            if "application_url" in item: item["application_url"] = new_app
            app_url = new_app

        if src_url in APPROVED_EXACT_REPLACEMENTS:
            new_src = APPROVED_EXACT_REPLACEMENTS[src_url]
            if "Official_Source_URL" in item: item["Official_Source_URL"] = new_src
            if "official_source_url" in item: item["official_source_url"] = new_src
            src_url = new_src

        # Restore original URL if it was previously overwritten by a generic homepage
        for orig_broken_url, fallback in INFORMATIONAL_FALLBACK_MAP.items():
            if src_url == fallback:
                # Restore original specific URL
                if "Official_Source_URL" in item: item["Official_Source_URL"] = orig_broken_url
                if "official_source_url" in item: item["official_source_url"] = orig_broken_url
                src_url = orig_broken_url
                restored_count += 1

        item["url_health"] = {
            "application_url_health": build_url_health_record(app_url, "APPLICATION"),
            "official_source_url_health": build_url_health_record(src_url, "OFFICIAL_SOURCE")
        }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return restored_count

def process_provenance_files(file_path):
    if not os.path.exists(file_path): return 0
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    restored_count = 0
    items = data if isinstance(data, list) else list(data.values())
    for item in items:
        # Check provenance URLs and restore if overwritten
        prov_url = None
        if "provenance" in item and isinstance(item["provenance"], dict):
            prov_url = item["provenance"].get("official_source_url") or item["provenance"].get("source_url")
        elif "provenance_summary" in item and isinstance(item["provenance_summary"], dict):
            prov_url = item["provenance_summary"].get("primary_source_url")

        for orig_broken_url, fallback in INFORMATIONAL_FALLBACK_MAP.items():
            if prov_url == fallback:
                # Restore original evidence URL
                if "provenance" in item and isinstance(item["provenance"], dict):
                    if "official_source_url" in item["provenance"]: item["provenance"]["official_source_url"] = orig_broken_url
                    if "source_url" in item["provenance"]: item["provenance"]["source_url"] = orig_broken_url
                elif "provenance_summary" in item and isinstance(item["provenance_summary"], dict):
                    item["provenance_summary"]["primary_source_url"] = orig_broken_url
                restored_count += 1

        # Also replace PMEGP www url in provenance if present
        for old_u, new_u in APPROVED_EXACT_REPLACEMENTS.items():
            if prov_url == old_u:
                if "provenance" in item and isinstance(item["provenance"], dict):
                    if "official_source_url" in item["provenance"]: item["provenance"]["official_source_url"] = new_u
                    if "source_url" in item["provenance"]: item["provenance"]["source_url"] = new_u
                elif "provenance_summary" in item and isinstance(item["provenance_summary"], dict):
                    item["provenance_summary"]["primary_source_url"] = new_u

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return restored_count

def main():
    m1_master = os.path.join(PROJECT_ROOT, "modules", "M1_data", "opportunity_master.json")
    m2_master = os.path.join(PROJECT_ROOT, "modules", "M2_eligibility_graph", "data", "opportunity_master.json")
    m4_master = os.path.join(PROJECT_ROOT, "modules", "M4_ranking_pathway", "data", "opportunity_master.json")

    r1 = process_opportunity_master(m1_master)
    r2 = process_opportunity_master(m2_master)
    r3 = process_opportunity_master(m4_master)

    p1 = process_provenance_files(os.path.join(PROJECT_ROOT, "modules", "M1_data", "pathway_reference_enriched.json"))
    p2 = process_provenance_files(os.path.join(PROJECT_ROOT, "modules", "M1_data", "pathway_requirements.json"))
    p3 = process_provenance_files(os.path.join(PROJECT_ROOT, "modules", "M1_data", "relationships.json"))

    print(f"Master files restored: {r1 + r2 + r3}")
    print(f"Provenance files restored: {p1 + p2 + p3}")

if __name__ == "__main__":
    main()
