"""Regression tests for M3 profile extraction and M2 adapter boundary.

Ensures accurate fact extraction, normalization to canonical M1 taxonomy,
preservation of explicit negative evidence, and zero eligibility decisions in M3.
"""

import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.M3_nlp_ai.nlp.profile_extractor import ProfileExtractor
from modules.M3_nlp_ai.nlp.m2_adapter import build_m2_profile
from server.adapters import sanitize_profile


EXACT_TEST_INPUT = (
    "I am a 24-year-old woman from Tamil Nadu. I have completed my degree and "
    "I want to start a food processing business. My annual family income is ₹3 lakh "
    "and I can invest around ₹2 lakh of my own money. I am looking for financial support, "
    "subsidy and training. I have not registered my business yet and I don't have "
    "Udyam registration or FSSAI registration."
)


def test_exact_user_input_extraction_and_adaptation():
    extractor = ProfileExtractor()
    m3_result = extractor.extract(EXACT_TEST_INPUT)

    # Verify M3 output contains no eligibility decision
    assert "eligible" not in m3_result
    assert "ineligible" not in m3_result
    assert "eligibility_status" not in m3_result
    assert "recommendations" not in m3_result

    profile = m3_result["profile"]

    # 1. Fact assertions
    assert profile.get("age") == 24
    assert profile.get("gender") == "Female"
    assert profile.get("state") == "Tamil Nadu"
    assert profile.get("education") == "Degree"
    assert profile.get("income") == 300000
    assert profile.get("available_capital") == 200000

    # 2. Sector canonicalization to exact M1 value
    assert profile.get("sector") == "Food Processing & Agri Value Addition"

    # 3. Business stage semantics: intending to start an unregistered business -> Idea
    assert profile.get("business_stage") == "Idea"

    # 4. Support needs/preferences preserve Finance/Credit, Subsidy, Training
    needs = profile.get("support_needs", [])
    assert "SUBSIDY" in needs
    assert "TRAINING" in needs
    assert "CREDIT" in needs

    # 5. Explicit missing registration evidence
    missing_regs = profile.get("missing_registrations", [])
    assert "UDYAM" in missing_regs
    assert "FSSAI" in missing_regs
    assert profile.get("unregistered_business") is True

    # 6. Unspecified fields remain unknown / None
    assert profile.get("category") is None
    assert profile.get("project_cost") is None

    # Test M2 Adapter payload
    m2_profile = build_m2_profile(profile)
    assert m2_profile["age"] == 24
    assert m2_profile["gender"] == "Female"
    assert m2_profile["state"] == "Tamil Nadu"
    assert m2_profile["education"] == "Degree"
    assert m2_profile["annual_income"] == 300000
    assert m2_profile["sector"] == "Food Processing & Agri Value Addition"
    assert m2_profile["business_stage"] == "Idea"
    assert m2_profile["existing_business"] is False
    assert m2_profile["extra"]["available_capital"] == 200000
    assert "UDYAM" in m2_profile["extra"]["missing_registrations"]
    assert "FSSAI" in m2_profile["extra"]["missing_registrations"]
    assert m2_profile["extra"]["unregistered_business"] is True
    assert m2_profile["category"] is None
    assert m2_profile["project_cost"] is None

    # Test Server Profile Sanitization
    sanitized = sanitize_profile(profile)
    assert sanitized["age"] == 24
    assert sanitized["gender"] == "Female"
    assert sanitized["state"] == "Tamil Nadu"
    assert sanitized["education"] == "Degree"
    assert sanitized["annual_income"] == 300000
    assert sanitized["available_capital"] == 200000
    assert sanitized["sector"] == "Food Processing & Agri Value Addition"
    assert sanitized["business_stage"] == "Idea"
    assert sanitized["category"] is None
    assert sanitized["project_cost"] is None
    assert "UDYAM" in sanitized["extra"]["missing_registrations"]
    assert "FSSAI" in sanitized["extra"]["missing_registrations"]
    assert sanitized["extra"]["unregistered_business"] is True


def test_hyphenated_age_extraction():
    extractor = ProfileExtractor()
    res = extractor.extract("I am a 24-year-old female looking for schemes.")
    assert res["profile"]["age"] == 24


def test_lakh_income_extraction():
    extractor = ProfileExtractor()
    res = extractor.extract("My annual family income is ₹3 lakh")
    assert res["profile"]["income"] == 300000


def test_available_capital_suffix_extraction():
    extractor = ProfileExtractor()
    res = extractor.extract("I can invest around ₹2 lakh of my own money")
    assert res["profile"]["available_capital"] == 200000


def test_food_processing_exact_m1_canonical_sector():
    extractor = ProfileExtractor()
    res = extractor.extract("I want to start a food processing business")
    assert res["profile"]["sector"] == "Food Processing & Agri Value Addition"


def test_want_to_start_not_promoted_to_established_business():
    extractor = ProfileExtractor()
    res = extractor.extract("I want to start a business")
    assert res["profile"]["business_stage"] == "Idea"
    assert res["profile"].get("existing_business") is not True


def test_explicit_missing_registrations_retained():
    extractor = ProfileExtractor()
    res = extractor.extract("I don't have Udyam registration and I don't have FSSAI registration.")
    assert "UDYAM" in res["profile"]["missing_registrations"]
    assert "FSSAI" in res["profile"]["missing_registrations"]


def test_unspecified_category_and_project_cost_remain_unknown():
    extractor = ProfileExtractor()
    res = extractor.extract("I am 24 from Tamil Nadu.")
    assert res["profile"].get("category") is None
    assert res["profile"].get("project_cost") is None


def test_m3_output_contains_no_eligibility_decision():
    extractor = ProfileExtractor()
    res = extractor.extract("I am 24 from Tamil Nadu wanting to start a business.")
    assert "eligible" not in res
    assert "ineligible" not in res
    assert "eligibility_status" not in res
    assert "recommendation" not in res
