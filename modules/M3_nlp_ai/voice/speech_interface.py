"""Optional speech-to-text and text-to-speech integration.

Voice libraries are intentionally optional so the NLP core remains usable on
servers and during tests.  Install SpeechRecognition and pyttsx3 only when the
frontend needs local voice support.
"""


class SpeechInterface:
    def transcribe_microphone(self, language_code: str = "en-IN") -> dict:
        try:
            import speech_recognition as sr
        except ImportError:
            return {
                "success": False,
                "text": "",
                "error": "SpeechRecognition is not installed.",
            }

        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language=language_code)
            return {"success": True, "text": text, "error": None}
        except Exception as exc:  # Device/network errors must not crash M3.
            return {"success": False, "text": "", "error": str(exc)}

    def speak(self, text: str, language_code: str = "en-IN") -> dict:
        del language_code  # pyttsx3 voice selection is OS-specific.
        try:
            import pyttsx3
        except ImportError:
            return {
                "success": False,
                "error": "pyttsx3 is not installed.",
            }

        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return {"success": True, "error": None}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
