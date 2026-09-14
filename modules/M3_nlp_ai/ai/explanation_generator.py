"""NLG helpers for M3.

Eligibility explanations themselves belong to M2.  This generator only creates
conversation/profile language and never changes eligibility results.
"""


class ExplanationGenerator:
    def profile_summary(self, profile: dict, language: str = "English") -> str:
        if not profile:
            return "I do not have profile information yet."
        visible = []
        for field in ("age", "gender", "state", "education", "category", "sector", "business_type", "income", "project_cost"):
            if field in profile:
                visible.append(f"{field.replace('_', ' ')}: {profile[field]}")
        summary = ", ".join(visible)
        if language == "Tamil":
            return f"நான் சேகரித்த தகவல்கள்: {summary}"
        if language == "Hindi":
            return f"मैंने यह जानकारी एकत्र की है: {summary}"
        return f"I have collected: {summary}"

    def safe_recovery(self, current_question=None, language="English"):
        if current_question:
            if language == "Tamil":
                return "அந்த பதிலை புரிந்து கொள்ள முடியவில்லை. தயவுசெய்து மீண்டும் தெளிவாக சொல்லுங்கள்."
            if language == "Hindi":
                return "मैं उस उत्तर को समझ नहीं पाया। कृपया थोड़ा स्पष्ट करके बताइए।"
            return "I couldn't confidently understand that answer. Please provide it again a little more clearly."
        return "I couldn't confidently extract profile information from that message."
