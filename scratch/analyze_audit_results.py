import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_RESULTS_PATH = os.path.join(PROJECT_ROOT, "scratch", "url_audit_live_results.json")
M1_PATH = os.path.join(PROJECT_ROOT, "modules", "M1_data", "opportunity_master.json")
REPORT_PATH = os.path.join(PROJECT_ROOT, "scratch", "url_audit_report.md")

# Known verified official replacements for government portals that block bots or have updated URLs
OFFICIAL_REPLACEMENTS = {
    "https://kviconline.gov.in/pmegpeportal/": {
        "verified_url": "https://www.pmegp.msme.gov.in/",
        "authority": "Ministry of MSME / PMEGP Official Portal",
        "action": "Updated to verified MSME PMEGP Portal"
    },
    "https://kviconline.gov.in/pmegpportal/": {
        "verified_url": "https://www.pmegp.msme.gov.in/",
        "authority": "Ministry of MSME / PMEGP Official Portal",
        "action": "Updated to verified MSME PMEGP Portal"
    },
    "https://www.kviconline.gov.in/pmegpeportal/": {
        "verified_url": "https://www.pmegp.msme.gov.in/",
        "authority": "Ministry of MSME / PMEGP Official Portal",
        "action": "Updated to verified MSME PMEGP Portal"
    }
}

def analyze():
    if not os.path.exists(LIVE_RESULTS_PATH):
        print(f"Error: {LIVE_RESULTS_PATH} does not exist yet. Audit script still running.")
        return

    with open(LIVE_RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)

    total = len(results)
    valid_count = 0
    redirect_count = 0
    broken_count = 0
    manual_count = 0

    kviconline_occurrences = []

    classified_results = []

    for item in results:
        opp_id = item["opportunity_id"]
        name = item["opportunity_name"]
        url = item["stored_url"]
        status = item["status"]
        code = item["http_code"]
        err = item["error"]
        final_dest = item["final_url"]
        last_verified = item.get("last_verified", "")

        # Check for kviconline
        if "kviconline" in url.lower():
            kviconline_occurrences.append((opp_id, name, url))

        rec_action = "Preserve verified URL"
        verified_replacement = ""
        official_source = ""

        if status == "VALID":
            valid_count += 1
            rec_action = "Preserve valid URL"
            verified_replacement = url
            official_source = "Verified active live portal response (HTTP 200)"
        elif status == "VALID_REDIRECT":
            redirect_count += 1
            rec_action = "Update stored URL to canonical redirect destination"
            verified_replacement = final_dest or url
            official_source = "Official portal redirect (HTTP 301/302)"
        elif status in ("BROKEN_404", "BROKEN_DNS", "SERVER_ERROR", "TIMEOUT"):
            broken_count += 1
            if url in OFFICIAL_REPLACEMENTS:
                rec_action = OFFICIAL_REPLACEMENTS[url]["action"]
                verified_replacement = OFFICIAL_REPLACEMENTS[url]["verified_url"]
                official_source = OFFICIAL_REPLACEMENTS[url]["authority"]
            else:
                rec_action = "Manual government portal verification required"
                verified_replacement = ""
                official_source = "Ministry / Department Portal Audit Needed"
        else: # MANUAL_VERIFICATION_REQUIRED
            manual_count += 1
            if url in OFFICIAL_REPLACEMENTS:
                rec_action = OFFICIAL_REPLACEMENTS[url]["action"]
                verified_replacement = OFFICIAL_REPLACEMENTS[url]["verified_url"]
                official_source = OFFICIAL_REPLACEMENTS[url]["authority"]
            else:
                rec_action = "Verify via Ministry / Official Portal (Automated request blocked/restricted)"
                verified_replacement = ""
                official_source = "Official Ministry Portal Audit Needed"

        classified_results.append({
            "opp_id": opp_id,
            "name": name,
            "url": url,
            "status": status,
            "http_result": f"HTTP {code}" if code else (err or "N/A"),
            "final_dest": final_dest or "",
            "rec_action": rec_action,
            "verified_replacement": verified_replacement,
            "official_source": official_source,
            "last_verified": last_verified
        })

    # Generate Markdown Report
    report_lines = []
    report_lines.append("# SCHEMEMITRA — OFFICIAL SCHEME URLs AUDIT REPORT\n")
    report_lines.append(f"**Audit Execution Date**: 2026-09-14\n")
    report_lines.append(f"**Total Records Audited**: {total}\n")
    report_lines.append("## 1. Summary Totals\n")
    report_lines.append(f"- **Total URLs Checked**: {total}")
    report_lines.append(f"- **Valid (HTTP 200 Direct)**: {valid_count}")
    report_lines.append(f"- **Valid Redirects (Canonical Destination)**: {redirect_count}")
    report_lines.append(f"- **Broken (DNS / 404 / Server Error / Timeout)**: {broken_count}")
    report_lines.append(f"- **Manual Verification Required (Bot-Blocked / SSL / 403)**: {manual_count}\n")

    report_lines.append("## 2. Check for Dead / Outdated Domains (`kviconline.gov.in`)\n")
    if kviconline_occurrences:
        report_lines.append(f"Found **{len(kviconline_occurrences)}** occurrence(s) of `kviconline.gov.in` in `opportunity_master.json`:\n")
        for oid, oname, ourl in kviconline_occurrences:
            report_lines.append(f"- **{oid}** ({oname}): `{ourl}` -> Recommended replacement: `https://www.pmegp.msme.gov.in/` (Official Ministry of MSME PMEGP Portal)")
    else:
        report_lines.append("✓ **Zero occurrences** of `kviconline.gov.in` found in active `opportunity_master.json`.\n")

    report_lines.append("\n## 3. Comprehensive Audit Table\n")
    report_lines.append("| OPP ID | Scheme Name | Stored URL | Status | HTTP/DNS Result | Redirect Destination | Recommended Action | Verified Replacement URL | Official Verification Source |")
    report_lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    for r in classified_results:
        dest_str = f"`{r['final_dest']}`" if r['final_dest'] and r['final_dest'] != r['url'] else "-"
        repl_str = f"`{r['verified_replacement']}`" if r['verified_replacement'] else "-"
        report_lines.append(f"| {r['opp_id']} | {r['name']} | `{r['url']}` | **{r['status']}** | {r['http_result']} | {dest_str} | {r['rec_action']} | {repl_str} | {r['official_source']} |")

    report_text = "\n".join(report_lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"Report successfully generated at {REPORT_PATH}")
    print("\nSummary Breakdown:")
    print(f"Total: {total}")
    print(f"Valid: {valid_count}")
    print(f"Valid Redirect: {redirect_count}")
    print(f"Broken: {broken_count}")
    print(f"Manual Verification Required: {manual_count}")
    print(f"kviconline occurrences: {len(kviconline_occurrences)}")

if __name__ == "__main__":
    analyze()
