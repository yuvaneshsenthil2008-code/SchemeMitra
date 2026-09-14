"""
SchemeMitra — Comprehensive Second-Stage URL Audit Processor
Evaluates all 39 non-direct-valid records strictly against User Prompt Rules 1-8.
"""

import json

# Full dataset of 100 records
M1_FILE = "modules/M1_data/opportunity_master.json"
with open(M1_FILE, "r", encoding="utf-8") as f:
    opps = json.load(f)

opp_map = {o["Opportunity_ID"]: o for o in opps}

# List of all 39 non-direct-valid records with initial audit info
audit_records = [
    # 11 VALID_REDIRECT records
    ("OPP003", "Formation and Promotion of 10,000 Farmer Producer Organizations (FPOs)", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2296208", "VALID_REDIRECT", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2296208&reg=48&lang=2"),
    ("OPP027", "Micro & Small Enterprises Cluster Development Programme (MSE-CDP)", "https://cluster.dcmsme.gov.in/", "VALID_REDIRECT", "https://cluster.dcmsme.gov.in/Admin/Default.aspx"),
    ("OPP028", "International Cooperation Scheme (IC)", "https://ic.msme.gov.in/", "VALID_REDIRECT", "https://ic.msme.gov.in/IC_APP/IC_Welcome.aspx"),
    ("OPP030", "Raising and Accelerating MSME Performance (RAMP)", "https://ramp.msme.gov.in/", "VALID_REDIRECT", "https://ramp.msme.gov.in/ramp/"),
    ("OPP054", "Jan Shikshan Sansthan (JSS)", "https://jss.gov.in/", "VALID_REDIRECT", "https://www.skillindiadigital.gov.in//"),
    ("OPP055", "Craftsmen Training Scheme (CTS)", "https://dgt.gov.in/cts", "VALID_REDIRECT", "https://dgt.gov.in/hi/CTS"),
    ("OPP056", "Craft Instructor Training Scheme (CITS)", "https://dgt.gov.in/cits", "VALID_REDIRECT", "https://dgt.gov.in/hi/CITS"),
    ("OPP060", "Entrepreneurship and Skill Development Programme (ESDP)", "https://msme.gov.in/", "VALID_REDIRECT", "https://www.msme.gov.in/"),
    ("OPP077", "NSTFDC Term Loan Scheme", "https://nstfdc.tribal.gov.in/", "VALID_REDIRECT", "https://nstfdc.tribal.gov.in/(S(o0rztrqttoizuivpwvjovy42))/default.aspx"),
    ("OPP078", "NSTFDC Adivasi Mahila Sashaktikaran Yojana", "https://nstfdc.tribal.gov.in/", "VALID_REDIRECT", "https://nstfdc.tribal.gov.in/(S(uzm5owm50u41gnlr4t03oioo))/default.aspx"),
    ("OPP098", "Sustainable and Inclusive Development of Natural Rubber Sector", "https://rubberboard.gov.in/", "VALID_REDIRECT", "https://rubberboard.gov.in/public"),

    # 2 MANUAL_VERIFICATION_REQUIRED (403) records
    ("OPP040", "NBCFDC Micro Finance Scheme", "https://nbcfdc.gov.in/nbcfdc/web/pattern-of-finance", "MANUAL_VERIFICATION_REQUIRED", "HTTP 403"),
    ("OPP069", "NBCFDC Mahila Samriddhi Yojana", "https://nbcfdc.gov.in/nbcfdc/web/pattern-of-finance", "MANUAL_VERIFICATION_REQUIRED", "HTTP 403"),

    # 1 SERVER_ERROR (500) record
    ("OPP034", "Credit Guarantee Scheme for Startups (CGSS)", "https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss", "SERVER_ERROR", "HTTP 500"),

    # 2 BROKEN_DNS records
    ("OPP046", "Technology Incubation and Development of Entrepreneurs (TIDE 2.0)", "https://meitystartuphub.in/", "BROKEN_DNS", "DNS Failure"),
    ("OPP059", "Rural Self Employment Training Institutes (RSETI)", "https://rseti.gov.in/", "BROKEN_DNS", "DNS Failure"),

    # 7 BROKEN_404 records
    ("OPP017", "PMKSY – Creation/Expansion of Food Processing & Preservation Capacities", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "HTTP 404"),
    ("OPP018", "PMKSY – Agro Processing Cluster", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "HTTP 404"),
    ("OPP019", "PMKSY – Food Safety & Quality Assurance Infrastructure", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "HTTP 404"),
    ("OPP020", "Operation Greens", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "HTTP 404"),
    ("OPP067", "NSFDC Mahila Adhikarita Yojana", "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf", "BROKEN_404", "HTTP 404"),
    ("OPP074", "NSFDC Laghu Vyavasay Yojana (LVY)", "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf", "BROKEN_404", "HTTP 404"),
    ("OPP075", "NSFDC Green Business Scheme", "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf", "BROKEN_404", "HTTP 404"),
    ("OPP091", "Market Access Initiative (MAI)", "https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/", "BROKEN_404", "HTTP 404"),
    ("OPP092", "Trade Infrastructure for Export Scheme (TIES)", "https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/", "BROKEN_404", "HTTP 404"),

    # 17 TIMEOUT records
    ("OPP050", "Atal Incubation Centres (AIC)", "https://aim.gov.in/aic.php", "TIMEOUT", "Connection Timed Out"),
    ("OPP057", "PM-DAKSH", "https://pmdaksh.dosje.gov.in/", "TIMEOUT", "Connection Timed Out"),
    ("OPP062", "DAY-NRLM – SHG Bank Linkage & Enterprise Financing", "https://aajeevika.gov.in/", "TIMEOUT", "Connection Timed Out"),
    ("OPP063", "Start-up Village Entrepreneurship Programme (SVEP)", "https://aajeevika.gov.in/", "TIMEOUT", "Connection Timed Out"),
    ("OPP064", "Lakhpati Didi Initiative", "https://aajeevika.gov.in/", "TIMEOUT", "Connection Timed Out"),
    ("OPP065", "Mahila Coir Yojana", "https://coirboard.gov.in/?page_id=8452", "TIMEOUT", "Connection Timed Out"),
    ("OPP070", "NSKFDC Mahila Samridhi Yojana (MSY)", "https://nskfdc.nic.in/en/content/schemes-programmes/mahila-samridhi-yojna-msy", "TIMEOUT", "Connection Timed Out"),
    ("OPP072", "SMILE – Livelihood/Skill Support for Transgender Persons", "https://transgender.dosje.gov.in/", "TIMEOUT", "Connection Timed Out"),
    ("OPP079", "NSKFDC General Term Loan", "https://nskfdc.nic.in/en/content/schemes-programmes/general-term-loan-tl", "TIMEOUT", "Connection Timed Out"),
    ("OPP080", "NSKFDC Swachhta Udyami Yojana (SUY)", "https://nskfdc.nic.in/en/node/4083", "TIMEOUT", "Connection Timed Out"),
    ("OPP083", "NHDP – Ambedkar Hastshilp Vikas Yojana (AHVY)", "https://handicrafts.nic.in/schemes.aspx", "TIMEOUT", "Connection Timed Out"),
    ("OPP084", "NHDP – Marketing Support & Services (MSS)", "https://handicrafts.nic.in/tenders.aspx?type=27", "TIMEOUT", "Connection Timed Out"),
    ("OPP085", "NHDP – Skill Development for Handicraft Sector (SDHS)", "https://handicrafts.nic.in/tenders.aspx?type=27", "TIMEOUT", "Connection Timed Out"),
    ("OPP086", "NHDP – Infrastructure & Technology Support", "https://handicrafts.nic.in/tenders.aspx?type=27", "TIMEOUT", "Connection Timed Out"),
]

print(f"Total audit records: {len(audit_records)}")
