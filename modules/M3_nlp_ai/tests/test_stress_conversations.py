from ai.ai_assistant import AIAssistant


# ============================================================
# HELPER
# ============================================================

def run_conversation(messages):
    ai = AIAssistant()

    last_response = None

    for message in messages:
        last_response = ai.process_message(message)

    return ai, last_response


# ============================================================
# GROUP 1 — NORMAL REALISTIC CONVERSATIONS
# ============================================================

def test_stress_01_basic_english_flow():
    ai, result = run_conversation([
        "I want to start a food business",
        "24",
        "Male",
        "Tamil Nadu",
        "Degree",
        "General",
    ])

    assert ai.profile["age"] == 24
    assert ai.profile["gender"] == "Male"
    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["education"] == "Degree"
    assert ai.profile["category"] == "General"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_stress_02_information_given_in_one_message():
    ai, result = run_conversation([
        "I am 28, male, from Tamil Nadu and I want to start a food business"
    ])

    assert ai.profile["age"] == 28
    assert ai.profile["gender"] == "Male"
    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_stress_03_profile_information_order_changes():
    ai, result = run_conversation([
        "I live in Kerala",
        "I am 31",
        "Female",
        "Diploma",
    ])

    assert ai.profile["state"] == "Kerala"
    assert ai.profile["age"] == 31
    assert ai.profile["gender"] == "Female"
    assert ai.profile["education"] == "Diploma"


def test_stress_04_food_business_followup():
    ai, result = run_conversation([
        "I want to open a bakery",
        "26",
        "Female",
        "Karnataka",
        "Degree",
    ])

    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["age"] == 26
    assert ai.profile["gender"] == "Female"
    assert ai.profile["state"] == "Karnataka"


def test_stress_05_existing_business():
    ai, result = run_conversation([
        "I already have a running food business",
        "35",
        "Male",
        "Tamil Nadu",
    ])

    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] == "Existing"


# ============================================================
# GROUP 2 — INFORMAL ENGLISH
# ============================================================

def test_stress_06_im_24():
    ai, result = run_conversation([
        "I want to start a food business",
        "im 24",
    ])

    assert ai.profile["age"] == 24


def test_stress_07_im_a_male():
    ai, result = run_conversation([
        "I want to start a food business",
        "24",
        "im male",
    ])

    assert ai.profile["gender"] == "Male"


def test_stress_08_from_tn():
    ai, result = run_conversation([
        "I want to start a food business",
        "24",
        "Male",
        "TN",
    ])

    assert ai.profile["state"] == "Tamil Nadu"


def test_stress_09_degree_informal():
    ai, result = run_conversation([
        "I want to start a food business",
        "24",
        "Male",
        "Tamil Nadu",
        "degree",
    ])

    assert ai.profile["education"] == "Degree"


def test_stress_10_general_category_phrase():
    ai, result = run_conversation([
        "I want to start a food business",
        "24",
        "Male",
        "Tamil Nadu",
        "Degree",
        "general category",
    ])

    assert ai.profile["category"] == "General"


# ============================================================
# GROUP 3 — TANGLISH
# ============================================================

def test_stress_11_tanglish_business():
    ai, result = run_conversation([
        "Enakku food business start panna poren"
    ])

    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_stress_12_tanglish_age():
    ai, result = run_conversation([
        "Food business start panna poren",
        "enaku 24 vayasu",
    ])

    assert ai.profile["age"] == 24


def test_stress_13_tanglish_state():
    ai, result = run_conversation([
        "Food business start panna poren",
        "24",
        "aan",
        "TN",
    ])

    assert ai.profile["state"] == "Tamil Nadu"


def test_stress_14_tanglish_education():
    ai, result = run_conversation([
        "Food business start panna poren",
        "24",
        "aan",
        "Tamil Nadu",
        "degree mudichiten",
    ])

    assert ai.profile["education"] == "Degree"


def test_stress_15_mixed_english_tanglish():
    ai, result = run_conversation([
        "I am 24, Tamil Nadu la iruken, food business start panna poren"
    ])

    assert ai.profile["age"] == 24
    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


# ============================================================
# GROUP 4 — HINDI / HINGLISH
# ============================================================

def test_stress_16_hinglish_business():
    ai, result = run_conversation([
        "Mujhe food business shuru karna hai"
    ])

    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_stress_17_hinglish_age():
    ai, result = run_conversation([
        "Mujhe food business shuru karna hai",
        "meri age 24 hai",
    ])

    assert ai.profile["age"] == 24


def test_stress_18_hinglish_gender():
    ai, result = run_conversation([
        "Mujhe food business shuru karna hai",
        "24",
        "aadmi",
    ])

    assert ai.profile["gender"] == "Male"


def test_stress_19_hindi_profile():
    ai, result = run_conversation([
        "मुझे तमिलनाडु में फूड बिजनेस शुरू करना है",
        "24",
        "पुरुष",
    ])

    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]
    assert ai.profile["gender"] == "Male"


def test_stress_20_hindi_age_sentence():
    ai, result = run_conversation([
        "मुझे व्यवसाय शुरू करना है",
        "मैं 24 साल का हूँ",
    ])

    assert ai.profile["age"] == 24


