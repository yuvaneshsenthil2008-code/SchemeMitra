import re


class SupportInference:
    """Infer support *needs* from explicit natural-language evidence.

    This module never sets preferred_support_types. Preferences are explicit UI
    choices and are supplied separately by the user/frontend.
    """

    SUPPORT_TYPES = {
        "LOAN", "SUBSIDY", "INTEREST_SUBVENTION", "CREDIT_GUARANTEE",
        "GRANT", "SEED_CAPITAL", "MARGIN_MONEY", "EQUITY", "TRAINING",
        "SKILL_DEVELOPMENT", "EQUIPMENT_SUPPORT", "TOOLKIT_SUPPORT",
        "MARKET_SUPPORT", "INCUBATION", "FINANCE", "CREDIT",
    }

    PATTERNS = {
        "LOAN": [r"\bloan\b", r"\bborrow(?:ing)?\b", r"\bcredit\b", "கடன்", "लोन", "ऋण", "రుణం", "ಸಾಲ", "വായ്പ", "ঋণ"],
        "GRANT": [r"\bgrant\b", "अनुदान", "மானியம்"],
        "SUBSIDY": [r"\bcapital subsidy\b", r"\bsubsidy\b", "सब्सिडी", "சலுகை", "சப்ஸிடீ", "సబ్సిడీ", "ಸಬ್ಸಿಡಿ", "സബ്സിഡി", "ভর্তুকি"],
        "TRAINING": [r"\btraining\b", r"\btrain me\b", "பயிற்சி", "प्रशिक्षण", "శిక్షణ", "ತರಬೇತಿ", "പരിശീലനം", "প্রশিক্ষণ"],
        "SKILL_DEVELOPMENT": [r"\bskill(?:s)?\b", r"skill development", "திறன்", "कौशल"],
        "EQUIPMENT_SUPPORT": [r"\bequipment\b", r"\bmachinery\b", r"\bmachine\b", "இயந்திர", "मशीन", "యంత్ర", "ಯಂತ್ರ", "യന്ത്രം", "মেশিন"],
        "TOOLKIT_SUPPORT": [r"\btoolkit\b", r"\btools\b", "கருவி", "औजार"],
        "MARKET_SUPPORT": [r"\bmarket(?:ing)?\b", r"\bsell(?:ing)?\b", r"find customers", r"reach customers", "சந்தை", "விற்பனை", "मार्केट", "बेचना", "మార్కెట్", "ಮಾರುಕಟ್ಟೆ", "വിപണി", "বাজার"],
        "INCUBATION": [r"\bincubat(?:e|ion|or)\b", r"\bmentor(?:ing|ship)?\b", "मार्गदर्शन"],
        "SEED_CAPITAL": [r"\bseed (?:capital|fund|funding)\b"],
        "EQUITY": [r"\bequity\b", r"\binvestor\b"],
        "CREDIT_GUARANTEE": [r"\bcredit guarantee\b", r"\bcollateral guarantee\b"],
        "INTEREST_SUBVENTION": [r"\binterest subvention\b", r"\binterest subsidy\b", r"\blower interest\b"],
        "MARGIN_MONEY": [r"\bmargin money\b"],
        "FINANCE": [r"\bfunding\b", r"\bfinancial help\b", r"\bfinancial support\b", r"\bfinance\b", "நிதி உதவி", "वित्तीय सहायता"],
    }

    def infer(self, text: str):
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        lower = text.lower()
        needs = []
        for support, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if pattern.isascii():
                    if re.search(pattern, lower):
                        needs.append(support)
                        break
                elif pattern in text:
                    needs.append(support)
                    break

        if "FINANCE" in needs:
            if not any(x in needs for x in ("LOAN", "CREDIT")):
                needs.append("CREDIT")
            needs.remove("FINANCE")
        return list(dict.fromkeys(needs))

    def infer_business_goal(self, text: str):
        lower = text.lower()
        start_patterns = [
            r"\b(?:want|planning|plan|going) to start\b", r"\bstart(?:ing)? (?:a |my )?business\b",
            r"\bnew business\b", r"\bstartup\b", r"business\s+start\s+pann", r"business\s+shuru",
            "தொழில் தொடங்க", "வணிகம் தொடங்க", "व्यवसाय शुरू", "बिजनेस शुरू", "వ్యాపారం ప్రారంభ", "ವ್ಯವಹಾರ ಆರಂಭ", "ബിസിനസ് തുടങ്ങ", "ব্যবসা শুরু",
        ]
        grow_patterns = [
            r"\bgrow(?:\s+my|\s+the)?(?:\s+existing)?(?:\s+\w+){0,3}\s+business\b", r"\bexpand(?:\s+my|\s+the)?(?:\s+existing)?(?:\s+\w+){0,3}\s+business\b", r"\bscale(?:\s+my|\s+the)?(?:\s+existing)?(?:\s+\w+){0,3}\s+business\b",
            r"\bincrease production\b", r"\bopen another (?:shop|branch|unit)\b",
            "விரிவாக்க", "बढ़ाना", "विस्तार", "విస్తర", "ವಿಸ್ತರ", "വിപുലീകര", "সম্প্রসারণ",
        ]
        for p in grow_patterns:
            if (p.isascii() and re.search(p, lower)) or (not p.isascii() and p in text):
                return "GROW_BUSINESS"
        for p in start_patterns:
            if (p.isascii() and re.search(p, lower)) or (not p.isascii() and p in text):
                return "START_BUSINESS"
        return None
