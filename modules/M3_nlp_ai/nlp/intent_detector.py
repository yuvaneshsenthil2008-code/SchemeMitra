import re


class IntentDetector:
    """Conservative intent classifier for OpportunityOS conversations."""

    OPPORTUNITY_KEYWORDS = {
        # English
        "scheme", "loan", "subsidy", "business", "startup", "government support",
        "government scheme", "eligible", "eligibility", "funding", "financial assistance",
        "entrepreneur", "opportunity", "grant", "project", "want to start", "apply", "support",
        # Tamil/Tanglish
        "தொழில்", "வணிகம்", "வியாபாரம்", "கடன்", "மானியம்", "அரசு திட்டம்", "நிதி உதவி",
        "thozhil", "business panna", "start panna", "loan venum", "scheme venum", "arasu scheme",
        "maanayam", "maaniyam", "thaguthi", "funding venum",
        # Hindi/Hinglish
        "योजना", "लोन", "ऋण", "सब्सिडी", "व्यवसाय", "कारोबार", "स्टार्टअप", "वित्तीय सहायता",
        "अनुदान", "पात्रता", "आवेदन", "yojana", "sarkari scheme", "loan chahiye", "business shuru",
        "funding chahiye", "madad chahiye",
        # Telugu
        "వ్యాపారం", "పథకం", "రుణం", "సబ్సిడీ", "సహాయం",
        # Kannada
        "ವ್ಯವಹಾರ", "ಯೋಜನೆ", "ಸಾಲ", "ಸಬ್ಸಿಡಿ", "ಸಹಾಯ",
        # Malayalam
        "ബിസിനസ്", "പദ്ധതി", "വായ്പ", "സബ്സിഡി", "സഹായം",
        # Bengali
        "ব্যবসা", "প্রকল্প", "ঋণ", "ভর্তুকি", "সহায়তা",
        # Marathi/Gujarati/Punjabi/Odia common
        "व्यवसाय", "कर्ज", "अनुदान", "યોજના", "લોન", "વ્યવસાય", "ਯੋਜਨਾ", "ਕਰਜ਼", "ବ୍ୟବସାୟ", "ଋଣ",
    }

    GENERAL_KEYWORDS = {
        "weather", "temperature", "news", "movie", "song", "cricket", "football", "joke", "recipe", "translate", "meaning",
        "வானிலை", "வெப்பநிலை", "செய்தி", "திரைப்படம்", "பாடல்", "கிரிக்கெட்",
        "मौसम", "तापमान", "समाचार", "फिल्म", "गाना", "क्रिकेट",
        "mausam", "news batao", "gaana", "recipe batao", "translate karo",
    }

    GREETINGS = {
        "hi", "hello", "hey", "vanakkam", "வணக்கம்", "namaste", "नमस्ते", "namaskar",
        "నమస్తే", "ನಮಸ್ಕಾರ", "നമസ്കാരം", "নমস্কার",
    }

    def __init__(self):
        self.opportunity_keywords = self.OPPORTUNITY_KEYWORDS
        self.general_keywords = self.GENERAL_KEYWORDS

    def detect(self, text):
        if not isinstance(text, str):
            raise TypeError("Text must be a string.")
        raw = text.strip()
        lower = raw.lower()
        if not lower:
            return self._result("UNKNOWN", False, 0.0, "ASK_CLARIFICATION")

        opportunity_hits = self._hits(lower, self.opportunity_keywords)
        general_hits = self._hits(lower, self.general_keywords)

        if opportunity_hits and opportunity_hits >= general_hits:
            return self._result("OPPORTUNITY", True, min(0.99, 0.82 + 0.04 * opportunity_hits), "CONTINUE")
        if general_hits:
            return self._result("GENERAL_QUERY", False, min(0.99, 0.84 + 0.03 * general_hits), "REDIRECT")

        # Greetings intentionally remain UNKNOWN for backward compatibility:
        # a greeting should not be mistaken for an opportunity request.
        if self._looks_like_greeting(lower):
            return self._result("UNKNOWN", False, 0.80, "ASK_CLARIFICATION")

        return self._result("UNKNOWN", False, 0.50, "ASK_CLARIFICATION")

    @staticmethod
    def _result(intent, relevant, confidence, action):
        return {"intent": intent, "relevant": relevant, "confidence": confidence, "action": action}

    @staticmethod
    def _hits(text, keywords):
        count = 0
        for keyword in keywords:
            k = keyword.lower()
            if k.isascii() and re.fullmatch(r"[a-z0-9 ]+", k):
                if re.search(rf"(?<!\w){re.escape(k)}(?!\w)", text):
                    count += 1
            elif k in text:
                count += 1
        return count

    def _looks_like_greeting(self, text):
        cleaned = re.sub(r"[^\w\u0900-\u0d7f]+", " ", text).strip()
        return any(g in cleaned for g in self.GREETINGS)
