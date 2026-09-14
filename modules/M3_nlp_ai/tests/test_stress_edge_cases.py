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
    """
    Simulates the AI currently asking for one specific field.
    """
    ai = AIAssistant()
    ai.current_question = field

    result = ai.process_message(answer)

    return ai, result


# ============================================================
# GROUP 1 — COMMON SPELLING / TYPING VARIATIONS
# ============================================================

def test_edge_01_tamilnadu_typo():
    ai, result = ask_field(
        "state",
        "tamilnaduu"
    )

    assert ai.profile["state"] == "Tamil Nadu"


def test_edge_02_tamil_nadu_typo_with_space():
    ai, result = ask_field(
        "state",
        "tamil naduu"
    )

    assert ai.profile["state"] == "Tamil Nadu"


def test_edge_03_degree_typo():
    ai, result = ask_field(
        "education",
        "dgree"
    )

    assert ai.profile["education"] == "Degree"


def test_edge_04_general_typo():
    ai, result = ask_field(
        "category",
        "genral"
    )

    assert ai.profile["category"] == "General"


def test_edge_05_female_typo():
    ai, result = ask_field(
        "gender",
        "femle"
    )

    assert ai.profile["gender"] == "Female"


def test_edge_06_tanglish_age_typo():
    ai, result = ask_field(
        "age",
        "enaku 24 vaysu"
    )

    assert ai.profile["age"] == 24


# ============================================================
# GROUP 2 — MONEY FORMAT ROBUSTNESS
# ============================================================

def test_edge_07_income_25_thousand():
    ai, result = ask_field(
        "income",
        "25 thousand"
    )

    assert ai.profile["income"] == 25000


def test_edge_08_project_cost_two_lac():
    ai, result = ask_field(
        "project_cost",
        "2 lac"
    )

    assert ai.profile["project_cost"] == 200000


def test_edge_09_project_cost_two_point_five_l():
    ai, result = ask_field(
        "project_cost",
        "2.5L"
    )

    assert ai.profile["project_cost"] == 250000


def test_edge_10_project_cost_one_cr():
    ai, result = ask_field(
        "project_cost",
        "1cr"
    )

    assert ai.profile["project_cost"] == 10000000


def test_edge_11_income_rupees_with_slash():
    ai, result = ask_field(
        "income",
        "₹25,000/-"
    )

    assert ai.profile["income"] == 25000


def test_edge_12_invalid_double_k_not_silently_parsed():
    ai, result = ask_field(
        "income",
        "25kk"
    )

    assert "income" not in ai.profile


# ============================================================
# GROUP 3 — MIXED-LANGUAGE MONEY
# ============================================================

def test_edge_13_tanglish_income():
    ai, result = ask_field(
        "income",
        "en income 25k"
    )

    assert ai.profile["income"] == 25000


def test_edge_14_hinglish_income():
    ai, result = ask_field(
        "income",
        "mera income 30k hai"
    )

    assert ai.profile["income"] == 30000


def test_edge_15_hinglish_project_cost():
    ai, result = ask_field(
        "project_cost",
        "mera budget 2 lakh hai"
    )

    assert ai.profile["project_cost"] == 200000


def test_edge_16_tanglish_project_cost():
    ai, result = ask_field(
        "project_cost",
        "business ku 3 lakh venum"
    )

    assert ai.profile["project_cost"] == 300000


# ============================================================
# GROUP 4 — WRONG TYPE / OUT-OF-ORDER ANSWERS
# ============================================================

def test_edge_17_state_given_when_age_was_asked():
    ai = AIAssistant()

    ai.process_message(
        "I want to start a food business"
    )

    assert ai.current_question == "age"

    ai.process_message("Tamil Nadu")

    assert ai.profile["state"] == "Tamil Nadu"
    assert "age" not in ai.profile


def test_edge_18_gender_given_when_age_was_asked():
    ai = AIAssistant()

    ai.process_message(
        "I want to start a food business"
    )

    assert ai.current_question == "age"

    ai.process_message("Male")

    assert ai.profile["gender"] == "Male"
    assert "age" not in ai.profile


