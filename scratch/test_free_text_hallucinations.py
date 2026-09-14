import sys
import re
import json
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def extract_allowed_tokens(trusted_context: dict) -> set:
    """Extracts all legitimate numbers, amounts, percentages, and URLs from trusted context."""
    allowed = set()

    # Flatten JSON to string and extract numbers
    raw_str = json.dumps(trusted_context)
    
    # Numbers (integers, floats)
    nums = re.findall(r'\b\d+(?:\.\d+)?\b', raw_str)
    for n in nums:
        allowed.add(n)
        # Also add formatted versions e.g. 500000 -> 5,00,000 / 5 lakh
        try:
            val = float(n)
            if val >= 100000 and val % 100000 == 0:
                allowed.add(f"{int(val//100000)} lakh")
                allowed.add(f"{int(val//100000)}lakh")
            if val >= 10000000 and val % 10000000 == 0:
                allowed.add(f"{int(val//10000000)} crore")
                allowed.add(f"{int(val//10000000)}crore")
        except ValueError:
            pass

    # Extract official URLs
    for url in trusted_context.get("official_sources", []):
        allowed.add(url.strip())

    return allowed


def sanitize_free_text(text: str, trusted_context: dict) -> str:
    """Sanitizes ungrounded monetary, percentage, deadline, URL, and approval claims from text."""
    if not text or not isinstance(text, str):
        return ""

    allowed_tokens = extract_allowed_tokens(trusted_context)
    official_urls = trusted_context.get("official_sources", [])

    # 1. Strip unverified URLs
    def url_sub(match):
        u = match.group(0)
        if any(u.startswith(off_u) for off_u in official_urls):
            return u
        return ""
    text = re.sub(r'https?://[^\s<>"]+', url_sub, text)

    # 2. Sanitize unverified monetary amounts: e.g. ₹10 lakh, INR 5,00,000, 25 lakh, 5,000 processing fee
    def money_sub(match):
        full_match = match.group(0)
        num_part = match.group('num')
        clean_num = num_part.replace(",", "")
        if clean_num in allowed_tokens or full_match.lower() in allowed_tokens:
            return full_match
        return "[amount specified in official guidelines]"

    # Pattern for monetary amounts
    money_pattern = re.compile(r'(?:₹|INR|\bRs\.?)\s*(?P<num>[\d,]+(?:\.\d+)?)\s*(?:lakh|crore|thousand|k)?\b|\b(?P<num2>[\d,]+)\s*(?:lakh|crore)\b', re.IGNORECASE)
    
    def money_replacer(m):
        raw = m.group(0)
        num = m.group('num') or m.group('num2') or ""
        clean_num = num.replace(",", "")
        if clean_num in allowed_tokens:
            return raw
        return "the eligible amount under scheme guidelines"

    text = money_pattern.sub(money_replacer, text)

    # 3. Sanitize unverified percentages e.g. 50%, 75%
    def pct_replacer(m):
        raw = m.group(0)
        num = m.group('num')
        if num in allowed_tokens:
            return raw
        return "the percentage specified under scheme rules"

    pct_pattern = re.compile(r'\b(?P<num>\d+(?:\.\d+)?)\s*%', re.IGNORECASE)
    text = pct_pattern.sub(pct_replacer, text)

    # 4. Sanitize unverified deadlines / dates e.g. 31st March 2026, 31st December 2026
    date_pattern = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{0,4}\b|\b(?:deadline|due date|expiry date)\b', re.IGNORECASE)
    def date_replacer(m):
        raw = m.group(0)
        if raw in allowed_tokens:
            return raw
        return "the timeline specified in official scheme notices"
    text = date_pattern.sub(date_replacer, text)

    # 5. Sanitize ungrounded approval / fee claims
    text = re.sub(r'\bofficially (?:approved|sanctioned|selected)\b', 'evaluated for eligibility', text, flags=re.IGNORECASE)
    text = re.sub(r'\bguarantee[s]?\s+\d+%\s+success\b', 'supports enterprise setup', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpay\s+(?:₹|INR|Rs\.?)\s*[\d,]+\s+(?:processing|upfront)\s+fee\b', 'follow official fee guidelines if any', text, flags=re.IGNORECASE)

    return text.strip()


# Test sanitization function
trusted_context = {
    "profile_summary": {
        "annual_income": 300000,
        "available_capital": 200000,
        "project_cost": 500000
    },
    "opportunity": {
        "opportunity_id": "OPP021",
        "name": "PMEGP"
    },
    "official_sources": ["https://kviconline.gov.in/pmegpeportal/"]
}

sample_bad = "You get ₹10 lakh grant with 50% subsidy. Submit DPR before 31st March 2026 at http://fake.com. Pay ₹5,000 processing fee."
sys.stdout.buffer.write(("BEFORE: " + sample_bad + "\n").encode('utf-8'))
sys.stdout.buffer.write(("AFTER : " + sanitize_free_text(sample_bad, trusted_context) + "\n").encode('utf-8'))
