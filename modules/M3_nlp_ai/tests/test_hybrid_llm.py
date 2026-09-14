from nlp.llm_extractor import LLMExtractor
from nlp.profile_extractor import ProfileExtractor


def fake_client(**kwargs):
    return {
        "age": 27,
        "state": "Telangana",
        "education": "Degree",
        "sector": "Technology",
        "business_type": "Startup",
    }


def test_hybrid_llm_can_fill_missing_rule_fields():
    llm = LLMExtractor(client=fake_client)
    ex = ProfileExtractor(llm_extractor=llm)
    result = ex.extract("నాకు కొత్త వ్యాపారం గురించి సహాయం కావాలి", use_llm="always")
    assert result["profile"]["age"] == 27
    assert result["profile"]["state"] == "Telangana"
    assert result["confidence"]["age"]["source"] == "llm"
    assert result["hybrid"]["llm_used"] is True


def test_rule_value_has_priority_over_llm_value():
    llm = LLMExtractor(client=lambda **kwargs: {"age": 25, "state": "Kerala"})
    ex = ProfileExtractor(llm_extractor=llm)
    result = ex.extract("I am 24 and I live in Tamil Nadu", use_llm="always")
    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"
    fields = {c["field"] for c in result["conflicts"]}
    assert {"age", "state"}.issubset(fields)


def test_llm_prompt_forbids_preferred_support_inference():
    prompt = LLMExtractor().build_prompt("I need funding", "English")
    assert "Do not create preferred_support_types" in prompt


def test_unconnected_llm_does_not_break_pipeline():
    result = ProfileExtractor().extract("I want to start a food business")
    assert result["profile"]["sector"] == "Food Processing & Agri Value Addition"
    assert result["hybrid"]["llm_used"] is False
