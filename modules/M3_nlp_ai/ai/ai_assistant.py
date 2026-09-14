try:
    from nlp.profile_extractor import ProfileExtractor
    from nlp.m2_adapter import build_m2_profile, build_m2_payload
    from multilingual.language_config import LANGUAGE_QUESTION_TEMPLATES, COMPLETION_MESSAGES
except ModuleNotFoundError:  # package import: nlp_ai.ai.ai_assistant
    from ..nlp.profile_extractor import ProfileExtractor
    from ..nlp.m2_adapter import build_m2_profile, build_m2_payload
    from ..multilingual.language_config import LANGUAGE_QUESTION_TEMPLATES, COMPLETION_MESSAGES


class AIAssistant:
    """Stateful M3 conversation manager.

    Responsibilities:
    - remember facts across messages,
    - understand short answers using the last question,
    - ask only for missing core fields,
    - preserve old values when contradictory information appears,
    - accept explicit support preferences from UI,
    - export a clean canonical profile for M2/M4.
    """

    CORE_FIELDS = [
        "age", "gender", "state", "education", "category",
        "business_type", "sector", "income", "project_cost",
    ]

    PREFERRED_SUPPORT_TYPES = {
        "LOAN", "CAPITAL_SUBSIDY", "INTEREST_SUBVENTION", "CREDIT_GUARANTEE",
        "GRANT", "SEED_CAPITAL", "MARGIN_MONEY", "EQUITY", "TRAINING",
        "SKILL_DEVELOPMENT", "EQUIPMENT_SUPPORT", "TOOLKIT_SUPPORT",
        "MARKET_SUPPORT", "INCUBATION",
    }

    SUPPORT_ALIASES = {
        "LOAN": "LOAN", "LOANS": "LOAN", "SUBSIDY": "CAPITAL_SUBSIDY", "CAPITAL SUBSIDY": "CAPITAL_SUBSIDY",
        "GRANT": "GRANT", "TRAINING": "TRAINING", "SKILL DEVELOPMENT": "SKILL_DEVELOPMENT",
        "EQUIPMENT": "EQUIPMENT_SUPPORT", "EQUIPMENT SUPPORT": "EQUIPMENT_SUPPORT", "TOOLKIT": "TOOLKIT_SUPPORT",
        "MARKETING": "MARKET_SUPPORT", "MARKET SUPPORT": "MARKET_SUPPORT", "INCUBATION": "INCUBATION",
        "SEED CAPITAL": "SEED_CAPITAL", "EQUITY": "EQUITY", "MARGIN MONEY": "MARGIN_MONEY",
        "INTEREST SUBVENTION": "INTEREST_SUBVENTION", "CREDIT GUARANTEE": "CREDIT_GUARANTEE",
    }

    def __init__(self, profile_extractor=None):
        self.profile_extractor = profile_extractor or ProfileExtractor()
        self.profile = {}
        self.current_question = None
        self.conversation_language = "English"
        self.language_locked = False
        self.profile_changes = []
        self.last_conflicts = []
        self.pending_conflict = None
        self.question_templates = LANGUAGE_QUESTION_TEMPLATES

    def process_message(self, message, preferred_support_types=None, use_llm="auto"):
        if preferred_support_types is not None:
            self.set_preferred_support_types(preferred_support_types)

        if not isinstance(message, str):
            return self._build_response(False, "Please enter a valid message.", "UNKNOWN", self._get_missing_fields())
        if not message.strip():
            return self._build_response(False, "Please enter a message.", "UNKNOWN", self._get_missing_fields())

        # If the previous turn raised a conflict, a short answer such as "25"
        # can explicitly resolve it instead of being misread as the next field.
        resolved = self._try_resolve_pending_conflict(message)
        if resolved is not None:
            response = self._continue_conversation()
            return self._build_response(True, response, "UNKNOWN", self._get_missing_fields(), changes=resolved, conflicts=[])

        result = self.profile_extractor.extract(
            message,
            current_question=self.current_question,
            use_llm=use_llm,
        )
        self._remember_language(result)

        intent_data = result.get("intent", {})
        intent = intent_data.get("intent", "UNKNOWN") if isinstance(intent_data, dict) else (intent_data or "UNKNOWN")
        new_profile = result.get("profile", {}) if isinstance(result.get("profile", {}), dict) else {}

        changes = self._update_profile(new_profile)

        # Rule-vs-LLM conflicts are also surfaced, but do not overwrite the
        # deterministic rule value.
        llm_conflicts = result.get("conflicts", [])
        if llm_conflicts and not self.last_conflicts:
            c = llm_conflicts[0]
            self.last_conflicts.append({
                "field": c["field"],
                "old_value": c["rule_value"],
                "new_value": c["llm_value"],
                "source": "rule_vs_llm",
            })

        if self.last_conflicts:
            self.pending_conflict = self.last_conflicts[0].copy()
            return self._build_response(
                True,
                self._conflict_response(),
                intent,
                self._get_missing_fields(),
                changes=changes,
                conflicts=self.last_conflicts,
            )

        response = self._continue_conversation()
        built = self._build_response(True, response, intent, self._get_missing_fields(), changes=changes, conflicts=[])
        built["hybrid"] = result.get("hybrid", {})
        built["confidence"] = result.get("confidence", {})
        built["validation"] = result.get("validation", {})
        return built

    def _remember_language(self, result):
        detail = result.get("language_detail", {}) or {}
        detected = result.get("language")
        primary = detail.get("primary_language") or detected

        # Romanized/native languages with a template are locked on the first
        # meaningful message. Mixed text uses the dominant native language.
        candidate = primary if primary in self.question_templates else detected
        if candidate in self.question_templates and not self.language_locked:
            self.conversation_language = candidate
            self.language_locked = True

    def _update_profile(self, new_profile):
        changes = []
        self.last_conflicts = []
        if not isinstance(new_profile, dict):
            return changes

        for field, new_value in new_profile.items():
            if new_value is None:
                continue

            # support_needs accumulates across messages; it is not a conflict.
            if field == "support_needs":
                existing = self.profile.get(field, [])
                merged = list(dict.fromkeys(list(existing) + list(new_value)))
                if merged != existing:
                    self.profile[field] = merged
                    change = {"field": field, "old_value": existing or None, "new_value": merged, "type": "added" if not existing else "merged"}
                    changes.append(change)
                    self.profile_changes.append(change)
                continue

            old_value = self.profile.get(field)
            if old_value is None:
                self.profile[field] = new_value
                change = {"field": field, "old_value": None, "new_value": new_value, "type": "added"}
                changes.append(change)
                self.profile_changes.append(change)
            elif old_value == new_value:
                continue
            else:
                conflict = {"field": field, "old_value": old_value, "new_value": new_value}
                self.last_conflicts.append(conflict)
                change = {"field": field, "old_value": old_value, "new_value": new_value, "type": "conflict"}
                changes.append(change)
                self.profile_changes.append(change)
                # Keep the established value until the user resolves it.
                self.profile[field] = old_value
        return changes

    def _try_resolve_pending_conflict(self, message):
        if not self.pending_conflict:
            return None
        field = self.pending_conflict["field"]
        parsed = self.profile_extractor.entity_extractor.extract_contextual(message, field)
        if field not in parsed:
            return None
        chosen = parsed[field]
        allowed = {self.pending_conflict["old_value"], self.pending_conflict["new_value"]}
        if chosen not in allowed:
            return None
        old = self.profile.get(field)
        self.profile[field] = chosen
        change = {"field": field, "old_value": old, "new_value": chosen, "type": "resolved"}
        self.profile_changes.append(change)
        self.pending_conflict = None
        self.last_conflicts = []
        return [change]

    def _conflict_response(self):
        if not self.last_conflicts:
            return "I noticed conflicting information."
        c = self.last_conflicts[0]
        field, old, new = c["field"], c["old_value"], c["new_value"]
        if self.conversation_language == "Tamil":
            return f"நீங்கள் முன்பு உங்கள் {field} {old} என்று கூறினீர்கள். இப்போது {new} என்று கூறுகிறீர்கள். எது சரியானது?"
        if self.conversation_language == "Tanglish":
            return f"Neenga munnadi unga {field} {old} nu sonneenga. Ippo {new} nu solreenga. Edhu correct?"
        if self.conversation_language == "Hindi":
            return f"आपने पहले अपनी {field} {old} बताई थी, लेकिन अब आपने {new} कहा है। कौन सा सही है?"
        if self.conversation_language == "Hinglish":
            return f"Aapne pehle apni {field} {old} batayi thi, lekin ab aapne {new} kaha hai. Kaunsa correct hai?"
        return f"You previously said your {field} was {old}, but now you said {new}. Which one is correct?"

    def _get_missing_fields(self):
        return [field for field in self.CORE_FIELDS if field not in self.profile]

    def _continue_conversation(self):
        missing = self._get_missing_fields()
        if not missing:
            self.current_question = None
            return COMPLETION_MESSAGES.get(self.conversation_language, COMPLETION_MESSAGES["English"])
        self.current_question = missing[0]
        return self._get_question(self.current_question)

    def _get_question(self, field):
        templates = self.question_templates.get(self.conversation_language, self.question_templates["English"])
        return templates.get(field, self.question_templates["English"].get(field, f"Please provide your {field}."))

    def get_current_question(self):
        return None if self.current_question is None else self._get_question(self.current_question)

    def set_preferred_support_types(self, support_types):
        if support_types is None:
            self.profile.pop("preferred_support_types", None)
            return []
        if isinstance(support_types, str):
            support_types = [support_types]
        if not isinstance(support_types, (list, tuple, set)):
            raise TypeError("preferred_support_types must be a list/tuple/set or string")

        normalized = []
        for item in support_types:
            key = str(item).strip().upper().replace("_", " ")
            canonical = self.SUPPORT_ALIASES.get(key, str(item).strip().upper())
            if canonical not in self.PREFERRED_SUPPORT_TYPES:
                raise ValueError(f"Unsupported support type: {item}")
            if canonical not in normalized:
                normalized.append(canonical)
        self.profile["preferred_support_types"] = normalized
        return normalized

    def export_for_m2(self):
        """Return the canonical M3 -> M2/M4 profile contract."""
        return build_m2_profile(self.profile)

    def to_m2_payload(self):
        return build_m2_payload(self.profile)

    def _build_response(self, success, response, intent, missing_fields, changes=None, conflicts=None):
        return {
            "success": success,
            "response": response,
            "profile": self.profile.copy(),
            "missing_fields": missing_fields,
            "intent": intent,
            "current_question": self.current_question,
            "next_field": self.current_question,
            "changes": changes or [],
            "conflicts": conflicts or [],
            "language": self.conversation_language,
            "m2_profile": self.export_for_m2(),
        }

    def reset_profile(self):
        self.profile = {}
        self.current_question = None
        self.conversation_language = "English"
        self.language_locked = False
        self.profile_changes = []
        self.last_conflicts = []
        self.pending_conflict = None
