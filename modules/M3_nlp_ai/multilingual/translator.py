"""Translation abstraction.

The project does not silently call an external translation service.  A caller
may inject a translator function or an LLM-backed translator.  If neither is
configured, the original text is returned with a status flag, allowing the
assistant to keep working without network access.
"""

from typing import Callable, Optional


class Translator:
    def __init__(self, translate_callable: Optional[Callable] = None):
        self.translate_callable = translate_callable

    def translate(self, text: str, source_language: str, target_language: str = "English") -> dict:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip() or source_language == target_language:
            return {
                "text": text,
                "translated": False,
                "source_language": source_language,
                "target_language": target_language,
                "status": "NOT_NEEDED",
            }

        if self.translate_callable is None:
            return {
                "text": text,
                "translated": False,
                "source_language": source_language,
                "target_language": target_language,
                "status": "TRANSLATOR_NOT_CONNECTED",
            }

        translated = self.translate_callable(
            text=text,
            source_language=source_language,
            target_language=target_language,
        )

        if not isinstance(translated, str) or not translated.strip():
            return {
                "text": text,
                "translated": False,
                "source_language": source_language,
                "target_language": target_language,
                "status": "TRANSLATION_FAILED",
            }

        return {
            "text": translated,
            "translated": True,
            "source_language": source_language,
            "target_language": target_language,
            "status": "OK",
        }
