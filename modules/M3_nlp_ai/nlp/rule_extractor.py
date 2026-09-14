import json
import re
from pathlib import Path
from .money_parser import MoneyParser
from .support_inference import SupportInference


class RuleExtractor:
    """Deterministic, evidence-first entity extractor.

    Rules intentionally prefer missing a fact over assigning a number/value to
    the wrong field.  Difficult cases can be passed to the optional LLM layer.
    """

    def __init__(self):
        self.money = MoneyParser()
        self.support = SupportInference()
        loc_path = Path(__file__).resolve().parent.parent / "data" / "india_locations.json"
        if loc_path.exists():
            try:
                self.india_locations = json.loads(loc_path.read_text(encoding="utf-8"))
            except Exception:
                self.india_locations = {}
        else:
            self.india_locations = {}

    GENDER_MAP = {
        "male": "Male", "man": "Male", "boy": "Male", "female": "Female", "woman": "Female", "girl": "Female",
        "transgender": "Transgender", "trans man": "Transgender", "trans woman": "Transgender", "third gender": "Transgender",
        "hijra": "Transgender", "kinnar": "Transgender", "thirunangai": "Transgender", "thirunambi": "Transgender",
        "aan": "Male", "aambala": "Male", "ponnu": "Female", "pen": "Female",
        "ஆண்": "Male", "பெண்": "Female", "पुरुष": "Male", "महिला": "Female", "आदमी": "Male", "औरत": "Female",
        "పురుషుడు": "Male", "మగ": "Male", "మహిళ": "Female", "ఆడ": "Female",
        "ಪುರುಷ": "Male", "ಗಂಡು": "Male", "ಮಹಿಳೆ": "Female", "ಹೆಣ್ಣು": "Female",
        "പുരുഷൻ": "Male", "ആൺ": "Male", "സ്ത്രീ": "Female", "പെൺ": "Female",
        "পুরুষ": "Male", "মহিলা": "Female",
    }

    STATE_MAP = {
        "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu", "tn": "Tamil Nadu", "kerala": "Kerala", "karnataka": "Karnataka",
        "andhra pradesh": "Andhra Pradesh", "telangana": "Telangana", "maharashtra": "Maharashtra", "delhi": "Delhi",
        "uttar pradesh": "Uttar Pradesh", "west bengal": "West Bengal", "bihar": "Bihar", "rajasthan": "Rajasthan",
        "gujarat": "Gujarat", "punjab": "Punjab", "haryana": "Haryana", "odisha": "Odisha", "assam": "Assam",
        "madhya pradesh": "Madhya Pradesh", "jharkhand": "Jharkhand", "chhattisgarh": "Chhattisgarh", "goa": "Goa",
        "தமிழ்நாடு": "Tamil Nadu", "தமிழ்நாட்டில்": "Tamil Nadu", "தமிழ்நாட்டை": "Tamil Nadu", "கேரளா": "Kerala", "கேரளாவில்": "Kerala", "கர்நாடகா": "Karnataka",
        "तमिलनाडु": "Tamil Nadu", "तमिल नाडु": "Tamil Nadu", "केरल": "Kerala", "कर्नाटक": "Karnataka", "महाराष्ट्र": "Maharashtra",
        "उत्तर प्रदेश": "Uttar Pradesh", "पश्चिम बंगाल": "West Bengal", "बिहार": "Bihar", "राजस्थान": "Rajasthan", "गुजरात": "Gujarat",
        "తమిళనాడు": "Tamil Nadu", "తెలంగాణ": "Telangana", "ఆంధ్ర ప్రదేశ్": "Andhra Pradesh", "కర్ణాటక": "Karnataka", "కేరళ": "Kerala",
        "ತಮಿಳುನಾಡು": "Tamil Nadu", "ಕರ್ನಾಟಕ": "Karnataka", "ಕೇರಳ": "Kerala", "ತೆಲಂಗಾಣ": "Telangana",
        "തമിഴ്നാട്": "Tamil Nadu", "കേരളം": "Kerala", "കർണാടക": "Karnataka", "തെലങ്കാന": "Telangana",
        "তামিলনাড়ু": "Tamil Nadu", "পশ্চিমবঙ্গ": "West Bengal", "কেরল": "Kerala", "কর্ণাটক": "Karnataka",
    }

    CITY_STATE_MAP = {
        # Tamil Nadu districts / major cities
        "ariyalur": ("Ariyalur", "Tamil Nadu"), "chengalpattu": ("Chengalpattu", "Tamil Nadu"),
        "chennai": ("Chennai", "Tamil Nadu"), "coimbatore": ("Coimbatore", "Tamil Nadu"),
        "cuddalore": ("Cuddalore", "Tamil Nadu"), "dharmapuri": ("Dharmapuri", "Tamil Nadu"),
        "dindigul": ("Dindigul", "Tamil Nadu"), "erode": ("Erode", "Tamil Nadu"),
        "kallakurichi": ("Kallakurichi", "Tamil Nadu"), "kanchipuram": ("Kanchipuram", "Tamil Nadu"),
        "kanyakumari": ("Kanyakumari", "Tamil Nadu"), "nagercoil": ("Kanyakumari", "Tamil Nadu"),
        "karur": ("Karur", "Tamil Nadu"), "krishnagiri": ("Krishnagiri", "Tamil Nadu"),
        "madurai": ("Madurai", "Tamil Nadu"), "mayiladuthurai": ("Mayiladuthurai", "Tamil Nadu"),
        "nagapattinam": ("Nagapattinam", "Tamil Nadu"), "namakkal": ("Namakkal", "Tamil Nadu"),
        "nilgiris": ("Nilgiris", "Tamil Nadu"), "ooty": ("Nilgiris", "Tamil Nadu"),
        "perambalur": ("Perambalur", "Tamil Nadu"), "pudukkottai": ("Pudukkottai", "Tamil Nadu"),
        "ramanathapuram": ("Ramanathapuram", "Tamil Nadu"), "ranipet": ("Ranipet", "Tamil Nadu"),
        "salem": ("Salem", "Tamil Nadu"), "sivaganga": ("Sivaganga", "Tamil Nadu"),
        "tenkasi": ("Tenkasi", "Tamil Nadu"), "thanjavur": ("Thanjavur", "Tamil Nadu"),
        "theni": ("Theni", "Tamil Nadu"), "thoothukudi": ("Thoothukudi", "Tamil Nadu"),
        "tuticorin": ("Thoothukudi", "Tamil Nadu"), "tiruchirappalli": ("Tiruchirappalli", "Tamil Nadu"),
        "trichy": ("Tiruchirappalli", "Tamil Nadu"), "tirunelveli": ("Tirunelveli", "Tamil Nadu"),
        "tirupathur": ("Tirupathur", "Tamil Nadu"), "tiruppur": ("Tiruppur", "Tamil Nadu"),
        "tirupur": ("Tiruppur", "Tamil Nadu"), "tiruvallur": ("Tiruvallur", "Tamil Nadu"),
        "tiruvannamalai": ("Tiruvannamalai", "Tamil Nadu"), "tiruvarur": ("Tiruvarur", "Tamil Nadu"),
        "vellore": ("Vellore", "Tamil Nadu"), "viluppuram": ("Viluppuram", "Tamil Nadu"),
        "virudhunagar": ("Virudhunagar", "Tamil Nadu"),

        # Major places across India. Ambiguous place names are intentionally omitted.
        "bengaluru": ("Bengaluru", "Karnataka"), "bangalore": ("Bengaluru", "Karnataka"),
        "mysuru": ("Mysuru", "Karnataka"), "mysore": ("Mysuru", "Karnataka"),
        "mangaluru": ("Mangaluru", "Karnataka"), "mangalore": ("Mangaluru", "Karnataka"),
        "hubballi": ("Hubballi", "Karnataka"), "belagavi": ("Belagavi", "Karnataka"),
        "kalaburagi": ("Kalaburagi", "Karnataka"), "shivamogga": ("Shivamogga", "Karnataka"),
        "hyderabad": ("Hyderabad", "Telangana"), "warangal": ("Warangal", "Telangana"),
        "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"), "vijayawada": ("Vijayawada", "Andhra Pradesh"),
        "guntur": ("Guntur", "Andhra Pradesh"), "tirupati": ("Tirupati", "Andhra Pradesh"),
        "mumbai": ("Mumbai", "Maharashtra"), "pune": ("Pune", "Maharashtra"),
        "nagpur": ("Nagpur", "Maharashtra"), "nashik": ("Nashik", "Maharashtra"),
        "thane": ("Thane", "Maharashtra"), "aurangabad": ("Aurangabad", "Maharashtra"),
        "kochi": ("Kochi", "Kerala"), "ernakulam": ("Ernakulam", "Kerala"),
        "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"), "kozhikode": ("Kozhikode", "Kerala"),
        "thrissur": ("Thrissur", "Kerala"), "kollam": ("Kollam", "Kerala"),
        "new delhi": ("New Delhi", "Delhi"), "delhi": ("Delhi", "Delhi"),
        "kolkata": ("Kolkata", "West Bengal"), "howrah": ("Howrah", "West Bengal"),
        "jaipur": ("Jaipur", "Rajasthan"), "jodhpur": ("Jodhpur", "Rajasthan"), "udaipur": ("Udaipur", "Rajasthan"),
        "ahmedabad": ("Ahmedabad", "Gujarat"), "surat": ("Surat", "Gujarat"), "vadodara": ("Vadodara", "Gujarat"),
        "lucknow": ("Lucknow", "Uttar Pradesh"), "kanpur": ("Kanpur", "Uttar Pradesh"),
        "noida": ("Noida", "Uttar Pradesh"), "agra": ("Agra", "Uttar Pradesh"), "varanasi": ("Varanasi", "Uttar Pradesh"),
        "patna": ("Patna", "Bihar"), "gaya": ("Gaya", "Bihar"),
        "bhubaneswar": ("Bhubaneswar", "Odisha"), "cuttack": ("Cuttack", "Odisha"),
        "guwahati": ("Guwahati", "Assam"), "dispur": ("Dispur", "Assam"),
        "bhopal": ("Bhopal", "Madhya Pradesh"), "indore": ("Indore", "Madhya Pradesh"),
        "raipur": ("Raipur", "Chhattisgarh"), "ranchi": ("Ranchi", "Jharkhand"),
        "chandigarh": ("Chandigarh", "Chandigarh"), "dehradun": ("Dehradun", "Uttarakhand"),
        "shimla": ("Shimla", "Himachal Pradesh"), "panaji": ("Panaji", "Goa"),
        "gangtok": ("Gangtok", "Sikkim"), "agartala": ("Agartala", "Tripura"),
        "imphal": ("Imphal", "Manipur"), "aizawl": ("Aizawl", "Mizoram"),
        "kohima": ("Kohima", "Nagaland"), "shillong": ("Shillong", "Meghalaya"),
        "itanagar": ("Itanagar", "Arunachal Pradesh"),
    }

    CATEGORY_MAP = {
        "scheduled caste": "SC", "scheduled tribe": "ST", "other backward class": "OBC", "economically weaker section": "EWS",
        "sc": "SC", "st": "ST", "obc": "OBC", "general": "General", "ews": "EWS",
        "பொது": "General", "सामान्य": "General", "अनुसूचित जाति": "SC", "अनुसूचित जनजाति": "ST", "अन्य पिछड़ा वर्ग": "OBC",
    }

    SECTOR_MAP = {
        "food processing": "Food Processing", "food business": "Food", "restaurant": "Food", "catering": "Food", "bakery": "Food", "food": "Food",
        "tailoring": "Textile", "textile business": "Textile", "textiles": "Textile", "textile": "Textile", "garment": "Textile", "clothing": "Textile",
        "agriculture": "Agriculture", "farming": "Agriculture", "farm": "Agriculture", "agri": "Agriculture",
        "handicrafts": "Handicrafts", "handicraft": "Handicrafts", "artisan": "Handicrafts", "handmade": "Handicrafts",
        "manufacturing": "Manufacturing", "factory": "Manufacturing", "service": "Service", "services": "Service",
        "retail": "Retail", "shop": "Retail", "store": "Retail", "e-shop": "Retail", "e shop": "Retail", "ecommerce": "Retail", "e-commerce": "Retail", "online shop": "Retail", "online store": "Retail", "dairy": "Dairy", "fisheries": "Fisheries", "fishing": "Fisheries",
        "technology": "Technology", "software": "Technology", "it business": "Technology",
        "education": "Education", "healthcare": "Healthcare", "medical": "Healthcare",
        # Tamil
        "உணவு பதப்படுத்துதல்": "Food Processing", "உணவு": "Food", "வேளாண்மை": "Agriculture", "விவசாயம்": "Agriculture", "ஜவுளி": "Textile",
        "தையல்": "Textile", "கைத்தொழில்": "Handicrafts", "கைவினை": "Handicrafts", "சில்லறை": "Retail", "உற்பத்தி": "Manufacturing", "தொழில்நுட்பம்": "Technology",
        # Hindi
        "खाद्य प्रसंस्करण": "Food Processing", "फूड": "Food", "खाद्य": "Food", "रेस्टोरेंट": "Food", "कृषि": "Agriculture", "खेती": "Agriculture",
        "टेक्सटाइल": "Textile", "कपड़ा": "Textile", "सिलाई": "Textile", "हस्तशिल्प": "Handicrafts", "दुकान": "Retail", "निर्माण": "Manufacturing",
        "टेक्नोलॉजी": "Technology", "सॉफ्टवेयर": "Technology",
        # Telugu
        "ఆహారం": "Food", "వ్యవసాయం": "Agriculture", "టెక్స్టైల్": "Textile", "కుట్టు": "Textile", "తయారీ": "Manufacturing", "సాంకేతిక": "Technology",
        # Kannada
        "ಆಹಾರ": "Food", "ಕೃಷಿ": "Agriculture", "ಜವಳಿ": "Textile", "ಹೊಲಿಗೆ": "Textile", "ತಯಾರಿಕೆ": "Manufacturing", "ತಂತ್ರಜ್ಞಾನ": "Technology",
        # Malayalam
        "ഭക്ഷണം": "Food", "കൃഷി": "Agriculture", "ടെക്സ്റ്റൈൽ": "Textile", "തയ്യൽ": "Textile", "നിർമാണം": "Manufacturing", "സാങ്കേതിക": "Technology",
        # Bengali
        "খাদ্য": "Food", "কৃষি": "Agriculture", "টেক্সটাইল": "Textile", "সেলাই": "Textile", "উৎপাদন": "Manufacturing", "প্রযুক্তি": "Technology",
    }

    QUALIFICATION_COURSE_PATTERNS = [
        (r"\b(?:b\.?\s*tech|btech|bachelor\s+of\s+technology)\b", "B.Tech", "Degree", None),
        (r"\b(?:b\.?\s*e\.?|be|bachelor\s+of\s+engineering)\b", "B.E.", "Degree", None),
        (r"\b(?:b\.?\s*sc\.?|bsc|bachelor\s+of\s+science)\b", "B.Sc", "Degree", None),
        (r"\b(?:bca|bachelor\s+of\s+computer\s+applications?)\b", "BCA", "Degree", "Computer Applications"),
        (r"\b(?:b\.?\s*com\.?|bcom|bachelor\s+of\s+commerce)\b", "B.Com", "Degree", "Commerce"),
        (r"\b(?:bba|bachelor\s+of\s+business\s+administration)\b", "BBA", "Degree", "Business Administration"),
        (r"\b(?:b\.?\s*a\.?|bachelor\s+of\s+arts)\b", "B.A.", "Degree", None),
        (r"\b(?:b\.?\s*pharm\.?|bpharm|bachelor\s+of\s+pharmacy)\b", "B.Pharm", "Degree", "Pharmacy"),
        (r"\b(?:b\.?\s*arch\.?|barch|bachelor\s+of\s+architecture)\b", "B.Arch", "Degree", "Architecture"),
        (r"\b(?:llb|bachelor\s+of\s+laws?)\b", "LLB", "Degree", "Law"),
        (r"\b(?:mbbs)\b", "MBBS", "Degree", "Medicine"),

        (r"\b(?:m\.?\s*tech|mtech|master\s+of\s+technology)\b", "M.Tech", "Postgraduate", None),
        (r"\b(?:m\.?\s*e\.?|me|master\s+of\s+engineering)\b", "M.E.", "Postgraduate", None),
        (r"\b(?:m\.?\s*sc\.?|msc|master\s+of\s+science)\b", "M.Sc", "Postgraduate", None),
        (r"\b(?:mca|master\s+of\s+computer\s+applications?)\b", "MCA", "Postgraduate", "Computer Applications"),
        (r"\b(?:mba|master\s+of\s+business\s+administration)\b", "MBA", "Postgraduate", "Business Administration"),
        (r"\b(?:m\.?\s*com\.?|mcom|master\s+of\s+commerce)\b", "M.Com", "Postgraduate", "Commerce"),
        (r"\b(?:m\.?\s*a\.?|master\s+of\s+arts)\b", "M.A.", "Postgraduate", None),
        (r"\b(?:m\.?\s*pharm\.?|mpharm|master\s+of\s+pharmacy)\b", "M.Pharm", "Postgraduate", "Pharmacy"),
        (r"\b(?:ph\.?d|doctorate)\b", "Ph.D", "PhD", None),

        (r"\b(?:diploma|polytechnic)\b", "Diploma", "Diploma", None),
        (r"\b(?:iti|industrial\s+training\s+institute)\b", "ITI", "ITI", None),

        (r"\b(?:12th(?:\s*pass)?|higher\s+secondary|hsc)\b", "12th", "12th Pass", None),
        (r"\b(?:10th(?:\s*pass)?|sslc|secondary\s+school)\b", "10th", "10th Pass", None),
        (r"\b(?:8th(?:\s*pass)?)\b", "8th", "8th Pass", None),
    ]

    EDUCATION_PATTERNS = [
        (r"\b(?:ph\.?d|doctorate)\b", "PhD"),
        (r"\b(?:post\s*graduate|postgraduate|masters?|m\.?tech|m\.?e|m\.?sc|mba|mca|m\.?com)\b", "Postgraduate"),
        (r"\b(?:graduate|graduation|degree|bachelor'?s?|b\.?tech|b\.?e|b\.?sc|bca|b\.?com|bba|b\.?a\.?|b\.?pharm|b\.?arch|llb|mbbs)\b", "Degree"),
        (r"\b(?:12th|higher secondary|hsc)\b", "12th Pass"),
        (r"\b(?:10th|sslc|secondary school)\b", "10th Pass"),
        (r"\b(?:8th)\b", "8th Pass"),
        (r"\bdiploma\b", "Diploma"), (r"\biti\b", "ITI"),
    ]

    EDUCATION_FIELD_PATTERNS = [
        (r"\b(?:computer\s+science(?:\s+and\s+engineering)?|cse)\b", "Computer Science"),
        (r"\b(?:artificial\s+intelligence|ai(?:\s+and\s+ml)?|ai\s*&\s*ml)\b", "Artificial Intelligence"),
        (r"\b(?:computer\s+applications?|bca|mca)\b", "Computer Applications"),
        (r"\b(?:mechanical\s+engineering|mechanical)\b", "Mechanical Engineering"),
        (r"\b(?:electrical\s+(?:and\s+electronics\s+)?engineering|eee)\b", "Electrical Engineering"),
        (r"\b(?:electronics\s+(?:and\s+communication\s+)?engineering|ece)\b", "Electronics and Communication Engineering"),
        (r"\b(?:civil\s+engineering|civil)\b", "Civil Engineering"),
        (r"\b(?:information\s+technology|it)\b", "Information Technology"),
        (r"\b(?:data\s+science)\b", "Data Science"),
        (r"\b(?:cyber\s*security|cybersecurity)\b", "Cyber Security"),
        (r"\b(?:software\s+engineering)\b", "Software Engineering"),
        (r"\b(?:electronics\s+and\s+computer\s+engineering)\b", "Electronics and Computer Engineering"),
        (r"\b(?:electrician)\b", "Electrician"),
        (r"\b(?:economics)\b", "Economics"),
        (r"\b(?:finance)\b", "Finance"),
        (r"\b(?:commerce)\b", "Commerce"),
        (r"\b(?:business\s+administration)\b", "Business Administration"),
    ]

    ARTISAN_TRADES = {
        "pottery": "Pottery", "potter": "Pottery", "weaving": "Weaving", "weaver": "Weaving", "handloom": "Handloom",
        "wood carving": "Wood Carving", "carpentry": "Carpentry", "carpenter": "Carpentry", "embroidery": "Embroidery",
        "basket making": "Basket Making", "leather work": "Leather Work", "jewellery": "Jewellery", "jewelry": "Jewellery",
        "மண்பாண்டம்": "Pottery", "நெசவு": "Weaving", "தச்சு": "Carpentry", "मिट्टी के बर्तन": "Pottery", "बुनाई": "Weaving", "बढ़ई": "Carpentry",
    }

    def extract(self, text):
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        text = text.strip()
        if not text:
            return {}

        profile = {}
        extractors = [
            ("age", self._extract_age), ("gender", self._extract_gender), ("state", self._extract_state), ("district", self._extract_district),
            ("education_course", self._extract_education_course), ("education", self._extract_education), ("education_field", self._extract_education_field), ("category", self._extract_category), ("sector", self._extract_sector),
            ("business_type", self._extract_business_type), ("income", self._extract_income), ("project_cost", self._extract_project_cost),
            ("available_capital", self._extract_available_capital), ("artisan_trade", self._extract_artisan_trade),
            ("is_new_unit", self._extract_is_new_unit), ("prior_gov_subsidy", self._extract_prior_gov_subsidy),
            ("family_pmegp_availed", self._extract_family_pmegp_availed),
        ]
        for field, fn in extractors:
            value = fn(text)
            if value is not None:
                profile[field] = value

        if "business_type" in profile:
            profile["business_stage"] = profile["business_type"]
            profile["new_business"] = profile["business_type"] in ["Startup", "Idea"]
            if profile.get("is_new_unit") is None and profile["business_type"] in ["Startup", "Idea"]:
                profile["is_new_unit"] = True

        # Extract explicit negative registration evidence
        lower = text.lower()
        missing_regs = []
        if re.search(r"\b(?:don't|do not|don’t|does not|without|no|not have|have not)\b.*?\budyam\b", lower) or ("udyam" in lower and ("don't have" in lower or "not registered" in lower or "no udyam" in lower)):
            missing_regs.append("UDYAM")
        if re.search(r"\b(?:don't|do not|don’t|does not|without|no|not have|have not)\b.*?\bfssai\b", lower) or ("fssai" in lower and ("don't have" in lower or "no fssai" in lower)):
            missing_regs.append("FSSAI")
        if missing_regs:
            profile["missing_registrations"] = missing_regs

        if re.search(r"\bhave not registered my business\b|\bnot registered my business\b|\bunregistered business\b|\bnot registered yet\b", lower):
            profile["unregistered_business"] = True

        period = self._extract_income_period(text) if "income" in profile else None
        if period:
            profile["income_period"] = period

        goal = self.support.infer_business_goal(text)
        if goal:
            profile["business_goal"] = goal

        support_needs = self.support.infer(text)
        if support_needs:
            profile["support_needs"] = support_needs

        return profile

    # ------------------------- AGE -------------------------
    def _extract_age(self, text):
        lower = text.lower()
        self_patterns = [
            r"\b(?:i am|i'm|im)\s+(?:a\s+)?(?:actually\s+)?(\d{1,3})\b",
            r"\bmy age\s*(?:is|:)?\s*(\d{1,3})\b", r"\bage\W*(\d{1,3})\b",
            r"\bmeri (?:age|umar|umr)\s*(?:is|hai|:)?\s*(\d{1,3})\b",
            r"\bmain\s+(\d{1,3})\s+saal\s+(?:ka|ki)\b",
            r"मैं\s+(\d{1,3})\s+साल\s+(?:का|की)\s+(?:हूँ|हूं|है)",
            r"\b(?:enakku|enaku)\s+(\d{1,3})\s+(?:vayasu|vaysu|vayas)\b",
            r"எனக்கு\s+(\d{1,3})\s+வய(?:து|சு)", r"मेरी उम्र\s*(?:है\s*)?(\d{1,3})",
            r"నా వయస్సు\s*(\d{1,3})", r"ನನ್ನ ವಯಸ್ಸು\s*(\d{1,3})", r"എന്റെ വയസ്സ്\s*(\d{1,3})", r"আমার বয়স\s*(\d{1,3})",
        ]
        for p in self_patterns:
            m = re.search(p, lower if p.isascii() else text, re.IGNORECASE if p.isascii() else 0)
            if m:
                return int(m.group(1))

        # Generic "24 years old" / "24-year-old" / "24 year old"
        m = re.search(r"\b(\d{1,3})[- ]years?[- ]old\b", lower)
        if m:
            prefix = lower[max(0, m.start() - 35):m.start()]
            if not re.search(r"\b(?:father|mother|dad|mom|brother|sister|friend|husband|wife|son|daughter)\b", prefix):
                return int(m.group(1))
        return None

    # ------------------------- GENDER -------------------------
    def _extract_gender(self, text):
        lower = text.lower()
        # Prefer explicit self-identification and ignore negated mentions.
        patterns = [
            (r"\bi am\s+(?:a\s+)?(male|female|man|woman|boy|girl)\b", None),
            (r"\bmy gender\s*(?:is|:)?\s*(male|female)\b", None),
            (r"\b(?:main|mai)\s+(purush|mahila|aadmi|aurat|ladka|ladki)\b", None),
        ]
        for p, _ in patterns:
            for m in re.finditer(p, lower):
                before = lower[max(0, m.start() - 6):m.start()]
                if "not " in before:
                    continue
                token = m.group(1)
                roman = {"purush": "Male", "aadmi": "Male", "ladka": "Male", "mahila": "Female", "aurat": "Female", "ladki": "Female"}
                return roman.get(token, self.GENDER_MAP.get(token))

        # In "not female, I am male", the first direct map item must not win.
        candidates = []
        for key in sorted(self.GENDER_MAP, key=len, reverse=True):
            if key.isascii():
                for m in re.finditer(rf"(?<!\w){re.escape(key)}(?!\w)", lower):
                    prefix = lower[max(0, m.start() - 8):m.start()]
                    if re.search(r"\bnot\s*$", prefix):
                        continue
                    candidates.append((m.start(), self.GENDER_MAP[key]))
            elif key in text:
                candidates.append((text.find(key), self.GENDER_MAP[key]))
        if candidates:
            # Later positive correction usually supersedes earlier negated/quoted mention.
            return sorted(candidates, key=lambda x: x[0])[-1][1]
        return None

    # ------------------------- STATE -------------------------
    def _location_is_third_party(self, lower, start_index):
        prefix = lower[max(0, start_index - 55):start_index]
        return bool(re.search(
            r"\b(?:my\s+)?(?:friend|father|mother|dad|mom|brother|sister|husband|wife|son|daughter)\b[^.!?]{0,35}\b(?:live|lives|stay|stays|from|in)\s*$",
            prefix,
        ))

    def _extract_self_city(self, text):
        lower = text.lower()
        # 1. Check india_locations lookup dictionary
        if self.india_locations:
            ambiguous_map = self.india_locations.get("ambiguous_locations", {})
            for city_key, data in self.india_locations.items():
                if city_key == "ambiguous_locations" or not isinstance(data, dict):
                    continue
                for m in re.finditer(rf"(?<!\w){re.escape(city_key)}(?!\w)", lower):
                    if self._location_is_third_party(lower, m.start()):
                        continue
                    district = data.get("district")
                    state = data.get("state")
                    return (district, state)

            for amb_key, possible_states in ambiguous_map.items():
                for m in re.finditer(rf"(?<!\w){re.escape(amb_key)}(?!\w)", lower):
                    if self._location_is_third_party(lower, m.start()):
                        continue
                    explicit_state = None
                    for st in possible_states:
                        if st.lower() in lower:
                            explicit_state = st
                            break
                    return (amb_key.capitalize(), explicit_state)

        # Fallback to CITY_STATE_MAP
        patterns = [
            r"\b(?:i\s+live\s+in|i\s+am\s+from|i'm\s+from|im\s+from|i\s+stay\s+in|i\s+reside\s+in)\s+([a-z ]{2,35})",
            r"\bi\s+am[^.!?]{0,25}\s+from\s+([a-z ]{2,35})",
        ]
        for p in patterns:
            for m in re.finditer(p, lower):
                fragment = m.group(1).strip()
                for city_key in sorted(self.CITY_STATE_MAP, key=len, reverse=True):
                    if re.search(rf"(?<!\w){re.escape(city_key)}(?!\w)", fragment):
                        return self.CITY_STATE_MAP[city_key]
        for city_key in sorted(self.CITY_STATE_MAP, key=len, reverse=True):
            for m in re.finditer(rf"(?<!\w){re.escape(city_key)}(?!\w)", lower):
                if self._location_is_third_party(lower, m.start()):
                    continue
                prefix = lower[max(0, m.start() - 30):m.start()]
                if re.search(r"\b(?:live|stay|reside|located|based)\s+in\s*$", prefix) or len(text.split()) <= 4:
                    return self.CITY_STATE_MAP[city_key]
        return None

    def _extract_state(self, text):
        lower = text.lower()
        city = self._extract_self_city(text)
        if city and city[1]:
            return city[1]

        # Self-location patterns beat mentions about friends/family.
        self_patterns = [
            r"\b(?:i live in|i am from|i'm from|im from)\s+([a-z ]{2,30})",
            r"\bi\s+am[^.!?]{0,25}\s+from\s+([a-z ]{2,30})",
            r"\b(?:enakku|naan|na)\b.*?\b(tamil nadu|kerala|karnataka|telangana)\b",
            r"\b(?:main|mai)\b.*?\b(tamil nadu|kerala|karnataka|telangana|maharashtra|delhi)\b",
        ]
        for p in self_patterns:
            m = re.search(p, lower)
            if m:
                fragment = m.group(1).strip()
                for key in sorted(self.STATE_MAP, key=len, reverse=True):
                    if key.isascii() and re.search(rf"(?<!\w){re.escape(key)}(?!\w)", fragment):
                        return self.STATE_MAP[key]

        occurrences = []
        for key in sorted(self.STATE_MAP, key=len, reverse=True):
            if key.isascii():
                for m in re.finditer(rf"(?<!\w){re.escape(key)}(?!\w)", lower):
                    prefix = lower[max(0, m.start() - 35):m.start()]
                    if re.search(r"(?:don't|do not|not)\s+(?:live|stay|reside)?\s*(?:in)?\s*$", prefix):
                        continue
                    if re.search(r"\b(?:friend|father|mother|brother|sister|husband|wife|son|daughter)\b.*(?:live|lives|stay|stays|(?:is\s+)?from)\s+(?:in\s+)?$", prefix):
                        continue
                    occurrences.append((m.start(), self.STATE_MAP[key]))
            elif key in text:
                occurrences.append((text.find(key), self.STATE_MAP[key]))
        return sorted(occurrences, key=lambda x: x[0])[-1][1] if occurrences else None

    def _extract_district(self, text):
        city = self._extract_self_city(text)
        return city[0] if city else None

    # ------------------------- EDUCATION -------------------------
    def _extract_education_course(self, text):
        lower = text.lower()
        for p, course_name, level, default_field in self.QUALIFICATION_COURSE_PATTERNS:
            if re.search(p, lower):
                return course_name
        return None

    def _extract_education(self, text):
        lower = text.lower()
        # 1. Check qualification patterns
        for p, course_name, level, default_field in self.QUALIFICATION_COURSE_PATTERNS:
            if re.search(p, lower):
                return level
        # 2. Check general education level patterns
        for p, value in self.EDUCATION_PATTERNS:
            if re.search(p, lower):
                return value
        lex = {
            "degree mudich": "Degree", "degree mudichiten": "Degree", "padichu mudich": "Degree",
            "பட்டம்": "Degree", "முதுகலை": "Postgraduate", "டிப்ளோமா": "Diploma",
            "स्नातकोत्तर": "Postgraduate", "स्नातक": "Degree", "डिग्री": "Degree", "डिप्लोमा": "Diploma", "बारहवीं": "12th Pass", "दसवीं": "10th Pass",
            "డిగ్రీ": "Degree", "డిప్లొమా": "Diploma", "పదో తరగతి": "10th Pass", "ఇంటర్": "12th Pass",
            "ಪದವಿ": "Degree", "ಡಿಪ್ಲೊಮಾ": "Diploma", "പഠനം": "School", "ഡിഗ്രി": "Degree", "ഡിപ്ലോമ": "Diploma", "ডিগ্রি": "Degree", "ডিপ্লোমা": "Diploma",
        }
        for key, value in lex.items():
            if key in (lower if key.isascii() else text):
                return value

        # CRITICAL AMBIGUITY RULE:
        # If user ONLY mentioned a field/subject (e.g. "computer science", "artificial intelligence") without specifying a qualification, return None (UNKNOWN).
        return None

    def _extract_education_field(self, text):
        lower = text.lower()
        # 1. Check if course implies field (e.g. BCA -> Computer Applications)
        for p, course_name, level, default_field in self.QUALIFICATION_COURSE_PATTERNS:
            if default_field and re.search(p, lower):
                for f_pattern, f_value in self.EDUCATION_FIELD_PATTERNS:
                    if re.search(f_pattern, lower):
                        return f_value
                return default_field
        # 2. Check explicit field patterns
        for pattern, value in self.EDUCATION_FIELD_PATTERNS:
            if re.search(pattern, lower):
                return value
        return None

    # ------------------------- CATEGORY -------------------------
    def _extract_category(self, text):
        lower = text.lower()
        occurrences = []
        for key in sorted(self.CATEGORY_MAP, key=len, reverse=True):
            if key.isascii():
                for m in re.finditer(rf"(?<!\w){re.escape(key)}(?!\w)", lower):
                    prefix = lower[max(0, m.start() - 8):m.start()]
                    if re.search(r"\bnot\s*$", prefix):
                        continue
                    occurrences.append((m.start(), self.CATEGORY_MAP[key]))
            elif key in text:
                occurrences.append((text.find(key), self.CATEGORY_MAP[key]))
        return sorted(occurrences, key=lambda x: x[0])[-1][1] if occurrences else None

    # ------------------------- SECTOR -------------------------
    def _extract_sector(self, text):
        lower = text.lower()
        # A course/degree field is not automatically the user's business sector.
        if self._extract_education_course(text) and not re.search(
            r"\b(?:business|enterprise|startup|start|launch|run|running|sector|industry|shop|store|farm|farming|manufactur|export|service|restaurant|bakery|tailor|handicraft|make|sell|open)\b",
            lower,
        ):
            return None

        # Strip education qualification/course terms so degree words like 'b.tech' do not trigger business classification
        business_text = re.sub(
            r"\b(?:b\.?\s*tech|m\.?\s*tech|btech|mtech|b\.?\s*e\.?|b\.?\s*sc\.?|bsc|bca|mca|mba|bcom|bba|diploma|polytechnic|iti|ph\.?d)\b",
            "",
            lower,
            flags=re.IGNORECASE,
        )

        # Exact non-overclassifying activity mappings
        if re.search(r"\bbakery\b|\bbake\b", lower):
            return "Food Processing & Agri Value Addition"
        if re.search(r"\bdairy\b|\bdairy\s+farming\b", lower):
            return "Agriculture & Allied"
        if re.search(r"\bpaper\s+bag\b|\bpaper\s+bags\b", lower):
            return "MSME & Manufacturing"
        if re.search(r"\bpottery\b|\bpotter\b", lower):
            return "Handicrafts, Handloom & Artisan Economy"
        if re.search(r"\bexport\s+spices?\b|\bspice\s+export\b", lower):
            return "Export, Market Access & Business Growth"
        if re.search(r"\be-?shop\b|\bonline\s+shop\b|\bonline\s+clothing\b|\bonline\s+store\b|\be-?commerce\b", lower):
            if re.search(r"\b(?:tech|ai|deeptech|patent|innovation|incubate|startup)\b", business_text):
                return "Startup & Innovation"
            return "MSME & Manufacturing"

        aliases = {
            "saapadu business": "Food", "hotel business": "Food", "vivasayam": "Agriculture", "vivasaayam": "Agriculture",
            "thuni business": "Textile", "tailoring business": "Textile",
        }
        for key, value in aliases.items():
            if key in lower:
                return value
        for key in sorted(self.SECTOR_MAP, key=len, reverse=True):
            if key.isascii():
                if re.search(rf"(?<!\w){re.escape(key)}(?!\w)", business_text):
                    return self.SECTOR_MAP[key]
            elif key in text:
                return self.SECTOR_MAP[key]
        return None

    # ------------------------- BUSINESS TYPE -------------------------
    def _extract_business_type(self, text):
        lower = text.lower()
        existing = [
            r"\bexisting(?:\s+\w+){0,3}\s+business\b", r"\brunning(?:\s+\w+){0,3}\s+business\b", r"\bestablished(?:\s+\w+){0,3}\s+business\b",
            r"\balready\s+(?:have|own|run|running)\b", r"\bi currently (?:operate|run|own|have)\b", r"\bcurrently (?:operating|operate|running|run)\b",
            r"\bpehle se .*business\b", r"\balready .*business .*hai\b", r"\balready .*business (?:run|running) pan(?:ren|rேன்)?\b",
            r"\bbusiness\s+run\s+panren\b",
        ]
        if any(re.search(p, lower) for p in existing):
            return "Existing"
        native_existing = ["ஏற்கனவே", "पहले से", "ఇప్పటికే", "ಈಗಾಗಲೇ", "ഇതിനകം", "ইতিমধ্যে"]
        if any(x in text for x in native_existing) and self._extract_sector(text):
            return "Existing"

        startup_explicit = [
            r"\bmy startup\b", r"\bour startup\b", r"\bregistered startup\b", r"\boperating startup\b",
            r"\bnew enterprise\b",
        ]
        if any(re.search(p, lower) for p in startup_explicit):
            return "Startup"

        idea_start = [
            r"\b(?:want|wants|planning|plan|going|intend(?:ing)?|wish(?:es)?|thinking)\s+to\s+(?:start|build|open|launch|create|set\s+up)\b",
            r"\bstart(?:ing)?\s+(?:a\s+|my\s+)?business\b", r"\bwant\s+a\s+business\b",
            r"\bbusiness\s+(?:shuru|start)\s+(?:karna|krna)\b", r"\b(?:shuru|start)\s+karna\s+hai\b",
            r"\bbusiness\s+start\s+pan", r"\bstart\s+(?:panna|panra|panren|poren)\b",
            r"\bunregistered\b", r"\bnot registered\b", r"\bhave not registered\b",
            r"\bidea\b", r"\bconcept\b", r"\bstartup\b", r"\bstart\s*up\b", r"\bnew business\b",
        ]
        if any(re.search(p, lower) for p in idea_start):
            return "Idea"

        native_start = ["தொழில் தொடங்க", "வணிகம் தொடங்க", "வியாபாரம் தொடங்க", "व्यवसाय शुरू", "बिजनेस शुरू", "వ్యాపారం ప్రారంభ", "వ్యాపారం మొదలు", "ವ್ಯವಹಾರ ಆರಂಭ", "ಬಿಸಿನೆಸ್ ಆರಂಭ", "ബിസിനസ് തുടങ്ങ", "ব্যবসা শুরু"]
        if any(x in text for x in native_start):
            return "Idea"
        return None

    # ------------------------- MONEY -------------------------
    def _amount_after_context(self, text, patterns):
        lower = text.lower()
        amount_expr = r"(?:₹|rs\.?|inr|रु\.?)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(k|thousand|thousands|l|lac|lacs|lakh|lakhs|cr|crore|crores)?(?:\s*/-)?"
        for prefix, suffix in patterns:
            p = prefix + amount_expr + suffix
            m = re.search(p, lower, re.IGNORECASE)
            if m:
                raw = f"{m.group(1)}{m.group(2) or ''}"
                parsed = self.money.parse_first(raw, allow_bare=True)
                if parsed:
                    return parsed.amount
        return None

    def _extract_income(self, text):
        patterns = [
            (r"\b(?:my\s+)?(?:monthly\s+|annual\s+|yearly\s+)?(?:income|salary|earnings?)\s*(?:is|are|:)?\s*", r""),
            (r"\b(?:meri|mera)\s+(?:monthly\s+|annual\s+)?(?:income|salary)\s*(?:is|hai|:)?\s*", r""),
            (r"(?:மாத|ஆண்டு)?\s*வருமானம்\s*(?:என்பது|:)?\s*", r""),
            (r"(?:मासिक|वार्षिक)?\s*(?:आय|आमदनी|वेतन)\s*(?:है|:)?\s*", r""),
        ]
        return self._amount_after_context(text, patterns)

    def _extract_income_period(self, text):
        return self.money.detect_period(text)

    def _extract_project_cost(self, text):
        patterns = [
            (r"\b(?:my\s+)?(?:project|business)\s+(?:will\s+)?(?:cost|budget)\s*(?:is|will be|:)?\s*", r""),
            (r"\b(?:project|business)\s+(?:cost|budget)\s*(?:is|:)?\s*", r""),
            (r"\bbudget\s*(?:is|:)?\s*", r""),
            (r"\bi\s+need\s+", r"\s+(?:for|to fund)\s+(?:the\s+|my\s+)?(?:project|business)\b"),
            (r"\b(?:mera|meri)\s+(?:project|business)\s+(?:ka\s+)?(?:cost|budget)\s*(?:hai|is|:)?\s*", r""),
            (r"\b(?:project|business)\s+ku\s+", r"\s+venum\b"),
            (r"\b(?:business|project)\s+ku\s+", r""),
        ]
        return self._amount_after_context(text, patterns)

    def _extract_available_capital(self, text):
        patterns = [
            (r"\b(?:my own capital is|available capital is|own money is|i have saved|i can invest)\s*(?:around|approx|approximately|about)?\s*", r""),
            (r"\b(?:capital|own contribution)\s*(?:is|:)?\s*", r""),
        ]
        val = self._amount_after_context(text, patterns)
        if val is not None:
            return val

        lower = text.lower()
        amount_expr = r"(?:₹|rs\.?|inr|रु\.?)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(k|thousand|thousands|l|lac|lacs|lakh|lakhs|cr|crore|crores)?(?:\s*/-)?"
        suffix_pattern = amount_expr + r"\s+(?:available capital|of my own money|as own capital|own money|as own contribution|from my savings|of my savings|capital)\b"
        m = re.search(suffix_pattern, lower)
        if m:
            raw = f"{m.group(1)}{m.group(2) or ''}"
            parsed = self.money.parse_first(raw, allow_bare=True)
            if parsed:
                return parsed.amount

        prefix_pattern = r"\b(?:i have|have|saved|capital of|own capital of)\s+" + amount_expr + r"\s+(?:available capital|available|capital)\b"
        m2 = re.search(prefix_pattern, lower)
        if m2:
            raw = f"{m2.group(1)}{m2.group(2) or ''}"
            parsed = self.money.parse_first(raw, allow_bare=True)
            if parsed:
                return parsed.amount

        return None

    def _extract_is_new_unit(self, text):
        lower = text.lower()
        if re.search(r"\b(?:this is a new unit|new unit|setting up a new unit|fresh unit|new micro[- ]enterprise|new project)\b", lower) or re.search(r"\bwant to start a new\b", lower):
            return True
        if re.search(r"\b(?:this is an existing unit|existing unit|already running unit|running unit|existing enterprise|existing business)\b", lower):
            return False
        return None

    def _extract_prior_gov_subsidy(self, text):
        lower = text.lower()
        if re.search(r"\b(?:have not received|not received|no|never received)\b.*?\b(?:previous|prior|any)?\s*(?:government\s+)?subsidy\b", lower) or re.search(r"\bno previous government subsidy\b|\bhave not received any previous government subsidy\b", lower):
            return False
        if re.search(r"\b(?:previously received|already received|got|have received|availed)\b.*?\b(?:government\s+)?subsidy\b", lower):
            return True
        return None

    def _extract_family_pmegp_availed(self, text):
        lower = text.lower()
        if re.search(r"\b(?:neither i nor my spouse|nobody in my family|no one in my family|neither me nor my spouse|have not|never|no)\b.*?\b(?:availed|received|taken)?\s*pmegp\b", lower) or "neither i nor my spouse has already availed pmegp" in lower:
            return False
        if re.search(r"\b(?:my spouse|family member|spouse|i or my spouse)\b.*?\b(?:already\s+)?(?:availed|received|taken)\s+pmegp\b", lower) or re.search(r"\balready availed pmegp\b", lower):
            return True
        return None

    # ------------------------- ARTISAN -------------------------
    def _extract_artisan_trade(self, text):
        lower = text.lower()
        for key, value in sorted(self.ARTISAN_TRADES.items(), key=lambda x: len(x[0]), reverse=True):
            if key.isascii():
                if re.search(rf"(?<!\w){re.escape(key)}(?!\w)", lower):
                    return value
            elif key in text:
                return value
        return None
