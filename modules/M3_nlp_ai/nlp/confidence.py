class ConfidenceEngine:
    """Confidence/provenance helper for the hybrid extraction pipeline."""

    SOURCE_CONFIDENCE = {
        "rule": 1.00,
        "context": 0.99,
        "normalization": 0.98,
        "ui": 1.00,
        "llm": 0.85,
        "inferred_rule": 0.90,
    }

    def get_confidence(self, source):
        return self.SOURCE_CONFIDENCE.get(source, 0.50)

    def build_field_result(self, value, source, evidence=None):
        result = {"value": value, "source": source, "confidence": self.get_confidence(source)}
        if evidence is not None:
            result["evidence"] = evidence
        return result

    def detect_conflicts(self, rule_profile, llm_profile):
        conflicts = []
        for field in set(rule_profile) & set(llm_profile):
            rule_value = rule_profile[field]
            llm_value = llm_profile[field]
            if rule_value is not None and llm_value is not None and rule_value != llm_value:
                conflicts.append({
                    "field": field,
                    "rule_value": rule_value,
                    "llm_value": llm_value,
                    "action": "ASK_USER",
                })
        return conflicts

    def score_profile(self, profile_sources):
        result = {}
        for field, data in profile_sources.items():
            result[field] = self.build_field_result(
                data.get("value"), data.get("source", "unknown"), data.get("evidence")
            )
        return result
