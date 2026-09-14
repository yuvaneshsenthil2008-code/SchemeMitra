import re


class Normalizer:
    """Normalize extracted values into the canonical M3 vocabulary."""

    STATE_MAP = {
        "tn": "Tamil Nadu", "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu",
        "kerala": "Kerala", "karnataka": "Karnataka", "andhra pradesh": "Andhra Pradesh",
        "ap": "Andhra Pradesh", "telangana": "Telangana", "maharashtra": "Maharashtra",
        "delhi": "Delhi", "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh",
        "west bengal": "West Bengal", "bihar": "Bihar", "odisha": "Odisha", "orissa": "Odisha",
        "rajasthan": "Rajasthan", "gujarat": "Gujarat", "punjab": "Punjab", "haryana": "Haryana",
        "assam": "Assam", "jharkhand": "Jharkhand", "chhattisgarh": "Chhattisgarh",
        "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh", "goa": "Goa",
        "uttarakhand": "Uttarakhand", "himachal pradesh": "Himachal Pradesh",
        "sikkim": "Sikkim", "tripura": "Tripura", "manipur": "Manipur", "mizoram": "Mizoram",
        "nagaland": "Nagaland", "meghalaya": "Meghalaya", "arunachal pradesh": "Arunachal Pradesh",
        # Native aliases frequently encountered in the supported languages.
        "தமிழ்நாடு": "Tamil Nadu", "தமிழ்நாட்டில்": "Tamil Nadu", "கேரளா": "Kerala",
        "கர்நாடகா": "Karnataka", "ஆந்திர பிரதேசம்": "Andhra Pradesh", "தெலங்கானா": "Telangana",
        "तमिलनाडु": "Tamil Nadu", "तमिल नाडु": "Tamil Nadu", "केरल": "Kerala", "कर्नाटक": "Karnataka",
        "महाराष्ट्र": "Maharashtra", "उत्तर प्रदेश": "Uttar Pradesh", "पश्चिम बंगाल": "West Bengal",
        "తమిళనాడు": "Tamil Nadu", "తెలంగాణ": "Telangana", "ఆంధ్ర ప్రదేశ్": "Andhra Pradesh",
        "కర్ణాటక": "Karnataka", "కేరళ": "Kerala",
        "ತಮಿಳುನಾಡು": "Tamil Nadu", "ಕರ್ನಾಟಕ": "Karnataka", "ಕೇರಳ": "Kerala", "ತೆಲಂಗಾಣ": "Telangana",
        "തമിഴ്നാട്": "Tamil Nadu", "കേരളം": "Kerala", "കർണാടക": "Karnataka", "തെലങ്കാന": "Telangana",
        "তামিলনাড়ু": "Tamil Nadu", "পশ্চিমবঙ্গ": "West Bengal", "কেরল": "Kerala", "কর্ণাটক": "Karnataka",
    }

    NORMALIZATION_MAP = {
        "gender": {
            "male": "Male", "man": "Male", "boy": "Male", "m": "Male",
            "female": "Female", "woman": "Female", "girl": "Female", "f": "Female",
            "other": "Other", "non-binary": "Other", "nonbinary": "Other",
            "transgender": "Transgender", "trans": "Transgender", "transman": "Transgender", "transwoman": "Transgender",
            "third gender": "Transgender", "thirunangai": "Transgender", "thirunambi": "Transgender", "aravani": "Transgender", "kinnar": "Transgender", "hijra": "Transgender",
            "aan": "Male", "aambala": "Male", "ponnu": "Female", "pen": "Female",
            "ஆண்": "Male", "பெண்": "Female", "पुरुष": "Male", "महिला": "Female",
            "మగ": "Male", "పురుషుడు": "Male", "ఆడ": "Female", "మహిళ": "Female",
            "ಪುರುಷ": "Male", "ಗಂಡು": "Male", "ಮಹಿಳೆ": "Female", "ಹೆಣ್ಣು": "Female",
            "പുരുഷൻ": "Male", "ആൺ": "Male", "സ്ത്രീ": "Female", "പെൺ": "Female",
            "পুরুষ": "Male", "মহিলা": "Female",
        },
        "education": {
            "8th": "8th Pass", "8th pass": "8th Pass", "8th_pass": "8th Pass",
            "10th": "10th Pass", "10th pass": "10th Pass", "10th_pass": "10th Pass", "sslc": "10th Pass",
            "12th": "12th Pass", "12th pass": "12th Pass", "12th_pass": "12th Pass", "hsc": "12th Pass", "higher secondary": "12th Pass",
            "diploma": "Diploma", "iti": "ITI",
            "degree": "Degree", "graduate": "Degree", "graduated": "Degree", "graduation": "Degree",
            "bachelor": "Degree", "bachelors": "Degree", "b.tech": "Degree", "btech": "Degree", "b.e": "Degree", "bsc": "Degree", "b.sc": "Degree", "bca": "Degree", "b.com": "Degree",
            "postgraduate": "Postgraduate", "post graduate": "Postgraduate", "master": "Postgraduate", "masters": "Postgraduate", "m.tech": "Postgraduate", "mtech": "Postgraduate", "mca": "Postgraduate", "mba": "Postgraduate",
            "phd": "PhD", "doctorate": "PhD",
            "பட்டம்": "Degree", "முதுகலை": "Postgraduate", "டிப்ளோமா": "Diploma",
            "டிப்ளோம்": "Diploma",
            "டிப்ளோமா": "Diploma",
            "डिग्री": "Degree", "स्नातक": "Degree", "स्नातकोत्तर": "Postgraduate", "डिप्लोमा": "Diploma",
            "డిగ్రీ": "Degree", "డిప్లొమా": "Diploma",
            "ಪದವಿ": "Degree", "ಡಿಪ್ಲೊಮಾ": "Diploma",
            "ഡിഗ്രി": "Degree", "ഡിപ്ലോമ": "Diploma",
            "ഡിഗ്രി": "Degree", "ഡിപ്ലോമ": "Diploma",
            "ডিগ্রি": "Degree", "ডিপ্লোমা": "Diploma",
        },
        "education_course": {
            "btech": "B.Tech", "b.tech": "B.Tech", "bachelor of technology": "B.Tech",
            "be": "B.E.", "b.e": "B.E.", "b.e.": "B.E.", "bachelor of engineering": "B.E.",
            "bsc": "B.Sc", "b.sc": "B.Sc", "bachelor of science": "B.Sc",
            "bca": "BCA", "bachelor of computer applications": "BCA",
            "bcom": "B.Com", "b.com": "B.Com", "bachelor of commerce": "B.Com",
            "bba": "BBA", "bachelor of business administration": "BBA",
            "ba": "B.A.", "b.a": "B.A.", "b.a.": "B.A.", "bachelor of arts": "B.A.",
            "bpharm": "B.Pharm", "b.pharm": "B.Pharm", "bachelor of pharmacy": "B.Pharm",
            "barch": "B.Arch", "b.arch": "B.Arch", "bachelor of architecture": "B.Arch",
            "llb": "LLB", "bachelor of laws": "LLB", "mbbs": "MBBS",
            "mtech": "M.Tech", "m.tech": "M.Tech", "master of technology": "M.Tech",
            "me": "M.E.", "m.e": "M.E.", "m.e.": "M.E.", "master of engineering": "M.E.",
            "msc": "M.Sc", "m.sc": "M.Sc", "master of science": "M.Sc",
            "mca": "MCA", "master of computer applications": "MCA",
            "mba": "MBA", "master of business administration": "MBA",
            "mcom": "M.Com", "m.com": "M.Com", "master of commerce": "M.Com",
            "ma": "M.A.", "m.a": "M.A.", "m.a.": "M.A.", "master of arts": "M.A.",
            "mpharm": "M.Pharm", "m.pharm": "M.Pharm", "master of pharmacy": "M.Pharm",
            "phd": "Ph.D", "ph.d": "Ph.D", "doctorate": "Ph.D",
            "diploma": "Diploma", "polytechnic": "Diploma",
            "iti": "ITI", "12th": "12th", "10th": "10th", "8th": "8th"
        },
        "education_field": {
            "cse": "Computer Science", "computer science": "Computer Science", "computer science and engineering": "Computer Science",
            "ai": "Artificial Intelligence", "artificial intelligence": "Artificial Intelligence",
            "computer applications": "Computer Applications", "bca": "Computer Applications", "mca": "Computer Applications",
            "mechanical": "Mechanical Engineering", "mechanical engineering": "Mechanical Engineering",
            "electrical engineering": "Electrical Engineering", "eee": "Electrical Engineering",
            "electronics and communication engineering": "Electronics and Communication Engineering", "ece": "Electronics and Communication Engineering",
            "civil": "Civil Engineering", "civil engineering": "Civil Engineering",
            "information technology": "Information Technology", "data science": "Data Science", "cyber security": "Cyber Security", "cybersecurity": "Cyber Security", "software engineering": "Software Engineering", "electrician": "Electrician",
        },
        "category": {
            "sc": "SC", "scheduled caste": "SC", "st": "ST", "scheduled tribe": "ST",
            "obc": "OBC", "other backward class": "OBC", "general": "General", "ews": "EWS",
            "economically weaker section": "EWS", "பொது": "General", "सामान्य": "General",
        },
        "sector": {
            "food": "Food Processing & Agri Value Addition",
            "food processing": "Food Processing & Agri Value Addition",
            "food business": "Food Processing & Agri Value Addition",
            "restaurant": "Food Processing & Agri Value Addition",
            "catering": "Food Processing & Agri Value Addition",
            "bakery": "Food Processing & Agri Value Addition",
            "food processing & agri value addition": "Food Processing & Agri Value Addition",
            "agriculture": "Agriculture & Allied",
            "farming": "Agriculture & Allied",
            "agri": "Agriculture & Allied",
            "agriculture & allied": "Agriculture & Allied",
            "msme": "MSME & Manufacturing",
            "manufacturing": "MSME & Manufacturing",
            "msme & manufacturing": "MSME & Manufacturing",
            "finance": "Finance & Credit",
            "credit": "Finance & Credit",
            "finance & credit": "Finance & Credit",
            "startup": "Startup & Innovation",
            "innovation": "Startup & Innovation",
            "startup & innovation": "Startup & Innovation",
            "skills": "Skills & Employment",
            "employment": "Skills & Employment",
            "skills & employment": "Skills & Employment",
            "women": "Women & SHG Entrepreneurship",
            "shg": "Women & SHG Entrepreneurship",
            "women & shg entrepreneurship": "Women & SHG Entrepreneurship",
            "social": "Social Empowerment & Inclusive Entrepreneurship",
            "social empowerment": "Social Empowerment & Inclusive Entrepreneurship",
            "social empowerment & inclusive entrepreneurship": "Social Empowerment & Inclusive Entrepreneurship",
            "handicraft": "Handicrafts, Handloom & Artisan Economy",
            "handicrafts": "Handicrafts, Handloom & Artisan Economy",
            "handloom": "Handicrafts, Handloom & Artisan Economy",
            "artisan": "Handicrafts, Handloom & Artisan Economy",
            "handicrafts, handloom & artisan economy": "Handicrafts, Handloom & Artisan Economy",
            "export": "Export, Market Access & Business Growth",
            "market access": "Export, Market Access & Business Growth",
            "export, market access & business growth": "Export, Market Access & Business Growth",
            "textile": "MSME & Manufacturing",
            "textiles": "MSME & Manufacturing",
            "dairy": "Agriculture & Allied",
            "fisheries": "Agriculture & Allied",
            "fishing": "Agriculture & Allied",
            "retail": "MSME & Manufacturing", "shop": "MSME & Manufacturing", "e-shop": "MSME & Manufacturing", "e shop": "MSME & Manufacturing", "ecommerce": "MSME & Manufacturing", "e-commerce": "MSME & Manufacturing", "online shop": "MSME & Manufacturing", "online store": "MSME & Manufacturing",
        },
        "business_type": {
            "idea": "Idea", "planning": "Idea", "concept": "Idea",
            "startup": "Startup", "start-up": "Startup", "new business": "Startup", "new enterprise": "Startup",
            "existing": "Existing", "existing business": "Existing", "existing enterprise": "Existing", "running business": "Existing",
        },
        "business_goal": {
            "start_business": "START_BUSINESS", "start business": "START_BUSINESS", "START_BUSINESS": "START_BUSINESS",
            "grow_business": "GROW_BUSINESS", "grow business": "GROW_BUSINESS", "GROW_BUSINESS": "GROW_BUSINESS",
        },
    }

    def normalize_value(self, field, value):
        if value is None:
            return None
        if field in {"preferred_support_types", "support_needs"} and isinstance(value, (list, tuple, set)):
            return [str(v).strip().upper() for v in value if str(v).strip()]
        if not isinstance(value, str):
            return value
        cleaned = re.sub(r"\s+", " ", value.strip())
        lower = cleaned.lower()
        if field == "state":
            return self.STATE_MAP.get(lower, self.STATE_MAP.get(cleaned, value))
        mapping = self.NORMALIZATION_MAP.get(field, {})
        return mapping.get(lower, mapping.get(cleaned, value))

    def normalize_profile(self, profile):
        if not isinstance(profile, dict):
            raise TypeError("Profile must be a dictionary.")
        normalized = {}
        for field, value in profile.items():
            normalized[field] = self.normalize_value(field, value)
        return normalized
