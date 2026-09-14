from nlp.intent_detector import IntentDetector


def test_intent_opportunity():
    assert IntentDetector().detect("I need a loan for my business")["intent"] == "OPPORTUNITY"


def test_intent_general():
    assert IntentDetector().detect("What is the weather today?")["intent"] == "GENERAL_QUERY"


def test_intent_greeting_is_not_opportunity():
    assert IntentDetector().detect("Hello, how are you?")["intent"] == "UNKNOWN"
