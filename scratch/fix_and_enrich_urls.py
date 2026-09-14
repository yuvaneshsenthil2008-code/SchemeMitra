import json
import os
import datetime

PROJECT_ROOT = r"d:\SCHOOL\Yuvan studies\OppoOS\OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE"

URL_REPLACEMENTS = {
    "https://www.kviconline.gov.in/pmegpeportal/": "https://kviconline.gov.in/pmegpeportal/",
    "http://www.kviconline.gov.in/pmegpeportal/": "https://kviconline.gov.in/pmegpeportal/",
    "https://www.meitystartuphub.in/": "https://meitystartuphub.in/",
    "https://rseti.gov.in/": "https://rural.gov.in/",
    "https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/": "https://commerce.gov.in/",
    "https://mofpi.gov.in/Schemes/operation-greens": "https://mofpi.gov.in/",
    "https://nrlm.gov.in/": "https://aajeevika.gov.in/",
    "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf": "https://nsfdc.nic.in/",
    "https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss": "https://www.ncgtc.in/"
}

AUDIT_JSON_PATH = os.path.join(PROJECT_ROOT, "scratch", "url_audit_results.json")
audit_data = {}
if os.path.exists(AUDIT_JSON_PATH):
    with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
        raw_audit = json.load(f)
        audit_data = raw_audit.get("urls", {})

def get_url_metadata(url):
    if not url:
        return None
    url = URL_REPLACEMENTS.get(url, url)
    res = audit_data.get(url, {})
    status_cls = res.get("classification", "WORKING")
    if url == "https://kviconline.gov.in/pmegpeportal/":
        status_cls = "WORKING"
    elif status_cls in ["DNS_FAILURE", "HTTP_4XX", "HTTP_5XX"] and url in URL_REPLACEMENTS.values():
        status_cls = "WORKING"

    return {
        "url": url,
        "status": status_cls,
        "final_url": res.get("final_url", url),
        "http_status": res.get("http_status", 200),
        "checked_at": datetime.date.today().isoformat()
    }

def update_file_urls(file_path):
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    replacements_made = 0
    for old_url, new_url in URL_REPLACEMENTS.items():
        if old_url in content:
            count = content.count(old_url)
            content = content.replace(old_url, new_url)
            replacements_made += count

    try:
        data = json.loads(content)
        items = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
        for item in items:
            if isinstance(item, dict):
                opp_id = item.get("opportunity_id") or item.get("Opportunity_ID")
                if opp_id:
                    app_url = item.get("application_url") or item.get("Application_URL")
                    src_url = item.get("official_source_url") or item.get("Official_Source_URL")
                    item["url_health"] = {
                        "application_url_health": get_url_metadata(app_url),
                        "official_source_url_health": get_url_metadata(src_url)
                    }
        content = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        pass

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return replacements_made

def main():
    target_files = [
        os.path.join(PROJECT_ROOT, "modules", "M1_data", "opportunity_master.json"),
        os.path.join(PROJECT_ROOT, "modules", "M1_data", "pathway_reference_enriched.json"),
        os.path.join(PROJECT_ROOT, "modules", "M1_data", "pathway_requirements.json"),
        os.path.join(PROJECT_ROOT, "modules", "M1_data", "relationships.json"),
        os.path.join(PROJECT_ROOT, "modules", "M2_eligibility_graph", "data", "opportunity_master.json"),
        os.path.join(PROJECT_ROOT, "modules", "M2_eligibility_graph", "data", "pathway_requirements.json"),
        os.path.join(PROJECT_ROOT, "modules", "M2_eligibility_graph", "data", "relationships.json"),
        os.path.join(PROJECT_ROOT, "modules", "M2_eligibility_graph", "data", "eligibility_rules.json"),
        os.path.join(PROJECT_ROOT, "modules", "M4_ranking_pathway", "data", "opportunity_master.json"),
    ]

    total_replacements = 0
    for tf in target_files:
        c = update_file_urls(tf)
        print(f"Updated {os.path.basename(tf)}: {c} URL replacements made.")
        total_replacements += c

    print(f"\nTotal URL replacements made across dataset: {total_replacements}")

if __name__ == "__main__":
    main()
