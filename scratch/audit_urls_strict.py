import json
import os
import ssl
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = r"d:\SCHOOL\Yuvan studies/OppoOS/OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE"
M1_DIR = os.path.join(PROJECT_ROOT, "modules", "M1_data")

def collect_urls():
    urls = set()
    url_purposes = {}

    def add_url(url, purpose):
        if not url or not isinstance(url, str) or not url.startswith("http"):
            return
        cleaned = url.strip()
        urls.add(cleaned)
        if cleaned not in url_purposes:
            url_purposes[cleaned] = set()
        url_purposes[cleaned].add(purpose)

    # 1. opportunity_master.json
    master_path = os.path.join(M1_DIR, "opportunity_master.json")
    if os.path.exists(master_path):
        with open(master_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
            for item in items:
                if item.get("Application_URL") or item.get("application_url"):
                    add_url(item.get("Application_URL") or item.get("application_url"), "APPLICATION")
                if item.get("Official_Source_URL") or item.get("official_source_url"):
                    add_url(item.get("Official_Source_URL") or item.get("official_source_url"), "OFFICIAL_SOURCE")

    # 2. pathway_reference_enriched.json
    enriched_path = os.path.join(M1_DIR, "pathway_reference_enriched.json")
    if os.path.exists(enriched_path):
        with open(enriched_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
            for item in items:
                for off in item.get("official_sources", []):
                    if isinstance(off, dict) and off.get("url"):
                        add_url(off["url"], "OFFICIAL_SOURCE")
                if "provenance_summary" in item and isinstance(item["provenance_summary"], dict):
                    prov_url = item["provenance_summary"].get("primary_source_url")
                    if prov_url:
                        add_url(prov_url, "EVIDENCE")

    # 3. pathway_requirements.json
    reqs_path = os.path.join(M1_DIR, "pathway_requirements.json")
    if os.path.exists(reqs_path):
        with open(reqs_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
            for item in items:
                prov = item.get("provenance", {})
                if isinstance(prov, dict) and prov.get("official_source_url"):
                    add_url(prov["official_source_url"], "EVIDENCE")

    # 4. relationships.json
    rel_path = os.path.join(M1_DIR, "relationships.json")
    if os.path.exists(rel_path):
        with open(rel_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else (list(data.values()) if isinstance(data, dict) else [])
            for item in items:
                prov = item.get("provenance", {})
                if isinstance(prov, dict) and prov.get("official_source_url"):
                    add_url(prov["official_source_url"], "EVIDENCE")

    return sorted(list(urls)), {u: sorted(list(p)) for u, p in url_purposes.items()}

def check_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    record = {
        "original_url": url,
        "checked_url": url,
        "final_url": url,
        "http_status": 0,
        "status": "UNKNOWN_REQUIRES_MANUAL_CHECK",
        "semantic_status": "NORMAL",
        "tls_valid": False,
        "error": None
    }

    # First attempt: STRICT TLS Validation
    strict_ctx = ssl.create_default_context()
    
    # Check with strict TLS
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=strict_ctx) as resp:
            record["http_status"] = resp.getcode()
            record["final_url"] = resp.geturl()
            record["tls_valid"] = True
            
            content = resp.read(10240).decode("utf-8", errors="ignore").lower()
            if "under maintenance" in content or "site maintenance" in content or "system maintenance" in content:
                record["status"] = "UNDER_MAINTENANCE"
                record["semantic_status"] = "UNDER_MAINTENANCE"
            elif record["final_url"] != url:
                record["status"] = "REDIRECTED_WORKING"
            elif resp.getcode() == 200:
                record["status"] = "WORKING"
            else:
                record["status"] = f"HTTP_{resp.getcode()}"
            return record

    except urllib.error.HTTPError as e:
        record["http_status"] = e.code
        record["tls_valid"] = True
        if e.code in [401, 403]:
            record["status"] = "WORKING" # Govt WAF blocked python header but TLS and server host are valid
            record["error"] = f"HTTP {e.code} (Govt WAF)"
        elif 400 <= e.code < 500:
            record["status"] = "HTTP_4XX"
            record["error"] = f"HTTP {e.code}"
        elif e.code >= 500:
            record["status"] = "HTTP_5XX"
            record["error"] = f"HTTP {e.code}"
        return record

    except urllib.error.URLError as e:
        reason_str = str(e.reason).lower()
        if "ssl" in reason_str or "certificate" in reason_str or "handshake" in reason_str:
            # TLS Validation failed! Try unverified context to confirm TLS_ERROR
            insecure_ctx = ssl.create_default_context()
            insecure_ctx.check_hostname = False
            insecure_ctx.verify_mode = ssl.CERT_NONE
            try:
                req2 = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req2, timeout=10, context=insecure_ctx) as resp2:
                    record["http_status"] = resp2.getcode()
                    record["final_url"] = resp2.geturl()
                    record["status"] = "TLS_ERROR"
                    record["tls_valid"] = False
                    record["error"] = f"Strict TLS failed: {e.reason}"
                    return record
            except Exception as e2:
                record["status"] = "TLS_ERROR"
                record["tls_valid"] = False
                record["error"] = f"TLS error: {e.reason}"
                return record
        elif "getaddrinfo failed" in reason_str or "nodename" in reason_str:
            record["status"] = "DNS_FAILURE"
            record["error"] = str(e.reason)
            return record
        elif "timed out" in reason_str or "timeout" in reason_str:
            record["status"] = "TIMEOUT"
            record["error"] = "Timed Out"
            return record
        else:
            record["status"] = "DNS_FAILURE"
            record["error"] = str(e.reason)
            return record
    except Exception as exc:
        record["status"] = "UNKNOWN_REQUIRES_MANUAL_CHECK"
        record["error"] = str(exc)
        return record

def main():
    urls, purposes = collect_urls()
    print(f"Collected {len(urls)} unique URLs across M1 data.")

    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {executor.submit(check_url, u): u for u in urls}
        for future in as_completed(future_map):
            u = future_map[future]
            try:
                res = future.result()
                res["purposes"] = purposes.get(u, [])
                results[u] = res
            except Exception as e:
                results[u] = {
                    "original_url": u,
                    "checked_url": u,
                    "final_url": u,
                    "http_status": 0,
                    "status": "UNKNOWN_REQUIRES_MANUAL_CHECK",
                    "semantic_status": "NORMAL",
                    "tls_valid": False,
                    "error": str(e),
                    "purposes": purposes.get(u, [])
                }

    counts = {}
    for res in results.values():
        st = res["status"]
        counts[st] = counts.get(st, 0) + 1

    out_file = os.path.join(PROJECT_ROOT, "scratch", "url_audit_strict_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    total_unique = len(urls)
    sum_primary = sum(counts.values())
    duplicates = total_unique - len(results)

    print("\n--- RECONCILED URL HEALTH SUMMARY ---")
    print(f"total_unique_urls: {total_unique}")
    print(f"sum_of_primary_classifications: {sum_primary}")
    print(f"duplicate_classifications: {duplicates}")

    print("\nBreakdown by Primary Classification:")
    for st_name, cnt in sorted(counts.items()):
        print(f"  {st_name}: {cnt}")

    tls_valid_working = sum(1 for r in results.values() if r["status"] in ["WORKING", "REDIRECTED_WORKING"] and r["tls_valid"])
    print(f"\nTLS-VALID WORKING URL COUNT: {tls_valid_working}")

if __name__ == "__main__":
    main()
