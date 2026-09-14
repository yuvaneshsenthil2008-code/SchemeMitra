from ai.ai_assistant import AIAssistant
from nlp.language_detector import LanguageDetector
from nlp.profile_extractor import ProfileExtractor


def test_telugu_script_detection():
    d = LanguageDetector().detect_detail("నాకు వ్యాపారం ప్రారంభించాలి")
    assert d["language"] == "Telugu"


def test_kannada_script_detection():
    assert LanguageDetector().detect("ನನಗೆ ವ್ಯವಹಾರ ಆರಂಭಿಸಬೇಕು") == "Kannada"


def test_malayalam_script_detection():
    assert LanguageDetector().detect("എനിക്ക് ബിസിനസ് തുടങ്ങണം") == "Malayalam"


def test_bengali_script_detection():
    assert LanguageDetector().detect("আমি ব্যবসা শুরু করতে চাই") == "Bengali"


def test_mixed_tamil_english_detection():
    d = LanguageDetector().detect_detail("எனக்கு food business தொடங்க வேண்டும்")
    assert d["language"] == "Mixed"
    assert d["primary_language"] == "Tamil"


def test_telugu_profile_basics():
    result = ProfileExtractor().extract("నా వయస్సు 26. తెలంగాణలో ఆహారం వ్యాపారం ప్రారంభించాలి")
    p = result["profile"]
    assert p["age"] == 26
    assert p["state"] == "Telangana"
    assert p["sector"] == "Food Processing & Agri Value Addition"
    assert p["business_type"] in ["Startup", "Idea"]


def test_mixed_language_assistant_keeps_primary_native_prompt():
    ai = AIAssistant()
    r = ai.process_message("எனக்கு food business தொடங்க வேண்டும்")
    assert r["language"] == "Tamil"
    assert r["current_question"] == "age"
