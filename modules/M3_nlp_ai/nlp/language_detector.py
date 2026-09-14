import re
from collections import Counter


class LanguageDetector:
    """Lightweight India-focused language/script detector.

    Native scripts are detected deterministically.  Romanized Tamil/Hindi and
    a few other common romanized varieties use conservative word scoring.
    Difficult or mixed cases can be escalated to the optional LLM layer.
    """

    SCRIPT_RANGES = {
        "Devanagari": r"[\u0900-\u097F]",
        "Bengali": r"[\u0980-\u09FF]",
        "Gurmukhi": r"[\u0A00-\u0A7F]",
        "Gujarati": r"[\u0A80-\u0AFF]",
        "Odia": r"[\u0B00-\u0B7F]",
        "Tamil": r"[\u0B80-\u0BFF]",
        "Telugu": r"[\u0C00-\u0C7F]",
        "Kannada": r"[\u0C80-\u0CFF]",
        "Malayalam": r"[\u0D00-\u0D7F]",
    }

    TANGLISH_WORDS = {
        "naan", "naanga", "enakku", "enaku", "ennoda", "enoda", "enna",
        "irukken", "iruken", "irukku", "vayasu", "vaysu", "venum", "thevai",
        "mudichiten", "padichiruken", "pannanum", "panna", "panren", "poren",
        "inga", "anga", "epdi", "eppadi", "illa", "romba", "konjam", "evlo",
        "thozhil", "vivasayam", "saapadu", "sollunga", "kudunga",
    }

    HINGLISH_WORDS = {
        "main", "mujhe", "mera", "meri", "mere", "hum", "aap", "aapka", "kya",
        "kaise", "kyun", "hai", "hain", "hoon", "se", "ko", "ke", "ki", "mein",
        "chahiye", "karna", "karni", "karta", "karti", "paise", "umar", "saal",
        "shuru", "madad", "yojana", "sarkari", "paisa",
    }

    TELUGLISH_WORDS = {
        "naku", "naaku", "meeru", "nenu", "undi", "kavali", "kaavali", "cheyali",
        "vyaparam", "modalu", "pette", "vayasu",
    }

    KANGLISH_WORDS = {
        "nanu", "nanage", "nanna", "beku", "ide", "madbeku", "maadbeku",
        "vyapara", "vayassu",
    }

    MANGLISH_WORDS = {
        "enikku", "ente", "njan", "venam", "venum", "undu",
        "thudangan", "vayassu",
    }

    BENGLISH_WORDS = {
        "ami", "amar", "chai", "achhe", "ache", "shuru", "boyosh",
    }

    ENGLISH_WORDS = {
        "i", "am", "is", "are", "the", "a", "an", "my", "me", "from", "want",
        "need", "have", "completed", "degree", "graduate", "business", "start",
        "starting", "food", "service", "manufacturing", "income", "age", "years",
        "old", "loan", "scheme", "support", "project", "cost",
    }

    MARATHI_HINTS = {"माझे", "माझी", "मला", "आहे", "व्यवसाय", "वय", "महाराष्ट्र"}
    HINDI_HINTS = {"मुझे", "मेरी", "मेरा", "है", "व्यवसाय", "उम्र", "योजना", "लोन"}

    def detect(self, text: str) -> str:
        return self.detect_detail(text)["language"]

    def detect_detail(self, text: str) -> dict:
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        text = text.strip()
        if not text:
            return {"language": "Unknown", "primary_language": "Unknown", "scripts": [], "confidence": 0.0}

        counts = {
            script: len(re.findall(pattern, text))
            for script, pattern in self.SCRIPT_RANGES.items()
        }
        active = [name for name, count in counts.items() if count > 0]
        latin_count = len(re.findall(r"[A-Za-z]", text))

        if active:
            # Devanagari is shared by Hindi and Marathi. Use obvious lexical hints;
            # otherwise default to Hindi because it is the broader configured path.
            native = max(active, key=lambda s: counts[s])
            if native == "Devanagari":
                mr = sum(1 for w in self.MARATHI_HINTS if w in text)
                hi = sum(1 for w in self.HINDI_HINTS if w in text)
                native = "Marathi" if mr > hi and mr > 0 else "Hindi"
            elif native == "Gurmukhi":
                native = "Punjabi"

            if len(active) > 1 or latin_count > 0:
                return {
                    "language": "Mixed",
                    "primary_language": native,
                    "scripts": active + (["Latin"] if latin_count else []),
                    "confidence": 0.90,
                }
            return {"language": native, "primary_language": native, "scripts": active, "confidence": 0.99}

        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        if not words:
            return {"language": "Unknown", "primary_language": "Unknown", "scripts": [], "confidence": 0.2}

        dictionaries = {
            "Tanglish": self.TANGLISH_WORDS,
            "Hinglish": self.HINGLISH_WORDS,
            "Teluglish": self.TELUGLISH_WORDS,
            "Kanglish": self.KANGLISH_WORDS,
            "Manglish": self.MANGLISH_WORDS,
            "Benglish": self.BENGLISH_WORDS,
            "English": self.ENGLISH_WORDS,
        }
        scores = Counter({name: self._count_matches(words, vocab) for name, vocab in dictionaries.items()})

        # Existing behavior: two romanized-language clues beat English words unless English clearly dominates.
        romanized = ["Tanglish", "Hinglish", "Teluglish", "Kanglish", "Manglish", "Benglish"]
        best_roman = max(romanized, key=lambda x: scores[x])
        if scores["English"] > 0 and scores["English"] >= scores[best_roman] + 3:
            return {"language": "English", "primary_language": "English", "scripts": ["Latin"], "confidence": 0.85}

        if scores[best_roman] >= 2:
            return {"language": best_roman, "primary_language": best_roman, "scripts": ["Latin"], "confidence": 0.90}

        if scores["English"] >= 1:
            return {"language": "English", "primary_language": "English", "scripts": ["Latin"], "confidence": 0.85}

        if scores[best_roman] == 1:
            return {"language": best_roman, "primary_language": best_roman, "scripts": ["Latin"], "confidence": 0.60}

        return {"language": "Unknown", "primary_language": "Unknown", "scripts": ["Latin"], "confidence": 0.35}

    def _count_matches(self, words, dictionary):
        return sum(1 for word in words if word in dictionary)
