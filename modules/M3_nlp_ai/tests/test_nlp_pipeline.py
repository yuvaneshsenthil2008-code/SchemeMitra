from nlp.profile_extractor import ProfileExtractor


def test_complete_profile():
    extractor = ProfileExtractor()

    text = (
        "I am a 24 year old female from Tamil Nadu. "
        "I am a graduate, belong to SC category, "
        "and want to start a food business. "
        "My monthly income is 20000 and the project cost is 500000."
    )

    result = extractor.extract(text)

    assert result["intent"]["intent"] == "OPPORTUNITY"

    profile = result["profile"]

    assert profile["age"] == 24
    assert profile["gender"] == "Female"
    assert profile["state"] == "Tamil Nadu"
    assert profile["education"] == "Degree"
    assert profile["category"] == "SC"
    assert profile["sector"] == "Food Processing & Agri Value Addition"
    assert profile["business_type"] in ["Startup", "Idea"]
    assert profile["income"] == 20000
    assert profile["project_cost"] == 500000

    assert result["validation"]["valid"] is True

    assert result["missing_info"]["complete"] is True
    assert result["missing_info"]["missing_fields"] == []


def test_incomplete_profile():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "I want to start a food business"
    )

    assert result["intent"]["intent"] == "OPPORTUNITY"

    profile = result["profile"]

    assert profile["sector"] == "Food Processing & Agri Value Addition"
    assert profile["business_type"] in ["Startup", "Idea"]

    missing = result["missing_info"]["missing_fields"]

    assert "age" in missing
    assert "gender" in missing
    assert "state" in missing
    assert "education" in missing
    assert "category" in missing
    assert "income" in missing
    assert "project_cost" in missing

    assert result["missing_info"]["complete"] is False


def test_invalid_age():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "I am 150 years old and want to start a food business"
    )

    assert result["profile"]["age"] == 150

    assert result["validation"]["valid"] is False

    assert any(
        "Age must be between 1 and 120"
        in error
        for error in result["validation"]["errors"]
    )


def test_conflicting_information():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "I am 24 years old and want to start a food business",
        llm_response={
            "age": 25,
            "sector": "Food"
        }
    )

    assert len(result["conflicts"]) > 0

    age_conflict = next(
        conflict
        for conflict in result["conflicts"]
        if conflict["field"] == "age"
    )

    assert age_conflict["rule_value"] == 24
    assert age_conflict["llm_value"] == 25
    assert age_conflict["action"] == "ASK_USER"


def test_llm_fallback():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "I want government support for my business",
        llm_response={
            "age": 24,
            "state": "Tamil Nadu",
            "education": "Degree",
            "sector": "Food"
        }
    )

    profile = result["profile"]

    assert profile["age"] == 24
    assert profile["state"] == "Tamil Nadu"
    assert profile["education"] == "Degree"
    assert profile["sector"] == "Food Processing & Agri Value Addition"

    assert result["confidence"]["age"]["source"] == "llm"
    assert result["confidence"]["age"]["confidence"] == 0.85


def test_irrelevant_query():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "What is the weather today?"
    )

    assert result["intent"]["intent"] == "GENERAL_QUERY"
    assert result["intent"]["relevant"] is False

    assert result["profile"] == {}


def test_unknown_query():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "Hello, how are you?"
    )

    assert result["intent"]["intent"] == "UNKNOWN"
    assert result["intent"]["action"] == "ASK_CLARIFICATION"

    assert result["profile"] == {}


def test_empty_input():
    extractor = ProfileExtractor()

    result = extractor.extract("")

    assert result["intent"]["intent"] == "UNKNOWN"
    assert result["profile"] == {}

    assert result["missing_info"]["complete"] is False


def test_tanglish_profile():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "Enakku 24 vayasu, Tamil Nadu la irukken, "
        "food business start panna poren"
    )

    assert result["language"] == "Tanglish"

    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["profile"]["sector"] == "Food Processing & Agri Value Addition"
    assert result["profile"]["business_type"] in ["Startup", "Idea"]


def test_tamil_profile():
    extractor = ProfileExtractor()

    result = extractor.extract(
        "எனக்கு 24 வயது. தமிழ்நாட்டில் உணவு தொழில் தொடங்க விரும்புகிறேன்."
    )

    assert result["language"] == "Tamil"

    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"