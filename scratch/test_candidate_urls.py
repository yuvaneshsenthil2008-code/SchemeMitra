"""
Second stage URL audit helper: tests candidate URLs with browser-like user-agent, follows redirects, checks HTTPS status, and logs detailed diagnostic output.
"""

import json
import urllib.request
import urllib.error
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

def test_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            final_url = resp.geturl()
            code = resp.getcode()
            return {
                "status": "SUCCESS",
                "code": code,
                "final_url": final_url,
                "is_redirect": final_url.strip('/') != url.strip('/')
            }
    except urllib.error.HTTPError as e:
        return {"status": "HTTP_ERROR", "code": e.code, "final_url": e.url}
    except urllib.error.URLError as e:
        reason_str = str(e.reason)
        if "timed out" in reason_str.lower():
            return {"status": "TIMEOUT", "code": None, "reason": reason_str}
        return {"status": "URL_ERROR", "code": None, "reason": reason_str}
    except Exception as e:
        return {"status": "EXCEPTION", "code": None, "reason": str(e)}

# Specific candidate URL tests for BROKEN / 404 / 500 / DNS items
candidates_to_check = [
    # MoFPI schemes (OPP017, OPP018, OPP019, OPP020)
    ("OPP017", "PMKSY - CEFPPC", ["https://mofpi.gov.in/Schemes/creationexpansion-food-processing-preservation-capacities-cefppc", "https://mofpi.gov.in/en/Schemes/creationexpansion-food-processing-preservation-capacities-cefppc", "https://mofpi.gov.in/"]),
    ("OPP018", "PMKSY - Agro Processing Cluster", ["https://mofpi.gov.in/Schemes/agro-processing-cluster", "https://mofpi.gov.in/en/Schemes/agro-processing-cluster", "https://mofpi.gov.in/"]),
    ("OPP019", "PMKSY - Food Safety", ["https://mofpi.gov.in/Schemes/food-safety-and-quality-assurance-infrastructure", "https://mofpi.gov.in/en/Schemes/food-safety-and-quality-assurance-infrastructure", "https://mofpi.gov.in/"]),
    ("OPP020", "Operation Greens", ["https://mofpi.gov.in/Schemes/operation-greens", "https://mofpi.gov.in/en/Schemes/operation-greens", "https://mofpi.gov.in/"]),
    
    # NCGTC / CGSS (OPP034)
    ("OPP034", "CGSS", ["https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss", "https://www.ncgtc.in/", "https://www.startupindia.gov.in/content/sih/en/government-schemes/cgss.html"]),
    
    # TIDE 2.0 (OPP046)
    ("OPP046", "TIDE 2.0", ["https://msh.meity.gov.in/schemes/tide", "https://msh.meity.gov.in/", "https://meity.gov.in/content/tide-20"]),
    
    # RSETI (OPP059)
    ("OPP059", "RSETI", ["https://nert.in/", "https://rural.gov.in/", "https://rseti.org.in/"]),

    # NSFDC PDF 404s (OPP067, OPP074, OPP075)
    ("OPP067", "NSFDC Mahila Adhikarita", ["https://nsfdc.nic.in/faqs", "https://nsfdc.nic.in/"]),
    ("OPP074", "NSFDC Laghu Vyavasay", ["https://nsfdc.nic.in/faqs", "https://nsfdc.nic.in/"]),
    ("OPP075", "NSFDC Green Business", ["https://nsfdc.nic.in/faqs", "https://nsfdc.nic.in/"]),

    # Ministry of Commerce MAI & TIES (OPP091, OPP092)
    ("OPP091", "MAI", ["https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/", "https://www.commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/", "https://commerce.gov.in/"]),
    ("OPP092", "TIES", ["https://commerce.gov.in/trade-promotion/trade-infrastructure-for-export-scheme-ties/", "https://www.commerce.gov.in/trade-promotion/trade-infrastructure-for-export-scheme-ties/", "https://commerce.gov.in/"]),

    # Skill India Digital / JSS (OPP054)
    ("OPP054", "JSS", ["https://www.skillindiadigital.gov.in/", "https://www.skillindiadigital.gov.in/portal/jan-shikshan-sansthan"]),
]

print("=== CANDIDATE URL TESTING ===")
for opp_id, name, urls in candidates_to_check:
    print(f"\n--- {opp_id}: {name} ---")
    for u in urls:
        res = test_url(u)
        print(f"  URL: {u}")
        print(f"  Result: {res}")
