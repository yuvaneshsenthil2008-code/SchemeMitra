import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MoneyValue:
    amount: int
    period: Optional[str] = None  # "monthly", "annual", or None
    unit: Optional[str] = None
    raw: Optional[str] = None


class MoneyParser:
    """Parse common Indian money expressions safely."""

    MULTIPLIERS = {
        None: 1,
        "k": 1_000,
        "thousand": 1_000,
        "thousands": 1_000,
        "l": 100_000,
        "lac": 100_000,
        "lacs": 100_000,
        "lakh": 100_000,
        "lakhs": 100_000,
        "cr": 10_000_000,
        "crore": 10_000_000,
        "crores": 10_000_000,
    }

    AMOUNT_RE = re.compile(
        r"(?<![\w.])(?:₹|rs\.?|inr|रु\.?|రూ\.?|ರೂ\.?|৳)?\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*"
        r"(k|thousand|thousands|l|lac|lacs|lakh|lakhs|cr|crore|crores)?"
        r"(?:\s*/-)?(?![a-z])",
        re.IGNORECASE,
    )

    MONTHLY_MARKERS = (
        "per month", "monthly", "/month", "a month", "month income", "மாத", "மாதம்",
        "प्रति माह", "मासिक", "mahina", "mahine", "నెల", "ತಿಂಗಳ", "മാസ", "মাসিক",
    )
    ANNUAL_MARKERS = (
        "per year", "yearly", "annual", "annually", "a year", "வருட", "ஆண்டு",
        "वार्षिक", "सालाना", "saalana", "ప్రతి సంవత్సరం", "ವಾರ್ಷಿಕ", "വാർഷിക", "বার্ষিক",
    )

    def parse_first(self, text: str, allow_bare: bool = False) -> Optional[MoneyValue]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        cleaned = text.strip().lower()
        if not cleaned:
            return None

        # Explicitly reject malformed repeated-unit forms such as 25kk.
        if re.search(r"\d\s*(?:k|l|cr)\s*(?:k|l|cr)\b", cleaned):
            return None

        match = self.AMOUNT_RE.search(cleaned)
        if not match:
            return None

        raw_number, unit = match.group(1), match.group(2)
        had_currency = bool(re.search(r"₹|\brs\.?\b|\binr\b|रु\.?|రూ\.?|ರೂ\.?", cleaned))
        has_unit = unit is not None
        if not allow_bare and not had_currency and not has_unit:
            return None

        try:
            number = float(raw_number.replace(",", ""))
        except ValueError:
            return None
        if number < 0:
            return None

        unit = unit.lower() if unit else None
        amount = int(round(number * self.MULTIPLIERS[unit]))
        period = self.detect_period(cleaned)
        return MoneyValue(amount=amount, period=period, unit=unit, raw=match.group(0))

    def parse_all(self, text: str, allow_bare: bool = False):
        results = []
        for match in self.AMOUNT_RE.finditer(text.lower()):
            snippet = match.group(0)
            parsed = self.parse_first(snippet, allow_bare=allow_bare)
            if parsed:
                results.append(parsed)
        return results

    def detect_period(self, text: str) -> Optional[str]:
        lower = text.lower()
        if any(marker in lower for marker in self.MONTHLY_MARKERS):
            return "monthly"
        if any(marker in lower for marker in self.ANNUAL_MARKERS):
            return "annual"
        return None

    @staticmethod
    def annualize(amount: int, period: Optional[str]) -> int:
        return int(amount * 12) if period == "monthly" else int(amount)
