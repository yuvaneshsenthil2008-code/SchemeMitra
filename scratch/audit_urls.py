import json
import os
import re
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

M1_DIR = r"d:\SCHOOL\Yuvan studies\OppoOS\OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE\modules\M1_data"

def collect_urls():
    urls = set()
    url_sources = {}
    
    def add_url(url, file_name, key_path):
        if not url or not isinstance(url, str) or not url.startswith("http"):
            return
        cleaned = url.strip()
        urls.add(cleaned)
        if cleaned not in url_sources:
            url_sources[cleaned] = []
        url_sources[cleaned].append(f"{file_name}:{key_path}")

    # 1. opportunity_master.json
    master_path = os.path.join(M1_DIR, "opportunity_master.json")
    if os.path.exists(master_path):
        with open(master_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for idx, item in enumerate(data if isinstance(data, list) else data.values()):
                opp_id = item.get("opportunity_id", f"idx_{idx}")
                for key in ["official_source_url", "application_url", "url", "portal_url", "source_url"]:
                    if key in item and item[key]:
                        add_url(item[key], "opportunity_master.json", f"{opp_id}.{key}")

    # 2. pathway_reference_enriched.json
    enriched_path = os.path.join(M1_DIR, "pathway_reference_enriched.json")
    if os.path.exists(enriched_path):
        with open(enriched_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (data.values() if isinstance(data, dict) else [])
            for idx, item in enumerate(items):
                opp_id = item.get("opportunity_id", f"idx_{idx}")
                for key in ["official_source_url", "application_url", "url", "official_website"]:
                    if key in item and item[key]:
                        add_url(item[key], "pathway_reference_enriched.json", f"{opp_id}.{key}")
                if "provenance" in item and isinstance(item["provenance"], dict):
                    for pkey in ["official_source_url", "source_url"]:
                        if pkey in item["provenance"] and item["provenance"][pkey]:
                            add_url(item["provenance"][pkey], "pathway_reference_enriched.json", f"{opp_id}.provenance.{pkey}")

    # 3. pathway_requirements.json
    reqs_path = os.path.join(M1_DIR, "pathway_requirements.json")
    if os.path.exists(reqs_path):
        with open(reqs_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (data.values() if isinstance(data, dict) else [])
            for idx, item in enumerate(items):
                req_id = item.get("req_id", f"idx_{idx}")
                for key in ["official_source_url", "url", "source_url"]:
                    if key in item and item[key]:
                        add_url(item[key], "pathway_requirements.json", f"{req_id}.{key}")

    # 4. relationships.json
    rel_path = os.path.join(M1_DIR, "relationships.json")
    if os.path.exists(rel_path):
        with open(rel_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (data.values() if isinstance(data, dict) else [])
            for idx, item in enumerate(items):
                rel_id = item.get("relationship_id", f"idx_{idx}")
                for key in ["official_source_url", "url", "source_url"]:
                    if key in item and item[key]:
                        add_url(item[key], "relationships.json", f"{rel_id}.{key}")

    return sorted(list(urls)), url_sources

def check_single_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    result = {
        "original_url": url,
        "final_url": url,
        "http_status": 0,
        "classification": "UNKNOWN_REQUIRES_MANUAL_CHECK",
        "error": None
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            result["http_status"] = resp.getcode()
            result["final_url"] = resp.geturl()
            
            content = resp.read(10240).decode('utf-8', errors='ignore').lower()
            
            if "under maintenance" in content or "site maintenance" in content or "system maintenance" in content:
                result["classification"] = "UNDER_MAINTENANCE"
            elif result["final_url"] != url:
                result["classification"] = "REDIRECTED_WORKING"
            elif resp.getcode() == 200:
                result["classification"] = "WORKING"
            else:
                result["classification"] = f"HTTP_{resp.getcode()}"

    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        if e.code in [401, 403]:
            # Govt sites often 403 standard scripts, but host is UP and domain is real
            result["classification"] = "WORKING" # Govt firewall 403 on scraper header
            result["error"] = f"HTTP {e.code} (Govt WAF/Firewall)"
        elif e.code >= 400 and e.code < 500:
            result["classification"] = "HTTP_4XX"
            result["error"] = f"HTTP {e.code}"
        elif e.code >= 500:
            result["classification"] = "HTTP_5XX"
            result["error"] = f"HTTP {e.code}"
    except urllib.error.URLError as e:
        reason_str = str(e.reason).lower()
        if "getaddrinfo failed" in reason_str or "name or service not known" in reason_str or "nodename nor servname provided" in reason_str:
            result["classification"] = "DNS_FAILURE"
        elif "timed out" in reason_str or "timeout" in reason_str:
            result["classification"] = "TIMEOUT"
        elif "ssl" in reason_str or "certificate" in reason_str:
            result["classification"] = "TLS_ERROR"
        else:
            result["classification"] = "DNS_FAILURE"
        result["error"] = str(e.reason)
    except TimeoutError:
        result["classification"] = "TIMEOUT"
        result["error"] = "Connection Timed Out"
    except Exception as e:
        result["classification"] = "UNKNOWN_REQUIRES_MANUAL_CHECK"
        result["error"] = str(e)

    return result

def main():
    urls, sources = collect_urls()
    print(f"Collected {len(urls)} unique URLs across M1 data files.")
    
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_single_url, u): u for u in urls}
        for future in as_completed(future_to_url):
            u = future_to_url[future]
            try:
                res = future.result()
                results[u] = res
            except Exception as exc:
                results[u] = {
                    "original_url": u,
                    "final_url": u,
                    "http_status": 0,
                    "classification": "UNKNOWN_REQUIRES_MANUAL_CHECK",
                    "error": str(exc)
                }

    output_path = os.path.join(r"d:\SCHOOL\Yuvan studies\OppoOS\OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE\scratch", "url_audit_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"urls": results, "sources": sources}, f, indent=2)

    counts = {}
    for res in results.values():
        c = res["classification"]
        counts[c] = counts.get(c, 0) + 1

    print("\nURL Audit Summary:")
    for cls_name, cnt in sorted(counts.items()):
        print(f"  {cls_name}: {cnt}")

    # Specifically check PMEGP URL
    www_pmegp = "https://www.kviconline.gov.in/pmegpeportal/"
    non_www_pmegp = "https://kviconline.gov.in/pmegpeportal/"
    
    print("\nPMEGP URL Comparison:")
    print("  www.kviconline.gov.in:", results.get(www_pmegp))
    print("  kviconline.gov.in:", results.get(non_www_pmegp))

if __name__ == "__main__":
    main()
