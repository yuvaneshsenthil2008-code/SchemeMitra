"""
OpportunityOS — Gemini AI Provider

Handles low-level communication with Google Gemini API for factual pathway explanations.
Preserves strict system boundaries: Gemini is NEVER the source of truth for facts.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
import socket

logger = logging.getLogger("OpportunityOS.GeminiProvider")

SYSTEM_INSTRUCTION = (
    "You are the SchemeMitra Pathway Copilot.\n\n"
    "You explain personalized opportunity guidance using ONLY the verified context supplied by SchemeMitra.\n\n"
    "You are NOT the source of truth for:\n"
    "eligibility, scheme rules, government requirements, official process, benefits, deadlines, "
    "monetary values, documents, URLs, application sequence, or government relationships.\n\n"
    "Never invent facts.\n\n"
    "Preserve the supplied eligibility status exactly.\n\n"
    "If information is missing, say it is not available in the verified context.\n\n"
    "If ordering_confidence = OFFICIAL_SEQUENCE, preserve the supplied official sequence exactly.\n\n"
    "If ordering_confidence = PARTIAL or NO_OFFICIAL_SEQUENCE, any ordering you suggest must be clearly "
    "labelled as practical planning guidance, not an official government sequence.\n\n"
    "Do not claim the user is approved, selected, sanctioned, guaranteed, or officially eligible.\n\n"
    "Do not provide unofficial application links.\n\n"
    "Return only valid JSON matching the required schema."
)

JSON_SCHEMA_HINT = """
Return output strictly conforming to this JSON format:
{
  "summary": "High-level guidance summary",
  "current_position": "Statement of user's current match position",
  "why_this_opportunity_fits": "Clear explanation of why scheme matches profile",
  "priority_actions": [
    {
      "requirement_id": "EXACT_REQUIREMENT_ID_FROM_CONTEXT",
      "title": "Action title",
      "explanation": "Why to focus on this and what to prepare",
      "priority": "HIGH | MEDIUM | LOW",
      "ordering_basis": "OFFICIAL_SEQUENCE | PLANNING_GUIDANCE"
    }
  ],
  "support_explanation": [
    {
      "support_id": "EXACT_SUPPORT_ID_FROM_CONTEXT",
      "support_type": "Support type label",
      "explanation": "What this support provides"
    }
  ],
  "goal_connection": "How this opportunity helps achieve the user's business goal",
  "important_note": "Crucial disclaimer or guidance note"
}
"""


from pathlib import Path

def load_local_dotenv():
    """Safely loads key-value pairs from .env file into os.environ if present."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"')
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass

load_local_dotenv()


class GeminiProvider:
    """Provider abstraction for Gemini API interaction."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        load_local_dotenv()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
        self.timeout_seconds = 10

    def is_available(self) -> bool:
        """Returns True if GEMINI_API_KEY is configured."""
        return bool(self.api_key and str(self.api_key).strip())

    def generate_copilot_explanation(
        self,
        trusted_context: Dict[str, Any],
        language: str = "English"
    ) -> Optional[Dict[str, Any]]:
        """Invokes Gemini REST API to generate structured pathway explanation.

        Returns parsed dict on success, or None on failure/missing key/timeout/error.
        """
        if not self.is_available():
            logger.info("GEMINI_API_KEY missing or empty. Skipping Gemini invocation.")
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        user_prompt = (
            f"Requested Language: {language}\n\n"
            f"VERIFIED CONTEXT FROM SCHEMEMITRA:\n"
            f"{json.dumps(trusted_context, indent=2)}\n\n"
            f"{JSON_SCHEMA_HINT}\n\n"
            f"Please generate the personalized explanation JSON in {language}."
        )

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                # Non‑200 status handling without leaking URL or API key
                if resp.status != 200:
                    logger.warning("Gemini API HTTPError %s | %s", resp.status, resp.reason)
                    return None

                resp_bytes = resp.read()
                # First parse the Google envelope JSON safely
                try:
                    envelope = json.loads(resp_bytes.decode("utf-8"))
                except json.JSONDecodeError as envelope_err:
                    logger.warning("Gemini API envelope JSON decode error: %s", envelope_err)
                    return None

                # Extract text from candidates
                candidates = envelope.get("candidates") or []
                if not candidates:
                    logger.warning("Gemini API returned no candidates")
                    return None

                first_cand = candidates[0]
                parts = first_cand.get("content", {}).get("parts", [])
                if not parts:
                    logger.warning("Gemini API candidate has no content parts")
                    return None

                text_content = parts[0].get("text", "")
                if not text_content:
                    logger.warning("Gemini API returned empty candidate text")
                    return None

                # Clean possible markdown formatting ```json ... ```
                cleaned = text_content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

                # Parse the model‑generated JSON
                try:
                    parsed = json.loads(cleaned)
                except json.JSONDecodeError as model_err:
                    logger.warning("Gemini model output JSON decode error: %s", model_err)
                    return None

                if isinstance(parsed, dict):
                    return parsed
                return None
        except urllib.error.HTTPError as http_err:
            # Capture status, reason, and a sanitized body (max 500 chars)
            try:
                body_bytes = http_err.read()
                body_str = body_bytes.decode("utf-8", errors="ignore")[:500]
                try:
                    body_json = json.loads(body_str)
                    safe_msg = body_json.get("error", {}).get("message", body_str)
                except json.JSONDecodeError:
                    safe_msg = body_str
            except Exception:
                safe_msg = ""
            logger.warning(
                "Gemini API HTTPError %s | %s | %s",
                http_err.code,
                http_err.reason,
                safe_msg,
            )
            return None
        except urllib.error.URLError as url_err:
            reason = getattr(url_err, "reason", str(url_err))
            logger.warning("Gemini API URLError: %s", reason)
            return None
        except (socket.timeout, TimeoutError):
            logger.warning("Gemini API request timed out after %s seconds", self.timeout_seconds)
            return None
        except Exception as e:
            logger.error("Unexpected error invoking Gemini API: %s", e)
            return None
