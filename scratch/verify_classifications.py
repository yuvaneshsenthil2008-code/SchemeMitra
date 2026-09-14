"""
Verification script for Second-Stage URL Audit classifications.
"""

classifications = {
    "KEEP_CURRENT_URL": [
        ("OPP003", "Formation and Promotion of 10,000 Farmer Producer Organizations (FPOs)", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2296208", "VALID_REDIRECT", "-", "Stored URL is clean canonical PIB permalink; redirect adds tracking/lang params (reg=48&lang=2).", "Press Information Bureau (PIB), Govt of India"),
        ("OPP027", "Micro & Small Enterprises Cluster Development Programme (MSE-CDP)", "https://cluster.dcmsme.gov.in/", "VALID_REDIRECT", "-", "Root portal URL is clean and stable; auto-resolves to ASP.NET default page.", "Office of DC MSME"),
        ("OPP028", "International Cooperation Scheme (IC)", "https://ic.msme.gov.in/", "VALID_REDIRECT", "-", "Root portal URL is clean and stable.", "Ministry of MSME IC Portal"),
        ("OPP030", "Raising and Accelerating MSME Performance (RAMP)", "https://ramp.msme.gov.in/", "VALID_REDIRECT", "-", "Root portal URL is clean and stable.", "Ministry of MSME RAMP Portal"),
        ("OPP055", "Craftsmen Training Scheme (CTS)", "https://dgt.gov.in/cts", "VALID_REDIRECT", "-", "Stored URL is language-neutral; redirect adds /hi/ Hindi language subpath.", "Directorate General of Training (DGT), MSDE"),
        ("OPP056", "Craft Instructor Training Scheme (CITS)", "https://dgt.gov.in/cits", "VALID_REDIRECT", "-", "Stored URL is language-neutral; redirect adds /hi/ Hindi language subpath.", "Directorate General of Training (DGT), MSDE"),
        ("OPP060", "Entrepreneurship and Skill Development Programme (ESDP)", "https://msme.gov.in/", "VALID_REDIRECT", "-", "Stored URL points to clean Ministry domain.", "Ministry of MSME"),
        ("OPP077", "NSTFDC Term Loan Scheme", "https://nstfdc.tribal.gov.in/", "VALID_REDIRECT", "-", "Redirect destination contains transient ASP.NET session ID token /(S(...))/; root domain preserved.", "NSTFDC, Ministry of Tribal Affairs"),
        ("OPP078", "NSTFDC Adivasi Mahila Sashaktikaran Yojana", "https://nstfdc.tribal.gov.in/", "VALID_REDIRECT", "-", "Redirect destination contains transient ASP.NET session ID token /(S(...))/; root domain preserved.", "NSTFDC, Ministry of Tribal Affairs"),
        ("OPP098", "Sustainable and Inclusive Development of Natural Rubber Sector", "https://rubberboard.gov.in/", "VALID_REDIRECT", "-", "Root domain is clean and auto-routes to public portal endpoint.", "Rubber Board, Ministry of Commerce & Industry")
    ],
    "SAFE_TO_UPDATE": [
        ("OPP034", "Credit Guarantee Scheme for Startups (CGSS)", "https://www.ncgtc.in/content/credit-guarantee-scheme-startups-cgss", "SERVER_ERROR", "https://www.startupindia.gov.in/content/sih/en/government-schemes/cgss.html", "Stored NCGTC page returns HTTP 500 server error; replaced with dedicated official Government of India Startup India scheme portal page (HTTP 200).", "DPIIT / Startup India Portal, Ministry of Commerce & Industry"),
        ("OPP054", "Jan Shikshan Sansthan (JSS)", "https://jss.gov.in/", "VALID_REDIRECT", "https://www.skillindiadigital.gov.in/portal/jan-shikshan-sansthan", "Old domain jss.gov.in redirects with double-slash glitch; replaced with dedicated official Skill India Digital scheme portal page (HTTP 200).", "MSDE / Skill India Digital Portal"),
        ("OPP067", "NSFDC Mahila Adhikarita Yojana", "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf", "BROKEN_404", "https://nsfdc.nic.in/faqs", "Stored PDF URL is 404; replaced with active official NSFDC scheme directory page (HTTP 200).", "NSFDC, Ministry of Social Justice and Empowerment"),
        ("OPP074", "NSFDC Laghu Vyavasay Yojana (LVY)", "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf", "BROKEN_404", "https://nsfdc.nic.in/faqs", "Stored PDF URL is 404; replaced with active official NSFDC scheme directory page (HTTP 200).", "NSFDC, Ministry of Social Justice and Empowerment"),
        ("OPP075", "NSFDC Green Business Scheme", "https://nsfdc.nic.in/UploadedFiles/other/2024-05-15/1-4-1.pdf", "BROKEN_404", "https://nsfdc.nic.in/faqs", "Stored PDF URL is 404; replaced with active official NSFDC scheme directory page (HTTP 200).", "NSFDC, Ministry of Social Justice and Empowerment")
    ],
    "MANUAL_BROWSER_CHECK": [
        ("OPP040", "NBCFDC Micro Finance Scheme", "https://nbcfdc.gov.in/nbcfdc/web/pattern-of-finance", "MANUAL_VERIFICATION_REQUIRED", "-", "Automated request blocked by server WAF (HTTP 403); requires manual browser check.", "NBCFDC Official Portal"),
        ("OPP050", "Atal Incubation Centres (AIC)", "https://aim.gov.in/aic.php", "TIMEOUT", "-", "Automated request timed out; scheme page requires manual desktop browser verification.", "Atal Innovation Mission (AIM), NITI Aayog"),
        ("OPP057", "PM-DAKSH", "https://pmdaksh.dosje.gov.in/", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Ministry of Social Justice and Empowerment"),
        ("OPP062", "DAY-NRLM – SHG Bank Linkage & Enterprise Financing", "https://aajeevika.gov.in/", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Ministry of Rural Development"),
        ("OPP063", "Start-up Village Entrepreneurship Programme (SVEP)", "https://aajeevika.gov.in/", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Ministry of Rural Development"),
        ("OPP064", "Lakhpati Didi Initiative", "https://aajeevika.gov.in/", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Ministry of Rural Development"),
        ("OPP065", "Mahila Coir Yojana", "https://coirboard.gov.in/?page_id=8452", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Coir Board, Ministry of MSME"),
        ("OPP069", "NBCFDC Mahila Samriddhi Yojana", "https://nbcfdc.gov.in/nbcfdc/web/pattern-of-finance", "MANUAL_VERIFICATION_REQUIRED", "-", "Automated request blocked by server WAF (HTTP 403); requires manual browser check.", "NBCFDC Official Portal"),
        ("OPP070", "NSKFDC Mahila Samridhi Yojana (MSY)", "https://nskfdc.nic.in/en/content/schemes-programmes/mahila-samridhi-yojna-msy", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "NSKFDC Official Portal"),
        ("OPP072", "SMILE – Livelihood/Skill Support for Transgender Persons", "https://transgender.dosje.gov.in/", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Ministry of Social Justice and Empowerment"),
        ("OPP079", "NSKFDC General Term Loan", "https://nskfdc.nic.in/en/content/schemes-programmes/general-term-loan-tl", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "NSKFDC Official Portal"),
        ("OPP080", "NSKFDC Swachhta Udyami Yojana (SUY)", "https://nskfdc.nic.in/en/node/4083", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "NSKFDC Official Portal"),
        ("OPP083", "NHDP – Ambedkar Hastshilp Vikas Yojana (AHVY)", "https://handicrafts.nic.in/schemes.aspx", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Development Commissioner (Handicrafts), Ministry of Textiles"),
        ("OPP084", "NHDP – Marketing Support & Services (MSS)", "https://handicrafts.nic.in/tenders.aspx?type=27", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Development Commissioner (Handicrafts), Ministry of Textiles"),
        ("OPP085", "NHDP – Skill Development for Handicraft Sector (SDHS)", "https://handicrafts.nic.in/tenders.aspx?type=27", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Development Commissioner (Handicrafts), Ministry of Textiles"),
        ("OPP086", "NHDP – Infrastructure & Technology Support", "https://handicrafts.nic.in/tenders.aspx?type=27", "TIMEOUT", "-", "Automated request timed out; portal requires manual desktop browser verification.", "Development Commissioner (Handicrafts), Ministry of Textiles")
    ],
    "OFFICIAL_FALLBACK_ONLY": [
        ("OPP017", "PMKSY – Creation/Expansion of Food Processing & Preservation Capacities", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "https://mofpi.gov.in/", "Stored URL is 404; sub-scheme page restructured. Ministry root portal is active HTTP 200 fallback.", "Ministry of Food Processing Industries (MoFPI)"),
        ("OPP018", "PMKSY – Agro Processing Cluster", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "https://mofpi.gov.in/", "Stored URL is 404; sub-scheme page restructured. Ministry root portal is active HTTP 200 fallback.", "Ministry of Food Processing Industries (MoFPI)"),
        ("OPP019", "PMKSY – Food Safety & Quality Assurance Infrastructure", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "https://mofpi.gov.in/", "Stored URL is 404; sub-scheme page restructured. Ministry root portal is active HTTP 200 fallback.", "Ministry of Food Processing Industries (MoFPI)"),
        ("OPP020", "Operation Greens", "https://mofpi.gov.in/Schemes/operation-greens", "BROKEN_404", "https://mofpi.gov.in/", "Stored URL is 404; sub-scheme page restructured. Ministry root portal is active HTTP 200 fallback.", "Ministry of Food Processing Industries (MoFPI)"),
        ("OPP046", "Technology Incubation and Development of Entrepreneurs (TIDE 2.0)", "https://meitystartuphub.in/", "BROKEN_DNS", "https://msh.meity.gov.in/", "Stored domain meitystartuphub.in failed DNS; replaced with official active MeitY Startup Hub portal.", "MeitY Startup Hub, Ministry of Electronics & IT"),
        ("OPP059", "Rural Self Employment Training Institutes (RSETI)", "https://rseti.gov.in/", "BROKEN_DNS", "https://rural.gov.in/", "Stored domain rseti.gov.in failed DNS; replaced with active Ministry of Rural Development homepage fallback.", "Ministry of Rural Development"),
        ("OPP091", "Market Access Initiative (MAI)", "https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/", "BROKEN_404", "https://commerce.gov.in/", "Stored URL is 404; replaced with active Department of Commerce homepage fallback.", "Department of Commerce, Ministry of Commerce & Industry"),
        ("OPP092", "Trade Infrastructure for Export Scheme (TIES)", "https://commerce.gov.in/trade-promotion/market-access-initiative-mai-scheme/", "BROKEN_404", "https://commerce.gov.in/", "Stored URL is 404; replaced with active Department of Commerce homepage fallback.", "Department of Commerce, Ministry of Commerce & Industry")
    ],
    "NEEDS_FURTHER_RESEARCH": []
}

total_count = sum(len(v) for v in classifications.values())
print("=== CLASSIFICATION SUMMARY COUNTS ===")
for k, v in classifications.items():
    print(f"{k}: {len(v)}")
print(f"TOTAL AUDITED RECORDS: {total_count}")
assert total_count == 39, "Expected exactly 39 audited records"