# ============================================================
# GROUP 5 — TAMIL
# ============================================================

def test_stress_21_tamil_business():
    ai, result = run_conversation([
        "தமிழ்நாட்டில் உணவு தொழில் தொடங்க விரும்புகிறேன்"
    ])

    assert ai.profile["state"] == "Tamil Nadu"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"
    assert ai.profile["business_type"] in ["Startup", "Idea"]


def test_stress_22_tamil_age():
    ai, result = run_conversation([
        "உணவு தொழில் தொடங்க விரும்புகிறேன்",
        "எனக்கு 24 வயது",
    ])

    assert ai.profile["age"] == 24


def test_stress_23_tamil_gender():
    ai, result = run_conversation([
        "உணவு தொழில் தொடங்க விரும்புகிறேன்",
        "24",
        "ஆண்",
    ])

    assert ai.profile["gender"] == "Male"


def test_stress_24_tamil_state_short_answer():
    ai, result = run_conversation([
        "உணவு தொழில் தொடங்க விரும்புகிறேன்",
        "24",
        "ஆண்",
        "தமிழ்நாடு",
    ])

    assert ai.profile["state"] == "Tamil Nadu"


def test_stress_25_tamil_education():
    ai, result = run_conversation([
        "உணவு தொழில் தொடங்க விரும்புகிறேன்",
        "24",
        "ஆண்",
        "தமிழ்நாடு",
        "பட்டம்",
    ])

    assert ai.profile["education"] == "Degree"


# ============================================================
# GROUP 6 — INCOMPLETE / WEIRD ANSWERS
# ============================================================

def test_stress_26_empty_answer_does_not_corrupt_profile():
    ai = AIAssistant()

    ai.process_message("I want to start a food business")
    before = ai.profile.copy()

    ai.process_message("")

    assert ai.profile == before


def test_stress_27_yes_is_not_age():
    ai, result = run_conversation([
        "I want to start a food business",
        "yes",
    ])

    assert "age" not in ai.profile


def test_stress_28_no_is_not_age():
    ai, result = run_conversation([
        "I want to start a food business",
        "no",
    ])

    assert "age" not in ai.profile


def test_stress_29_random_symbols():
    ai, result = run_conversation([
        "I want to start a food business",
        "???",
    ])

    assert "age" not in ai.profile


def test_stress_30_unknown_answer():
    ai, result = run_conversation([
        "I want to start a food business",
        "idk",
    ])

    assert "age" not in ai.profile


# ============================================================
# GROUP 7 — CORRECTIONS / CONFLICTS
# ============================================================

def test_stress_31_age_conflict():
    ai = AIAssistant()

    ai.process_message("I am 24 and want to start a food business")

    result = ai.process_message("Actually I am 25")

    assert ai.profile["age"] == 24
    assert len(result["conflicts"]) >= 1
    assert result["conflicts"][0]["field"] == "age"


def test_stress_32_state_conflict():
    ai = AIAssistant()

    ai.process_message(
        "I am 24 and I live in Tamil Nadu and want to start a food business"
    )

    result = ai.process_message("Actually I live in Kerala")

    assert ai.profile["state"] == "Tamil Nadu"
    assert any(
        conflict["field"] == "state"
        for conflict in result["conflicts"]
    )


def test_stress_33_gender_conflict():
    ai = AIAssistant()

    ai.process_message(
        "I am a male and I want to start a food business"
    )

    result = ai.process_message("Actually female")

    assert ai.profile["gender"] == "Male"
    assert any(
        conflict["field"] == "gender"
        for conflict in result["conflicts"]
    )


def test_stress_34_same_age_not_conflict():
    ai = AIAssistant()

    ai.process_message(
        "I am 24 and want to start a food business"
    )

    result = ai.process_message("I am 24")

    assert result["conflicts"] == []


def test_stress_35_new_information_after_existing_profile():
    ai = AIAssistant()

    ai.process_message(
        "I am 24 and want to start a food business"
    )

    ai.process_message("Male")

    assert ai.profile["age"] == 24
    assert ai.profile["gender"] == "Male"
    assert ai.profile["sector"] == "Food Processing & Agri Value Addition"


# ============================================================
# GROUP 8 — MONEY / REAL USER FORMATS
# ============================================================

def test_stress_36_income_standard_number():
    ai = AIAssistant()

    result = ai.process_message(
        "My income is 25000"
    )

    assert ai.profile["income"] == 25000


def test_stress_37_income_with_rupee_symbol():
    ai = AIAssistant()

    result = ai.process_message(
        "My monthly income is ₹25,000"
    )

    assert ai.profile["income"] == 25000


def test_stress_38_income_25k():
    ai = AIAssistant()

    ai.current_question = "income"

    ai.process_message("25k")

    assert ai.profile["income"] == 25000


def test_stress_39_project_cost_two_lakh():
    ai = AIAssistant()

    ai.current_question = "project_cost"

    ai.process_message("2 lakh")

    assert ai.profile["project_cost"] == 200000


def test_stress_40_project_cost_2_point_5_lakh():
    ai = AIAssistant()

    ai.current_question = "project_cost"

    ai.process_message("2.5 lakh")

    assert ai.profile["project_cost"] == 250000