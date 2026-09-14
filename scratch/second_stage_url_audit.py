"""
SchemeMitra — Second-Stage URL Audit Script
Performs strict audit & classification of 39 non-valid scheme URLs according to exact prompt rules.
"""

import json
import urllib.request
import urllib.error
import ssl
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
M1_FILE = ROOT_DIR / "modules" / "M1_data" / "opportunity_master.json"

with open(M1_FILE, "r", encoding="utf-8") as f:
    opps = json.load(f)

# List of 39 non-direct-valid OPP IDs from initial audit
NON_VALID_OPP_IDS = [
    "OPP003", "OPP017", "OPP018", "OPP019", "OPP020",
    "OPP027", "OPP028", "OPP030", "OPP034", "OPP040",
    "OPP046", "OPP050", "OPP054", "OPP055", "OPP056",
    "OPP057", "OPP059", "OPP060", "OPP062", "OPP063",
    "OPP064", "OPP065", "OPP067", "OPP069", "OPP070",
    "OPP072", "OPP074", "OPP075", "OPP077", "OPP078",
    "OPP079", "OPP080", "OPP083", "OPP084", "OPP085",
    "OPP086", "OPP091", "OPP092", "OPP098"
]

print(f"Total non-valid OPP IDs to audit: {len(NON_VALID_OPP_IDS)}")
