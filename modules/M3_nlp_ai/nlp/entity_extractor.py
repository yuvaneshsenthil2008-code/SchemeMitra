import difflib
import re

from .money_parser import MoneyParser
from .normalizer import Normalizer
from .rule_extractor import RuleExtractor


class EntityExtractor:
    """High-level deterministic entity extraction.

    Free-form text uses RuleExtractor.  When the assistant has just asked a
    closed-choice question, conservative fuzzy matching is allowed for typos.
    This separation keeps typo support from creating false positives in random
    user messages.
    """

    def __init__(self):
        self.rules = RuleExtractor()
        self.normalizer = Normalizer()
        self.money = MoneyParser()

    def extract(self, text: str, current_question=None):
        profile = self.rules.extract(text)
        if current_question:
            contextual = self.extract_contextual(text, current_question)
            # Explicit rule evidence in the message wins if both agree on a
            # field; contextual extraction fills only what rules missed.
            for field, value in contextual.items():
                profile.setdefault(field, value)
        return profile

    def extract_contextual(self, text: str, field: str):
        if not isinstance(text, str):
            return {}
        raw = text.strip()
        lower = raw.lower().strip()
        if not raw:
            return {}

        if field == "age":
            patterns = [
                r"^(\d{1,3})$", r"^age\W*(\d{1,3})\W*$",
                r"^(?:i am|i'm|im)(?: actually)?\s+(\d{1,3})(?:\s+years?\s+old)?\W*$",
                r"^(?:enaku|enakku)\s+(\d{1,3})\s+(?:vayasu|vaysu|vayas)\W*$",
                r"^(?:meri age|meri umar)\s+(\d{1,3})(?:\s+hai)?\W*$",
            ]
            for p in patterns:
                m = re.match(p, lower)
                if m:
                    age = int(m.group(1))
                    if 1 <= age <= 120:
                        return {"age": age}
            return {}

        if field in {"income", "project_cost", "available_capital"}:
            parsed = self.money.parse_first(raw, allow_bare=True)
            if parsed:
                result = {field: parsed.amount}
                if field == "income" and parsed.period:
                    result["income_period"] = parsed.period
                return result
            return {}

        if field == "gender":
            aliases = {
                "male": "Male", "m": "Male", "man": "Male", "female": "Female", "f": "Female", "woman": "Female",
                "femle": "Female", "transgender": "Transgender", "trans": "Transgender", "transman": "Transgender", "transwoman": "Transgender", "third gender": "Transgender", "thirunangai": "Transgender", "thirunambi": "Transgender", "aravani": "Transgender", "kinnar": "Transgender", "hijra": "Transgender", "aan": "Male", "aambala": "Male", "ponnu": "Female", "pen": "Female",
                "ஆண்": "Male", "பெண்": "Female", "पुरुष": "Male", "महिला": "Female", "aadmi": "Male", "purush": "Male", "ladka": "Male", "aurat": "Female", "mahila": "Female", "ladki": "Female",
                "మగ": "Male", "పురుషుడు": "Male", "ఆడ": "Female", "మహిళ": "Female",
                "ಗಂಡು": "Male", "ಪುರುಷ": "Male", "ಹೆಣ್ಣು": "Female", "ಮಹಿಳೆ": "Female",
                "ആൺ": "Male", "പുരുഷൻ": "Male", "പെൺ": "Female", "സ്ത്രീ": "Female",
                "পুরুষ": "Male", "মহিলা": "Female",
            }
            return self._closed_choice(lower, "gender", aliases, cutoff=0.78)

        if field == "state":
            aliases = dict(self.normalizer.STATE_MAP)
            aliases.update({"tamilnaduu": "Tamil Nadu", "tamil naduu": "Tamil Nadu"})
            # Context answers often contain a small prefix such as "I live in".
            for prefix in ("i live in ", "from ", "currently live in ", "naan ", "main "):
                if lower.startswith(prefix):
                    lower = lower[len(prefix):].strip(" .!?,")
            return self._closed_choice(lower.strip(" .!?"), "state", aliases, cutoff=0.80)

        if field == "education":
            aliases = {
                "degree": "Degree", "dgree": "Degree", "graduate": "Degree", "graduation": "Degree", "diploma": "Diploma",
                "12th": "12th", "12": "12th", "10th": "10th", "10": "10th", "iti": "ITI", "school": "School",
                "postgraduate": "Postgraduate", "pg": "Postgraduate", "degree mudichiten": "Degree", "degree mudichitten": "Degree",
                "பட்டம்": "Degree", "டிப்ளோமா": "Diploma", "முதுகலை": "Postgraduate", "डिग्री": "Degree", "डिप्लोमा": "Diploma",
                "డిగ్రీ": "Degree", "డిప్లొమా": "Diploma", "ಪದವಿ": "Degree", "ಡಿಪ್ಲೊಮಾ": "Diploma", "ഡിഗ്രി": "Degree", "ഡിപ്ലോമ": "Diploma",
                "ডিগ্রি": "Degree", "ডিপ্লোমা": "Diploma",
            }
            # Recognize informal phrases before fuzzy exact-choice matching.
            if "degree mudich" in lower:
                return {"education": "Degree"}
            return self._closed_choice(lower.strip(" .!?"), "education", aliases, cutoff=0.76)

        if field == "category":
            aliases = {
                "general": "General", "genral": "General", "general category": "General", "obc": "OBC", "sc": "SC", "st": "ST", "ews": "EWS",
                "சாதாரண": "General", "பொது": "General", "सामान्य": "General",
            }
            return self._closed_choice(lower.strip(" .!?"), "category", aliases, cutoff=0.78)

        if field == "business_type":
            aliases = {
                "startup": "Startup", "new": "Startup", "new business": "Startup", "idea": "Startup",
                "existing": "Existing", "existing business": "Existing", "running": "Existing", "running business": "Existing",
            }
            result = self._closed_choice(lower.strip(" .!?"), "business_type", aliases, cutoff=0.78)
            if result:
                result["new_business"] = result["business_type"] == "Startup"
            return result

        if field == "sector":
            # Reuse the free-text rule extractor because sector answers often
            # contain phrases such as "tailoring business".
            value = self.rules._extract_sector(raw)
            return {"sector": value} if value else {}

        return {}

    def _closed_choice(self, text, field, aliases, cutoff):
        if text in aliases:
            return {field: aliases[text]}
        ascii_choices = [x for x in aliases if x.isascii()]
        if text.isascii():
            matches = difflib.get_close_matches(text, ascii_choices, n=1, cutoff=cutoff)
            if matches:
                return {field: aliases[matches[0]]}
        return {}
