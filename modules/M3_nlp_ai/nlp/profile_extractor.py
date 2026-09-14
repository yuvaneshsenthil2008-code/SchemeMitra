from .confidence import ConfidenceEngine
from .entity_extractor import EntityExtractor
from .intent_detector import IntentDetector
from .language_detector import LanguageDetector
from .llm_extractor import LLMExtractor
from .missing_info import MissingInfoDetector
from .normalizer import Normalizer
from .validator import ProfileValidator


class ProfileExtractor:
    """Hybrid M3 NLU pipeline: deterministic rules first, LLM when useful."""

    def __init__(self, llm_extractor=None):
        self.language_detector = LanguageDetector()
        self.entity_extractor = EntityExtractor()
        self.rule_extractor = self.entity_extractor.rules  # backward-compatible public attribute
        self.normalizer = Normalizer()
        self.llm_extractor = llm_extractor or LLMExtractor()
        self.confidence_engine = ConfidenceEngine()
        self.intent_detector = IntentDetector()
        self.validator = ProfileValidator()
        self.missing_info_detector = MissingInfoDetector()

    def extract(self, text, llm_response=None, current_question=None, use_llm="auto"):
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        if not text.strip():
            return self._empty_result()

        intent = self.intent_detector.detect(text)
        language_detail = self.language_detector.detect_detail(text)
        language = language_detail["language"]

        # General unrelated requests should not accidentally populate profile
        # fields just because they contain a number.
        if intent["intent"] == "GENERAL_QUERY":
            result = self._empty_result(language=language, intent=intent)
            result["language_detail"] = language_detail
            return result

        rule_profile = self.entity_extractor.extract(text, current_question=current_question)

        should_call_llm, reason = self._should_use_llm(
            text=text,
            language_detail=language_detail,
            intent=intent,
            rule_profile=rule_profile,
            current_question=current_question,
            use_llm=use_llm,
            llm_response=llm_response,
        )

        llm_profile = {}
        if should_call_llm:
            llm_profile = self.llm_extractor.extract(text, language_detail.get("primary_language") or language, llm_response)

        conflicts = self.confidence_engine.detect_conflicts(rule_profile, llm_profile)
        merged, sources = self._merge_profiles(rule_profile, llm_profile)
        normalized = self.normalizer.normalize_profile(merged)

        confidence_input = {
            field: {"value": value, "source": sources.get(field, "unknown")}
            for field, value in normalized.items()
        }
        confidence = self.confidence_engine.score_profile(confidence_input)
        validation = self.validator.validate(normalized)
        missing = self.missing_info_detector.analyze(normalized)

        return {
            "language": language,
            "language_detail": language_detail,
            "intent": intent,
            "profile": normalized,
            "confidence": confidence,
            "conflicts": conflicts,
            "validation": validation,
            "missing_info": missing,
            "hybrid": {
                "rule_fields": sorted(rule_profile.keys()),
                "llm_used": should_call_llm,
                "llm_reason": reason,
                "llm_status": self.llm_extractor.last_status if should_call_llm else "NOT_NEEDED",
            },
        }

    def _should_use_llm(self, text, language_detail, intent, rule_profile, current_question, use_llm, llm_response):
        if llm_response is not None:
            return True, "MOCK_RESPONSE"
        if use_llm is False or use_llm == "never":
            return False, "DISABLED"
        if not self.llm_extractor.connected:
            return False, "NOT_CONNECTED"
        if use_llm is True or use_llm == "always":
            return True, "FORCED"

        # Auto mode: rules are preferred. Escalate when a relevant message is
        # semantically rich but rules extracted little, or when a less-covered
        # Indian language/mixed-script message is encountered.
        primary = language_detail.get("primary_language")
        less_rule_covered = primary in {"Telugu", "Kannada", "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi", "Odia"}
        mixed = language_detail.get("language") == "Mixed"
        rich = len(text.split()) >= 5
        few_fields = len(rule_profile) <= 1
        if (less_rule_covered or mixed) and rich:
            return True, "MULTILINGUAL_FALLBACK"
        if intent["intent"] == "OPPORTUNITY" and rich and few_fields:
            return True, "LOW_RULE_COVERAGE"
        if current_question and current_question not in rule_profile and rich:
            return True, "UNRESOLVED_CONTEXT_ANSWER"
        return False, "RULES_SUFFICIENT"

    def _merge_profiles(self, rule_profile, llm_profile):
        merged, sources = {}, {}
        for field, value in rule_profile.items():
            if value is not None:
                merged[field] = value
                sources[field] = "rule"
        for field, value in llm_profile.items():
            if field not in merged and value is not None:
                merged[field] = value
                sources[field] = "llm"
        return merged, sources

    def _empty_result(self, language="Unknown", intent=None):
        if intent is None:
            intent = {"intent": "UNKNOWN", "relevant": False, "confidence": 0.0, "action": "ASK_CLARIFICATION"}
        validation = self.validator.validate({})
        missing = self.missing_info_detector.analyze({})
        return {
            "language": language,
            "language_detail": {"language": language, "primary_language": language, "scripts": [], "confidence": 0.0},
            "intent": intent,
            "profile": {}, "confidence": {}, "conflicts": [],
            "validation": validation, "missing_info": missing,
            "hybrid": {"rule_fields": [], "llm_used": False, "llm_reason": "EMPTY_OR_IRRELEVANT", "llm_status": "NOT_NEEDED"},
        }
