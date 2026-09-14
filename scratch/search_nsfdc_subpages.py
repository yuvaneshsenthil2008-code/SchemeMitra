"""
Subpage content search on nsfdc.nic.in for Mahila Adhikarita, Laghu Vyavasay, Green Business.
"""

import urllib.request
import ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

subpages = [
    "https://nsfdc.nic.in/form",
    "https://nsfdc.nic.in/indicative-activities",
    "https://nsfdc.nic.in/publication",
    "https://nsfdc.nic.in/performance-data",
    "https://nsfdc.nic.in/annual-reports",
    "https://nsfdc.nic.in/how-to-apply-2"
]

for url in subpages:
    print(f"\n==========================================")
    print(f"CHECKING: {url}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            code = resp.getcode()
            content = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text().lower()
            print(f"  Status: {code} | Text Length: {len(text)}")
            
            for kw in ["mahila", "adhikarita", "laghu", "vyavasay", "green business"]:
                if kw in text:
                    print(f"  -> Found match for '{kw}'!")
    except Exception as e:
        print(f"  Error: {e}")
