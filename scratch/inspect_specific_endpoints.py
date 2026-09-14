"""
Targeted Inspector for:
1. NCGTC CGSS: https://www.ncgtc.in/en/cgss and https://www.ncgtc.in/content/cgss
2. NSFDC Schemes page: https://nsfdc.nic.in/scheme
"""

import urllib.request
import ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def inspect_url(url):
    print(f"\n==========================================")
    print(f"INSPECTING: {url}")
    print(f"==========================================")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            print(f"Status Code: {resp.getcode()}")
            print(f"Final URL: {resp.geturl()}")
            content = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            print(f"Page Title: {soup.title.string.strip() if soup.title else 'No Title'}")
            print(f"Content Length: {len(text)} characters")
            
            # Print sample text
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            print("Sample lines:")
            for l in lines[:15]:
                print(f"  {l}")

            # Check specific scheme keywords
            for kw in ["credit guarantee scheme for startups", "cgss", "mahila adhikarita", "laghu vyavasay", "green business", "loan", "scheme"]:
                matches = [l for l in lines if kw in l.lower()]
                if matches:
                    print(f"\n  Found Keyword '{kw}' ({len(matches)} matches):")
                    for m in matches[:5]:
                        print(f"    -> {m}")
    except Exception as e:
        print(f"Error inspecting {url}: {e}")

inspect_url("https://www.ncgtc.in/en/cgss")
inspect_url("https://www.ncgtc.in/content/cgss")
inspect_url("https://nsfdc.nic.in/scheme")
