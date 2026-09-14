from modules.M3_nlp_ai.nlp.profile_extractor import ProfileExtractor
from modules.M3_nlp_ai.nlp.rule_extractor import RuleExtractor
from modules.M3_nlp_ai.nlp.validator import ProfileValidator
from server.adapters import sanitize_profile


def test_age_validation_rejects_zero_negative_and_over_120():
    for age in (0, -1, 121):
        assert sanitize_profile({"age": age})["age"] is None
        result = ProfileValidator().validate({"age": age})
        assert result["valid"] is False
    assert sanitize_profile({"age": 24})["age"] == 24
    assert ProfileValidator().validate({"age": 24})["valid"] is True


def test_age_validation_rejects_non_numeric_and_fractional_values():
    assert sanitize_profile({"age": "abc"})["age"] is None
    assert sanitize_profile({"age": 24.5})["age"] is None


def test_transgender_is_preserved_as_distinct_gender():
    assert sanitize_profile({"gender": "Transgender"})["gender"] == "Transgender"
    assert ProfileValidator().validate({"gender": "Transgender"})["valid"] is True


def test_education_level_course_and_field_extraction():
    extractor = ProfileExtractor()
    cases = [
        ("I completed B.Tech in Computer Science", "Degree", "B.Tech", "Computer Science"),
        ("I completed BE CSE", "Degree", "B.E.", "Computer Science"),
        ("BSc Computer Science", "Degree", "B.Sc", "Computer Science"),
        ("BCA", "Degree", "BCA", "Computer Applications"),
        ("B.Com", "Degree", "B.Com", "Commerce"),
        ("BBA", "Degree", "BBA", "Business Administration"),
        ("BA Economics", "Degree", "B.A.", "Economics"),
        ("M.Tech Artificial Intelligence", "Postgraduate", "M.Tech", "Artificial Intelligence"),
        ("MCA", "Postgraduate", "MCA", "Computer Applications"),
        ("MBA Finance", "Postgraduate", "MBA", "Finance"),
        ("MSc Data Science", "Postgraduate", "M.Sc", "Data Science"),
        ("Diploma in Mechanical Engineering", "Diploma", "Diploma", "Mechanical Engineering"),
        ("ITI electrician", "ITI", "ITI", "Electrician"),
        ("12th pass", "12th Pass", "12th", None),
        ("10th pass", "10th Pass", "10th", None),
        ("8th pass", "8th Pass", "8th", None),
    ]
    for text, level, course, field in cases:
        profile = extractor.extract(text, use_llm="never")["profile"]
        assert profile.get("education") == level
        if course:
            assert profile.get("education_course") == course
        if field:
            assert profile.get("education_field") == field


def test_standalone_field_does_not_infer_degree_completion():
    profile = ProfileExtractor().extract("computer science", use_llm="never")["profile"]
    assert profile.get("education") is None
    assert profile.get("education_course") is None
    assert profile.get("education_field") == "Computer Science"


def test_education_statement_does_not_become_business_sector():
    profile = ProfileExtractor().extract("I completed B.Tech in Computer Science", use_llm="never")["profile"]
    assert profile.get("sector") is None


def test_india_wide_location_resolver():
    rules = RuleExtractor()
    locations = [
        ("I live in Madurai", "Madurai", "Tamil Nadu"),
        ("I am from Mysuru", "Mysuru", "Karnataka"),
        ("I live in Pune", "Pune", "Maharashtra"),
        ("I live in Kochi", "Ernakulam", "Kerala"),
        ("I am from Lucknow", "Lucknow", "Uttar Pradesh"),
        ("I stay in Jaipur", "Jaipur", "Rajasthan"),
        ("I live in Coimbatore", "Coimbatore", "Tamil Nadu"),
    ]
    for text, exp_district, exp_state in locations:
        res = rules.extract(text)
        assert res.get("district") == exp_district
        assert res.get("state") == exp_state


def test_third_party_location_is_not_assigned_to_user():
    rules = RuleExtractor()
    assert rules.extract("My friend lives in Pune").get("state") is None
    assert rules.extract("My friend lives in Pune").get("district") is None
    assert rules.extract("My friend lives in Chennai").get("state") is None
    assert rules.extract("My friend lives in Chennai").get("district") is None
    assert rules.extract("My friend is from Tamil Nadu").get("state") is None


def test_business_activity_and_sector_classification():
    rules = RuleExtractor()
    assert rules.extract("I want to open a bakery")["sector"] == "Food Processing & Agri Value Addition"
    assert rules.extract("I want to start dairy farming")["sector"] == "Agriculture & Allied"
    assert rules.extract("I manufacture paper bags")["sector"] == "MSME & Manufacturing"
    assert rules.extract("I make pottery")["sector"] == "Handicrafts, Handloom & Artisan Economy"
    assert rules.extract("I want to export spices")["sector"] == "Export, Market Access & Business Growth"

    # E-commerce non-overclassification test
    eshop = rules.extract("I want to build an e-shop")
    assert eshop["sector"] == "MSME & Manufacturing"

    # B.Tech education term must NOT trigger Startup & Innovation for standard e-shop
    btech_eshop = rules.extract("I completed B.Tech Computer Science and want to create an e-shop.")
    assert btech_eshop["sector"] == "MSME & Manufacturing"

    # Genuine innovation/startup intent correctly classifies as Startup & Innovation
    ai_startup = rules.extract("I want to build an AI-powered e-commerce startup.")
    assert ai_startup["sector"] == "Startup & Innovation"


def test_under_18_profile_preserved():
    profile = {"age": 15, "state": "Tamil Nadu"}
    from server.app import build_under18_applicability_response
    eval_result = build_under18_applicability_response(profile)
    assert eval_result["applicability"]["personalized_matching_available"] is False
    assert eval_result["profile"]["age"] == 15

