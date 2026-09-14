from nlp.entity_extractor import EntityExtractor


def test_contextual_typo_state():
    assert EntityExtractor().extract_contextual("tamilnaduu", "state")["state"] == "Tamil Nadu"


def test_contextual_money_lakh():
    assert EntityExtractor().extract_contextual("2.5 lakh", "project_cost")["project_cost"] == 250000


def test_no_guess_from_bare_currency_without_question():
    assert EntityExtractor().extract("₹500000") == {}
