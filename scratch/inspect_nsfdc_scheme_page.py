"""
Inspect NSFDC scheme page content and check scheme links.
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

req = urllib.request.Request("https://nsfdc.nic.in/scheme", headers=HEADERS)
with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

soup = BeautifulSoup(content, 'html.parser')
text = soup.get_text()

lines = [line.strip() for line in text.splitlines() if line.strip()]

print("=== ALL SCHEME HEADING / TEXT LINES ON NSFDC/SCHEME ===")
for l in lines:
    if any(k in l.lower() for k in ["loan", "scheme", "finance", "yojana", "mahila", "laghu", "green", "adhikarita", "vyavasay"]):
        print(f"  -> {l.encode('ascii', errors='replace').decode('ascii')}")

# Extract all links on nsfdc.nic.in/scheme
links = soup.find_all('a', href=True)
print(f"\n=== ALL LINKS ON NSFDC/SCHEME ({len(links)} links) ===")
for l in links:
    href = l['href']
    t = l.get_text(strip=True).encode('ascii', errors='replace').decode('ascii')
    print(f"  Text: {t} | Href: {href}")
