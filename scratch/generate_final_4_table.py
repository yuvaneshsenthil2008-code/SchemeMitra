"""
Verifier for final targeted 4 records report formatting and data consistency.
"""

data = [
    {
        "opp_id": "OPP034",
        "scheme": "Credit Guarantee Scheme for Startups (CGSS)",
        "current_url": "https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss",
        "candidates": "1. https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss (HTTP 500)<br>2. https://www.ncgtc.in/content/cgss (HTTP 200)<br>3. https://www.ncgtc.in/en/cgss (HTTP 200)<br>4. https://www.startupindia.gov.in/content/sih/en/government-schemes/cgss.html (HTTP 404)",
        "best_url": "https://www.ncgtc.in/content/cgss",
        "classification": "SAFE_TO_UPDATE",
        "reason": "Old path returns HTTP 500. NCGTC updated the active path to /content/cgss, which is live (HTTP 200) and contains official guidelines, DPIIT notifications, and registered lender lists specifically for CGSS."
    },
    {
        "opp_id": "OPP067",
        "scheme": "NSFDC Mahila Adhikarita Yojana",
        "current_url": "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf",
        "candidates": "1. https://nsfdc.nic.in/UploadedFiles/.../1-4-1.pdf (HTTP 404)<br>2. https://nsfdc.nic.in/scheme (HTTP 200, no explicit mention)<br>3. https://nsfdc.nic.in/faqs (HTTP 200, no explicit mention)<br>4. https://nsfdc.nic.in/ (HTTP 200)",
        "best_url": "https://nsfdc.nic.in/scheme",
        "classification": "OFFICIAL_FALLBACK_ONLY",
        "reason": "Stored PDF returns HTTP 404. NSFDC restructured its portal into umbrella loan pages on /scheme without maintaining a separate active dedicated page or PDF for Mahila Adhikarita."
    },
    {
        "opp_id": "OPP074",
        "scheme": "NSFDC Laghu Vyavasay Yojana (LVY)",
        "current_url": "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf",
        "candidates": "1. https://nsfdc.nic.in/UploadedFiles/.../1-4-1.pdf (HTTP 404)<br>2. https://nsfdc.nic.in/scheme (HTTP 200, no explicit mention)<br>3. https://nsfdc.nic.in/faqs (HTTP 200, no explicit mention)<br>4. https://nsfdc.nic.in/ (HTTP 200)",
        "best_url": "https://nsfdc.nic.in/scheme",
        "classification": "OFFICIAL_FALLBACK_ONLY",
        "reason": "Stored PDF returns HTTP 404. Current NSFDC portal does not list a dedicated active page or valid PDF for Laghu Vyavasay Yojana."
    },
    {
        "opp_id": "OPP075",
        "scheme": "NSFDC Green Business Scheme",
        "current_url": "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf",
        "candidates": "1. https://nsfdc.nic.in/UploadedFiles/.../1-4-1.pdf (HTTP 404)<br>2. https://nsfdc.nic.in/scheme (HTTP 200, no explicit mention)<br>3. https://nsfdc.nic.in/faqs (HTTP 200, no explicit mention)<br>4. https://nsfdc.nic.in/ (HTTP 200)",
        "best_url": "https://nsfdc.nic.in/scheme",
        "classification": "OFFICIAL_FALLBACK_ONLY",
        "reason": "Stored PDF returns HTTP 404. Current NSFDC portal does not list a dedicated active page or valid PDF for Green Business Scheme."
    }
]

print("Targeted 4 Records Summary:")
for d in data:
    print(f"{d['opp_id']}: {d['classification']} -> Best URL: {d['best_url']}")
