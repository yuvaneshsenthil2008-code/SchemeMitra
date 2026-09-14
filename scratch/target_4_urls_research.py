"""
Targeted Research Script for 4 Specific Scheme Records:
OPP034 (CGSS), OPP067 (NSFDC Mahila Adhikarita), OPP074 (NSFDC Laghu Vyavasay), OPP075 (NSFDC Green Business).
"""

import urllib.request
import urllib.error
import ssl
import re
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_page(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            return {
                "status": "SUCCESS",
                "code": resp.getcode(),
                "url": resp.geturl(),
                "content": content
            }
    except urllib.error.HTTPError as e:
        return {"status": "HTTP_ERROR", "code": e.code, "url": e.url, "content": ""}
    except Exception as e:
        return {"status": "ERROR", "code": None, "reason": str(e), "content": ""}

print("=== 1. RESEARCHING OPP034 (CGSS) CANDIDATES ===")
cgss_candidates = [
    "https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss",
    "https://www.ncgtc.in/en/option-1",
    "https://www.ncgtc.in/en/cgss",
    "https://www.ncgtc.in/content/cgss",
    "https://www.ncgtc.in/",
    "https://www.startupindia.gov.in/content/sih/en/government-schemes/cgss.html",
    "https://www.startupindia.gov.in/content/sih/en/government-schemes.html",
    "https://dpiit.gov.in/schemes/credit-guarantee-scheme-startups-cgss"
]

for url in cgss_candidates:
    res = fetch_page(url)
    print(f"URL: {url} -> Status: {res['status']}, Code: {res['code']}")
    if res['status'] == "SUCCESS":
        text = BeautifulSoup(res['content'], 'html.parser').get_text()
        has_cgss = "credit guarantee scheme for startups" in text.lower() or "cgss" in text.lower()
        print(f"  Contains CGSS keywords: {has_cgss}")

print("\n=== 2. RESEARCHING NSFDC PAGES FOR OPP067, OPP074, OPP075 ===")
nsfdc_urls = [
    "https://nsfdc.nic.in/faqs",
    "https://nsfdc.nic.in/",
    "https://nsfdc.nic.in/en/content/schemes-programmes",
    "https://nsfdc.nic.in/en/schemes"
]

for url in nsfdc_urls:
    res = fetch_page(url)
    print(f"\nURL: {url} -> Status: {res['status']}, Code: {res['code']}")
    if res['status'] == "SUCCESS":
        soup = BeautifulSoup(res['content'], 'html.parser')
        text = soup.get_text()
        
        # Check explicit scheme keywords
        has_mahila = "mahila adhikarita" in text.lower()
        has_laghu = "laghu vyavasay" in text.lower()
        has_green = "green business" in text.lower()
        
        print(f"  Explicitly contains 'Mahila Adhikarita': {has_mahila}")
        print(f"  Explicitly contains 'Laghu Vyavasay': {has_laghu}")
        print(f"  Explicitly contains 'Green Business': {has_green}")
        
        # Find all pdf links or scheme links
        links = soup.find_all('a', href=True)
        scheme_links = [l['href'] for l in links if any(k in l.text.lower() or k in l['href'].lower() for k in ['mahila', 'laghu', 'green', 'scheme', 'loan', 'pdf'])]
        print(f"  Matching scheme/loan links count: {len(scheme_links)}")
        for sl in scheme_links[:10]:
            print(f"    - Link: {sl}")
