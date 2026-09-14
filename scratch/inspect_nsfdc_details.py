"""
Detailed inspector for NSFDC & NCGTC pages.
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

def inspect(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(content, 'html.parser')
        return soup

print("=== NSFDC FAQS INSPECTION ===")
soup_faqs = inspect("https://nsfdc.nic.in/faqs")

for target in ["Mahila Adhikarita", "Laghu Vyavasay", "Green Business"]:
    print(f"\n--- Searching for: {target} in NSFDC FAQs ---")
    elements = soup_faqs.find_all(text=lambda t: t and target.lower() in t.lower())
    for el in elements[:5]:
        parent = el.parent
        print(f"Parent tag: <{parent.name}>")
        print(f"Text snippet: {parent.get_text(strip=True)[:300]}")
        # Check if inside link or has href
        if parent.name == 'a' or parent.find('a'):
            a_tag = parent if parent.name == 'a' else parent.find('a')
            print(f"  Link href: {a_tag.get('href')}")

print("\n=== NSFDC HOMEPAGE INSPECTION ===")
soup_home = inspect("https://nsfdc.nic.in/")

for target in ["Mahila Adhikarita", "Laghu Vyavasay", "Green Business"]:
    print(f"\n--- Searching for: {target} in NSFDC Homepage ---")
    elements = soup_home.find_all(text=lambda t: t and target.lower() in t.lower())
    for el in elements[:5]:
        parent = el.parent
        print(f"Parent tag: <{parent.name}>")
        print(f"Text snippet: {parent.get_text(strip=True)[:300]}")
        link = parent.find_parent('a') or (parent if parent.name == 'a' else None)
        if link and link.has_attr('href'):
            print(f"  Link href: {link['href']}")

print("\n=== NCGTC HOMEPAGE & SCHEME LINKS INSPECTION ===")
soup_ncgtc = inspect("https://www.ncgtc.in/")
ncgtc_links = soup_ncgtc.find_all('a', href=True)
cgss_ncgtc_links = [l for l in ncgtc_links if "cgss" in l['href'].lower() or "credit guarantee scheme for startups" in l.text.lower() or "startups" in l.text.lower()]
print(f"Found {len(cgss_ncgtc_links)} CGSS-related links on NCGTC homepage:")
for l in cgss_ncgtc_links:
    print(f"  Link Text: {l.text.strip()} | Href: {l['href']}")
