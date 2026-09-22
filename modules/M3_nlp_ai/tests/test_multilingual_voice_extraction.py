import pytest
from nlp.profile_extractor import ProfileExtractor
from nlp.rule_extractor import RuleExtractor


@pytest.fixture
def extractor():
    return ProfileExtractor()


@pytest.fixture
def rules():
    return RuleExtractor()


# ============================================================
# 1. ENGLISH BASELINE PRESERVATION TESTS
# ============================================================

def test_english_cs_engineering_full(extractor):
    text = "I completed B.Tech in Computer Science Engineering."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") == "Degree"
    assert profile.get("education_field") == "Computer Science"


def test_english_cse_abbreviation(extractor):
    text = "I am studying CSE."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"


def test_english_full_profile_statement(extractor):
    text = "I am 24 years old from Tamil Nadu and want to start a food processing business."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("age") == 24
    assert profile.get("state") == "Tamil Nadu"
    assert profile.get("sector") == "Food Processing & Agri Value Addition"
    assert profile.get("business_type") == "Idea"


def test_english_btech_cs_and_food_processing(extractor):
    text = "I completed B.Tech in Computer Science and Engineering and want to start a food processing business."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") == "Degree"
    assert profile.get("education_field") == "Computer Science"
    assert profile.get("sector") == "Food Processing & Agri Value Addition"


def test_english_financial_expressions(extractor):
    t1 = "I have two lakh rupees available capital."
    res1 = extractor.extract(t1, use_llm="never")
    assert res1["profile"].get("available_capital") == 200000.0

    t2 = "My project will cost around five lakh rupees."
    res2 = extractor.extract(t2, use_llm="never")
    assert res2["profile"].get("project_cost") == 500000.0


# ============================================================
# 2. TAMIL EXTRACTION TESTS
# ============================================================

def test_tamil_cs_engineering_native(extractor):
    text = "நான் கம்ப்யூட்டர் சயின்ஸ் இன்ஜினியரிங் படிக்கிறேன்"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"


def test_tamil_btech_cs(extractor):
    text = "நான் பி.டெக் கம்ப்யூட்டர் சயின்ஸ் படித்தேன்"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") == "Degree"
    assert profile.get("education_field") == "Computer Science"


def test_tamil_branch_cse(extractor):
    text = "என்னுடைய branch CSE"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"


def test_tamil_state_and_sector(extractor):
    text = "நான் தமிழ்நாடு மற்றும் உணவு பதப்படுத்துதல் தொழில் தொடங்க விரும்புகிறேன்"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("state") == "Tamil Nadu"
    assert profile.get("sector") in ["Food Processing & Agri Value Addition", "Food Processing", "Food"]


# ============================================================
# 3. HINDI EXTRACTION TESTS
# ============================================================

def test_hindi_cs_engineering_native(extractor):
    text = "मैं कंप्यूटर साइंस इंजीनियरिंग पढ़ रहा हूँ"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"


def test_hindi_btech_cs(extractor):
    text = "मैंने बीटेक कंप्यूटर साइंस किया है"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") == "Degree"
    assert profile.get("education_field") == "Computer Science"


def test_hindi_branch_cse(extractor):
    text = "मेरा branch CSE है"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"


def test_hindi_state_and_sector(extractor):
    text = "मैं तमिलनाडु से हूँ और फूड प्रोसेसिंग बिज़नेस शुरू करना चाहता हूँ"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("state") == "Tamil Nadu"
    assert profile.get("sector") in ["Food Processing & Agri Value Addition", "Food Processing", "Food"]


# ============================================================
# 4. CODE-SWITCHED EXTRACTION TESTS
# ============================================================

def test_code_switch_tamil_english_btech(extractor):
    text = "நான் B.Tech Computer Science Engineering படிக்கிறேன்"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") == "Degree"
    assert profile.get("education_field") == "Computer Science"


def test_code_switch_hindi_english_btech(extractor):
    text = "मैं B.Tech Computer Science Engineering second year में हूँ"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") == "Degree"
    assert profile.get("education_field") == "Computer Science"


def test_code_switch_english_tamil_intent(extractor):
    text = "I am from Chennai, நான் food processing business start பண்ணணும்"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("district") == "Chennai"
    assert profile.get("state") == "Tamil Nadu"
    assert profile.get("sector") == "Food Processing & Agri Value Addition"


def test_code_switch_english_hindi_intent(extractor):
    text = "I live in Chennai and मुझे manufacturing business शुरू करना है"
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("district") == "Chennai"
    assert profile.get("state") == "Tamil Nadu"
    assert profile.get("sector") == "MSME & Manufacturing"


# ============================================================
# 5. NEGATIVE TESTS
# ============================================================

def test_negative_computer_usage(extractor):
    text = "I use a computer every day."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") is None


def test_negative_engineering_businesses(extractor):
    text = "I like engineering businesses."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") is None
    assert profile.get("education_field") is None


def test_negative_third_party_cse(extractor):
    text = "I know someone studying CSE."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") is None


def test_negative_friend_btech(extractor):
    text = "My friend completed B.Tech in Computer Science."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education") is None
    assert profile.get("education_field") is None


# ============================================================
# 6. STT SPEECH VARIANT RECOGNITION TESTS
# ============================================================

def test_stt_variant_computer_signs(extractor):
    text = "I studied computer signs engineering."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"


def test_stt_variant_computer_engineer(extractor):
    text = "I am a computer science engineer."
    res = extractor.extract(text, use_llm="never")
    profile = res["profile"]
    assert profile.get("education_field") == "Computer Science"
