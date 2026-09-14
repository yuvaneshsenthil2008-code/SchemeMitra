import pytest
from ai.ai_assistant import AIAssistant
from nlp.m2_adapter import build_m2_profile


def test_explicit_preference_is_separate_from_inferred_needs():
    ai = AIAssistant()
    ai.set_preferred_support_types(["LOAN"])
    ai.process_message("I need help marketing my products")
    assert ai.profile["preferred_support_types"] == ["LOAN"]
    assert "MARKET_SUPPORT" in ai.profile["support_needs"]


def test_loan_language_infers_need_not_preference():
    ai = AIAssistant()
    ai.process_message("I need a loan to buy machinery")
    assert "LOAN" in ai.profile["support_needs"]
    assert "EQUIPMENT_SUPPORT" in ai.profile["support_needs"]
    assert "preferred_support_types" not in ai.profile


def test_business_goal_start_is_exported():
    ai = AIAssistant()
    ai.process_message("I want to start a food business")
    assert ai.export_for_m2()["business_goal"] == "START_BUSINESS"


def test_business_goal_grow_is_exported():
    ai = AIAssistant()
    ai.process_message("I want to expand my existing food business")
    assert ai.export_for_m2()["business_goal"] == "GROW_BUSINESS"


def test_monthly_income_is_annualized_only_at_m2_boundary():
    ai = AIAssistant()
    ai.process_message("My monthly income is 25000")
    assert ai.profile["income"] == 25000
    assert ai.profile["income_period"] == "monthly"
    assert ai.export_for_m2()["annual_income"] == 300000


def test_annual_income_is_not_multiplied():
    profile = {"income": 300000, "income_period": "annual", "business_type": "Startup"}
    result = build_m2_profile(profile)
    assert result["annual_income"] == 300000
    assert result["business_stage"] == "Startup"


def test_m2_contract_uses_canonical_names():
    ai = AIAssistant()
    ai.process_message("I am 24 and I want to start a food business")
    payload = ai.to_m2_payload()
    assert "profile" in payload
    assert "annual_income" in payload["profile"]
    assert "business_stage" in payload["profile"]
    assert "income" not in payload["profile"]
    assert "business_type" not in payload["profile"]


def test_preference_aliases_are_normalized():
    ai = AIAssistant()
    assert ai.set_preferred_support_types(["loan", "market support"]) == ["LOAN", "MARKET_SUPPORT"]


def test_invalid_preference_is_rejected():
    ai = AIAssistant()
    with pytest.raises(ValueError):
        ai.set_preferred_support_types(["MAGIC_SUPPORT"])
