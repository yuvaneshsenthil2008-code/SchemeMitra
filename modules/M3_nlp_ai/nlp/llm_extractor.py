"""Optional LLM extraction layer.

The implementation is provider-agnostic.  It supports:
1) deterministic mock dictionaries in tests,
2) an injected callable, or
3) an OpenAI-compatible chat-completions HTTP endpoint configured with
   LLM_BASE_URL, LLM_API_KEY and LLM_MODEL.

No network call is made unless a provider is configured.
"""

import json
import os
import re
import urllib.error
import urllib.request
from typing import Callable, Optional


class LLMExtractor:
    SUPPORTED_FIELDS = [
        "age", "gender", "state", "district", "education", "education_field", "category",
        "business_type", "sector", "income", "income_period", "project_cost",
        "available_capital", "new_business", "artisan_trade", "business_goal",
        "support_needs",
    ]

    def __init__(self, client: Optional[Callable] = None, base_url=None, api_key=None, model=None, timeout=20):
        self.client = client
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL")
        self.timeout = timeout
        self.last_status = "NOT_CALLED"
        self.last_error = None

    @property
    def connected(self):
        return self.client is not None or bool(self.base_url and self.api_key and self.model)

    def build_prompt(self, text, language):
        return f"""You are the NLU extraction component of an Indian opportunity-discovery system.
User language: {language}

Extract ONLY facts that are explicitly stated or unambiguously implied by the user's own situation.
Never guess a missing fact. Never infer caste/category, gender, income, age, or location from names or stereotypes.
Ignore facts that clearly belong to another person (father, mother, friend, etc.).
Do not decide scheme eligibility. Do not rank schemes.
Do not create preferred_support_types; that comes directly from UI selection.

Return one JSON object only. Allowed fields:
{', '.join(self.SUPPORTED_FIELDS)}

Canonical values:
- education: use only a stated qualification level such as Degree, Postgraduate, Diploma, ITI, 12th, 10th, PhD.
- education_field: field/trade explicitly stated, such as Computer Science, Artificial Intelligence, Mechanical Engineering. Do not infer education level from a field name alone.
- business_type: Startup | Existing | Idea
- business_goal: START_BUSINESS | GROW_BUSINESS
- support_needs: array containing only LOAN, SUBSIDY, CREDIT, INTEREST_SUBVENTION,
  CREDIT_GUARANTEE, GRANT, SEED_CAPITAL, MARGIN_MONEY, EQUITY, TRAINING,
  SKILL_DEVELOPMENT, EQUIPMENT_SUPPORT, TOOLKIT_SUPPORT, MARKET_SUPPORT,
  INCUBATION, or FINANCE.
- income_period: monthly | annual when the period is explicitly stated.

User message:
{text}
"""

    def parse_response(self, response):
        if isinstance(response, str):
            response = self._json_from_text(response)
        if not isinstance(response, dict):
            raise TypeError("LLM response must be a dictionary or JSON object string.")
        result = {}
        for field in self.SUPPORTED_FIELDS:
            if field in response and response[field] is not None:
                result[field] = response[field]
        return result

    def extract(self, text, language, llm_response=None):
        if not isinstance(text, str):
            raise TypeError("Input text must be a string.")
        if not text.strip():
            self.last_status = "EMPTY_INPUT"
            return {}
        if llm_response is not None:
            self.last_status = "MOCK"
            return self.parse_response(llm_response)

        if self.client is not None:
            try:
                response = self.client(prompt=self.build_prompt(text, language), text=text, language=language)
                self.last_status = "OK"
                return self.parse_response(response)
            except Exception as exc:
                self.last_status = "ERROR"
                self.last_error = str(exc)
                return {}

        if not self.connected:
            self.last_status = "LLM_NOT_CONNECTED"
            return {}

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Return only valid JSON. You are a conservative information extractor."},
                    {"role": "user", "content": self.build_prompt(text, language)},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            self.last_status = "OK"
            return self.parse_response(content)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, TypeError) as exc:
            self.last_status = "ERROR"
            self.last_error = str(exc)
            return {}

    @staticmethod
    def _json_from_text(text):
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", cleaned, re.S)
            if not m:
                raise
            return json.loads(m.group(0))