def test_edge_19_education_given_early():
    ai = AIAssistant()

    ai.process_message(
        "I want to start a food business"
    )

    ai.process_message("Degree")

    assert ai.profile["education"] == "Degree"
    assert "age" not in ai.profile


def test_edge_20_multiple_out_of_order_fields():
    ai = AIAssistant()

    ai.process_message(
        "I want to start a food business"
    )

    ai.process_message("Tamil Nadu")
    ai.process_message("Degree")
    ai.process_message("Male")

    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["education"] == "Degree"
    assert ai.profile["gender"] == "Male"
    assert "age" not in ai.profile


# ============================================================
# GROUP 5 — CORRECTIONS / REPEATED INFORMATION
# ============================================================

def test_edge_21_repeated_identical_information():
    ai = AIAssistant()

    ai.process_message(
        "I am 24 and want to start a food business"
    )

    first_profile = ai.profile.copy()

    result = ai.process_message(
        "I am 24"
    )

    assert ai.profile["age"] == 24
    assert result["conflicts"] == []
    assert ai.profile["age"] == first_profile["age"]


def test_edge_22_multiple_age_corrections_preserve_original():
    ai = AIAssistant()

    ai.process_message(
        "I am 24 and want to start a food business"
    )

    first_conflict = ai.process_message(
        "Actually I am 25"
    )

    second_conflict = ai.process_message(
        "No, I am 26"
    )

    assert ai.profile["age"] == 24

    assert any(
        conflict["field"] == "age"
        for conflict in first_conflict["conflicts"]
    )

    assert any(
        conflict["field"] == "age"
        for conflict in second_conflict["conflicts"]
    )


def test_edge_23_repeated_state_does_not_conflict():
    ai = AIAssistant()

    ai.process_message(
        "I live in Tamil Nadu"
    )

    result = ai.process_message(
        "Tamil Nadu"
    )

    assert ai.profile["state"] == "Tamil Nadu"
    assert result["conflicts"] == []


def test_edge_24_state_correction_is_detected():
    ai = AIAssistant()

    ai.process_message(
        "I live in Tamil Nadu"
    )

    result = ai.process_message(
        "Actually Kerala"
    )

    assert ai.profile["state"] == "Tamil Nadu"

    assert any(
        conflict["field"] == "state"
        for conflict in result["conflicts"]
    )


# ============================================================
# GROUP 6 — LANGUAGE SWITCHING
# ============================================================

def test_edge_25_tamil_to_english_answers():
    ai = AIAssistant()

    ai.process_message(
        "தமிழ்நாட்டில் உணவு தொழில் தொடங்க விரும்புகிறேன்"
    )

    ai.process_message("24")
    ai.process_message("Male")
    ai.process_message("Degree")

    assert ai.profile["age"] == 24
    assert ai.profile["gender"] == "Male"
    assert ai.profile["education"] == "Degree"
    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"


def test_edge_26_english_to_tanglish_answers():
    ai = AIAssistant()

    ai.process_message(
        "I want to start a food business"
    )

    ai.process_message("enaku 24 vayasu")
    ai.process_message("aan")
    ai.process_message("Tamil Nadu")
    ai.process_message("degree mudichiten")

    assert ai.profile["age"] == 24
    assert ai.profile["gender"] == "Male"
    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["education"] == "Degree"


# ============================================================
# GROUP 7 — NOISY / REALISTIC INPUT
# ============================================================

def test_edge_27_age_with_heavy_punctuation():
    ai, result = ask_field(
        "age",
        "Age::: 24!!!"
    )

    assert ai.profile["age"] == 24


def test_edge_28_state_with_punctuation():
    ai, result = ask_field(
        "state",
        "Tamil Nadu!!!"
    )

    assert ai.profile["state"] == "Tamil Nadu"


def test_edge_29_noisy_complete_message():
    ai, result = run_conversation([
        "Hi!! I'm 24, male, from Tamil Nadu... "
        "I want to start a food business!!!"
    ])

    assert ai.profile["age"] == 24
    assert ai.profile["gender"] == "Male"
    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_edge_30_whitespace_does_not_corrupt_profile():
    ai = AIAssistant()

    ai.process_message(
        "I want to start a food business"
    )

    before = ai.profile.copy()

    ai.process_message("     ")

    assert ai.profile == before