from ai.ai_assistant import AIAssistant
from multilingual.translator import Translator


def test_conflict_can_be_resolved_on_next_turn():
    ai = AIAssistant()
    ai.process_message("I am 24")
    conflict = ai.process_message("Actually I am 25")
    assert conflict["conflicts"]
    resolved = ai.process_message("25")
    assert ai.profile["age"] == 25
    assert resolved["conflicts"] == []


def test_support_needs_merge_across_turns():
    ai = AIAssistant()
    ai.process_message("I need training")
    ai.process_message("I also need help marketing my products")
    assert set(ai.profile["support_needs"]) >= {"TRAINING", "MARKET_SUPPORT"}


def test_translator_graceful_without_provider():
    result = Translator().translate("வணக்கம்", "Tamil", "English")
    assert result["translated"] is False
    assert result["status"] == "TRANSLATOR_NOT_CONNECTED"
