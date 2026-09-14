from ai.ai_assistant import AIAssistant


# ============================================================
# HELPERS
# ============================================================

def run_conversation(messages):
    ai = AIAssistant()

    last_response = None

    for message in messages:
        last_response = ai.process_message(message)

    return ai, last_response


def ask_field(field, answer):
    ai = AIAssistant()
    ai.current_question = field

    result = ai.process_message(answer)

    return ai, result


# ============================================================
# GROUP 1 — NEGATION / CORRECTION INSIDE SAME MESSAGE
# ============================================================

def test_semantic_01_age_negation_then_correct_age():
    ai, result = run_conversation([
        "I am not 25, I am 24 and I want to start a food business"
    ])

    assert ai.profile["age"] == 24


def test_semantic_02_state_negation_then_correct_state():
    ai, result = run_conversation([
        "I don't live in Kerala, I live in Tamil Nadu"
    ])

    assert ai.profile["state"] == "Tamil Nadu"


def test_semantic_03_gender_negation_then_correct_gender():
    ai, result = run_conversation([
        "I am not female, I am male"
    ])

    assert ai.profile["gender"] == "Male"


def test_semantic_04_category_negation_should_not_extract_sc():
    ai, result = run_conversation([
        "I am not SC, I belong to General category"
    ])

    assert ai.profile["category"] == "General"


# ============================================================
# GROUP 2 — MULTIPLE NUMBERS WITH DIFFERENT MEANINGS
# ============================================================

def test_semantic_05_age_and_project_cost_same_message():
    ai, result = run_conversation([
        "I am 24 years old and my project will cost 2 lakh"
    ])

    assert ai.profile["age"] == 24
    assert ai.profile["project_cost"] == 200000


def test_semantic_06_income_and_project_cost_same_message():
    ai, result = run_conversation([
        "My income is 25000 and my project cost is 3 lakh"
    ])

    assert ai.profile["income"] == 25000
    assert ai.profile["project_cost"] == 300000


def test_semantic_07_age_income_project_cost_same_message():
    ai, result = run_conversation([
        "I am 26, my income is 30k and I need 5 lakh for the project"
    ])

    assert ai.profile["age"] == 26
    assert ai.profile["income"] == 30000
    assert ai.profile["project_cost"] == 500000


def test_semantic_08_phone_number_should_not_be_age():
    ai = AIAssistant()

    ai.process_message(
        "My phone number is 9876543210"
    )

    assert "age" not in ai.profile


def test_semantic_09_year_should_not_be_age():
    ai = AIAssistant()

    ai.process_message(
        "I started my business in 2024"
    )

    assert "age" not in ai.profile


# ============================================================
# GROUP 3 — OTHER PEOPLE'S INFORMATION
# ============================================================

def test_semantic_10_fathers_age_should_not_be_user_age():
    ai, result = run_conversation([
        "My father is 55 years old"
    ])

    assert "age" not in ai.profile


def test_semantic_11_user_age_with_fathers_age():
    ai, result = run_conversation([
        "My father is 55 but I am 24 years old"
    ])

    assert ai.profile["age"] == 24


def test_semantic_12_friend_state_should_not_be_user_state():
    ai, result = run_conversation([
        "My friend lives in Kerala but I live in Tamil Nadu"
    ])

    assert ai.profile["state"] == "Tamil Nadu"


# ============================================================
# GROUP 4 — BUSINESS STAGE SEMANTICS
# ============================================================

def test_semantic_13_planning_business_is_startup():
    ai, result = run_conversation([
        "I am planning to start a tailoring business"
    ])

    assert ai.profile["business_type"] in ["Idea", "Startup"]


def test_semantic_14_want_to_start_business_is_startup():
    ai, result = run_conversation([
        "I want to start a food business"
    ])

    assert ai.profile["business_type"] in ["Idea", "Startup"]


def test_semantic_15_existing_running_business():
    ai, result = run_conversation([
        "I already have a running food business"
    ])

    assert ai.profile["business_type"] == "Existing"


def test_semantic_16_operating_business_is_existing():
    ai, result = run_conversation([
        "I currently operate a tailoring business"
    ])

    assert ai.profile["business_type"] == "Existing"


# ============================================================
# GROUP 5 — CONTEXTUAL SHORT ANSWERS
# ============================================================

def test_semantic_17_age_answer_with_sentence():
    ai, result = ask_field(
        "age",
        "I am actually 24 years old"
    )

    assert ai.profile["age"] == 24


def test_semantic_18_income_answer_with_context():
    ai, result = ask_field(
        "income",
        "around 30k per year"
    )

    assert ai.profile["income"] == 30000


def test_semantic_19_project_cost_with_context():
    ai, result = ask_field(
        "project_cost",
        "I think around 2.5 lakh"
    )

    assert ai.profile["project_cost"] == 250000


def test_semantic_20_state_with_context():
    ai, result = ask_field(
        "state",
        "I currently live in Tamil Nadu"
    )

    assert ai.profile["state"] == "Tamil Nadu"


# ============================================================
# GROUP 6 — IRRELEVANT NUMBERS
# ============================================================

def test_semantic_21_quantity_should_not_be_age():
    ai = AIAssistant()

    ai.process_message(
        "I sell 50 products every month"
    )

    assert "age" not in ai.profile


def test_semantic_22_percentage_should_not_be_age():
    ai = AIAssistant()

    ai.process_message(
        "My profit margin is 25 percent"
    )

    assert "age" not in ai.profile


def test_semantic_23_shop_number_should_not_be_age():
    ai = AIAssistant()

    ai.process_message(
        "My shop number is 24"
    )

    assert "age" not in ai.profile


def test_semantic_24_years_experience_should_not_be_age():
    ai = AIAssistant()

    ai.process_message(
        "I have 20 years of experience in tailoring"
    )

    assert "age" not in ai.profile


# ============================================================
# GROUP 7 — MIXED LANGUAGE SEMANTICS
# ============================================================

def test_semantic_25_tanglish_age_and_business():
    ai, result = run_conversation([
        "enaku 24 vayasu, food business start panna poren"
    ])

    assert ai.profile["age"] == 24
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_semantic_26_hinglish_age_and_business():
    ai, result = run_conversation([
        "meri age 25 hai aur food business start karna hai"
    ])

    assert ai.profile["age"] == 25
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_semantic_27_tanglish_existing_business():
    ai, result = run_conversation([
        "already tailoring business run panren"
    ])

    assert ai.profile["sector"] == "MSME & Manufacturing"
    assert ai.profile["business_type"] == "Existing"


# ============================================================
# GROUP 8 — SAFE HANDLING OF AMBIGUOUS INPUT
# ============================================================

def test_semantic_28_only_number_without_question_should_not_guess():
    ai = AIAssistant()

    ai.process_message("24")

    assert "age" not in ai.profile


def test_semantic_29_currency_without_context_should_not_guess_field():
    ai = AIAssistant()

    ai.process_message("₹500000")

    assert "income" not in ai.profile
    assert "project_cost" not in ai.profile


def test_semantic_30_empty_and_noise_then_valid_message():
    ai = AIAssistant()

    ai.process_message("")
    ai.process_message("???!!!")
    ai.process_message("hello")
    ai.process_message(
        "I am 24 and I want to start a food business"
    )

    assert ai.profile["age"] == 24
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]