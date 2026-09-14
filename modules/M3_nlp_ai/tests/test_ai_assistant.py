from ai.ai_assistant import AIAssistant


def test_food_business():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I want to start a food business"
    )

    assert result["success"] is True
    assert result["intent"] == "OPPORTUNITY"
    assert result["profile"]["sector"] == "Food Processing & Agri Value Addition"
    assert result["profile"]["business_type"] in ["Startup", "Idea"]


def test_tanglish_business():
    assistant = AIAssistant()

    result = assistant.process_message(
        "Enakku 24 vayasu, Tamil Nadu la irukken, "
        "food business start panna poren"
    )

    assert result["success"] is True
    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["profile"]["sector"] == "Food Processing & Agri Value Addition"
    assert result["profile"]["business_type"] in ["Startup", "Idea"]


def test_missing_information():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I want to start a food business"
    )

    assert len(result["missing_fields"]) > 0
    assert result["next_field"] == "age"


def test_empty_message():
    assistant = AIAssistant()

    result = assistant.process_message("")

    assert result["success"] is False


def test_unknown_message():
    assistant = AIAssistant()

    result = assistant.process_message(
        "What is the weather today?"
    )

    assert result["intent"] in [
    "UNKNOWN",
    "IRRELEVANT",
    "GENERAL_QUERY",
]

def test_conversation_profile_state():
    assistant = AIAssistant()

    result1 = assistant.process_message("I am 24")

    assert result1["profile"]["age"] == 24

    result2 = assistant.process_message(
        "I live in Tamil Nadu"
    )

    assert result2["profile"]["age"] == 24
    assert result2["profile"]["state"] == "Tamil Nadu"

    result3 = assistant.process_message(
        "I completed my degree"
    )

    assert result3["profile"]["age"] == 24
    assert result3["profile"]["state"] == "Tamil Nadu"
    assert result3["profile"]["education"] == "Degree"

def test_hindi_business():
    assistant = AIAssistant()

    result = assistant.process_message(
        "मुझे तमिलनाडु में फूड बिजनेस शुरू करना है"
    )

    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["profile"]["sector"] == "Food Processing & Agri Value Addition"
    assert result["profile"]["business_type"] in ["Startup", "Idea"]
    assert result["profile"]["new_business"] is True


def test_hinglish_business():
    assistant = AIAssistant()

    result = assistant.process_message(
        "Mujhe Tamil Nadu mein food business shuru karna hai"
    )

    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["profile"]["sector"] == "Food Processing & Agri Value Addition"
    assert result["profile"]["business_type"] in ["Startup", "Idea"]
    assert result["profile"]["new_business"] is True


def test_short_age_answer():
    assistant = AIAssistant()

    # Start a conversation that requires information
    result1 = assistant.process_message(
        "I want to start a food business"
    )

    assert result1["current_question"] == "age"

    # Short answer should be understood using context
    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["current_question"] == "gender"


def test_short_state_answer():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "I want to start a food business"
    )

    assert result1["current_question"] == "age"

    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["current_question"] == "gender"

    result3 = assistant.process_message("Male")

    assert result3["profile"]["gender"] == "Male"
    assert result3["current_question"] == "state"

    result4 = assistant.process_message("Tamil Nadu")

    assert result4["profile"]["state"] == "Tamil Nadu"
    assert result4["current_question"] == "education"


def test_short_education_answer():
    assistant = AIAssistant()

    assistant.process_message(
        "I want to start a food business"
    )

    assistant.process_message("24")
    assistant.process_message("Male")
    assistant.process_message("Tamil Nadu")

    result = assistant.process_message("Degree")

    assert result["profile"]["education"] == "Degree"
    assert result["current_question"] == "category"

def test_profile_merging():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I am 24 and I live in Tamil Nadu"
    )

    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"

    assert result["changes"][0]["type"] == "added"



def test_profile_correction():
    assistant = AIAssistant()

    result1 = assistant.process_message("I am 24")

    assert result1["profile"]["age"] == 24

    result2 = assistant.process_message(
        "Actually, I am 25"
    )

    # v3.4:
    # Do not silently overwrite the existing value.
    assert result2["profile"]["age"] == 24

    # A conflict must be detected.
    assert len(result2["conflicts"]) == 1

    conflict = result2["conflicts"][0]

    assert conflict["field"] == "age"
    assert conflict["old_value"] == 24
    assert conflict["new_value"] == 25

    assert "Which one is correct?" in result2["response"]



def test_profile_preserves_previous_information():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "I am 24 and I live in Tamil Nadu"
    )

    assert result1["profile"]["age"] == 24
    assert result1["profile"]["state"] == "Tamil Nadu"

    result2 = assistant.process_message(
        "I completed my degree"
    )

    assert result2["profile"]["age"] == 24
    assert result2["profile"]["state"] == "Tamil Nadu"
    assert result2["profile"]["education"] == "Degree"

def test_only_next_missing_field_is_asked():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I want to start a food business"
    )

    assert result["current_question"] == "age"
    assert result["next_field"] == "age"

    result = assistant.process_message("24")

    assert result["profile"]["age"] == 24
    assert result["current_question"] == "gender"
    assert result["next_field"] == "gender"

    result = assistant.process_message("Male")

    assert result["profile"]["gender"] == "Male"
    assert result["current_question"] == "state"
    assert result["next_field"] == "state"


def test_context_aware_short_answers():
    assistant = AIAssistant()

    assistant.process_message(
        "I want to start a food business"
    )

    # AI asks age
    result = assistant.process_message("24")
    assert result["profile"]["age"] == 24

    # AI asks gender
    result = assistant.process_message("Male")
    assert result["profile"]["gender"] == "Male"

    # AI asks state
    result = assistant.process_message("Tamil Nadu")
    assert result["profile"]["state"] == "Tamil Nadu"

    # AI asks education
    result = assistant.process_message("Degree")
    assert result["profile"]["education"] == "Degree"

    assert result["current_question"] == "category"


def test_next_question_changes_after_each_answer():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I want to start a food business"
    )

    assert result["current_question"] == "age"

    result = assistant.process_message("24")
    assert result["current_question"] == "gender"

    result = assistant.process_message("Male")
    assert result["current_question"] == "state"

    result = assistant.process_message("Tamil Nadu")
    assert result["current_question"] == "education"

    result = assistant.process_message("Degree")
    assert result["current_question"] == "category"


def test_multiple_fields_skip_answered_questions():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I am 24, male, from Tamil Nadu and I completed my degree."
    )

    assert result["profile"]["age"] == 24
    assert result["profile"]["gender"] == "Male"
    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["profile"]["education"] == "Degree"

    # These four fields should NOT be asked again.
    assert "age" not in result["missing_fields"]
    assert "gender" not in result["missing_fields"]
    assert "state" not in result["missing_fields"]
    assert "education" not in result["missing_fields"]

    # The next missing field should be category.
    assert result["current_question"] == "category"
    assert result["next_field"] == "category"


def test_conflicting_age_is_detected():
    assistant = AIAssistant()

    result1 = assistant.process_message("I am 24")

    assert result1["profile"]["age"] == 24

    result2 = assistant.process_message(
        "Actually, I am 25"
    )

    # Old value must remain.
    assert result2["profile"]["age"] == 24

    # Conflict must be detected.
    assert len(result2["conflicts"]) == 1

    conflict = result2["conflicts"][0]

    assert conflict["field"] == "age"
    assert conflict["old_value"] == 24
    assert conflict["new_value"] == 25


def test_same_information_is_not_conflict():
    assistant = AIAssistant()

    assistant.process_message("I am 24")

    result = assistant.process_message("I am 24")

    assert result["profile"]["age"] == 24
    assert result["conflicts"] == []


def test_new_information_is_not_conflict():
    assistant = AIAssistant()

    result = assistant.process_message(
        "I am 24 and I live in Tamil Nadu"
    )

    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"

    assert result["conflicts"] == []


def test_conflict_preserves_previous_profile():
    assistant = AIAssistant()

    assistant.process_message(
        "I am 24 and I live in Tamil Nadu"
    )

    result = assistant.process_message(
        "Actually, I am 25"
    )

    # Previous information must remain.
    assert result["profile"]["age"] == 24
    assert result["profile"]["state"] == "Tamil Nadu"

    assert result["conflicts"][0]["old_value"] == 24
    assert result["conflicts"][0]["new_value"] == 25

def test_english_language_memory():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "I want to start a food business"
    )

    assert result1["language"] == "English"
    assert result1["response"] == "What is your age?"

    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "English"
    assert result2["response"] == "What is your gender?"


def test_tanglish_language_memory():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "Enakku food business start panna poren"
    )

    assert result1["language"] == "Tanglish"
    assert result1["response"] == "Ungaloda vayasu enna?"

    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Tanglish"
    assert result2["response"] == "Ungaloda gender enna?"


def test_tamil_language_memory():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "எனக்கு உணவு தொழில் தொடங்க வேண்டும்"
    )

    assert result1["language"] == "Tamil"
    assert result1["response"] == "உங்கள் வயது என்ன?"

    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Tamil"
    assert result2["response"] == "உங்கள் பாலினம் என்ன?"


def test_hindi_language_memory():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "मुझे फूड बिजनेस शुरू करना है"
    )

    assert result1["language"] == "Hindi"
    assert result1["response"] == "आपकी उम्र क्या है?"

    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Hindi"
    assert result2["response"] == "आपका लिंग क्या है?"


def test_hinglish_language_memory():
    assistant = AIAssistant()

    result1 = assistant.process_message(
        "Mujhe food business shuru karna hai"
    )

    assert result1["language"] == "Hinglish"
    assert result1["response"] == "Aapki age kya hai?"

    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Hinglish"
    assert result2["response"] == "Aapka gender kya hai?"

# =========================================================
# v3.5 STEP 4 - MULTILINGUAL SHORT ANSWER TESTS
# =========================================================


def test_tamil_short_answers():
    assistant = AIAssistant()

    # Start conversation in Tamil
    result1 = assistant.process_message(
        "எனக்கு உணவு தொழில் தொடங்க வேண்டும்"
    )

    assert result1["language"] == "Tamil"
    assert result1["current_question"] == "age"

    # Short age answer
    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Tamil"
    assert result2["current_question"] == "gender"

    # Tamil gender answer
    result3 = assistant.process_message("ஆண்")

    assert result3["profile"]["gender"] == "Male"
    assert result3["language"] == "Tamil"


def test_tanglish_short_answers():
    assistant = AIAssistant()

    # Start conversation in Tanglish
    result1 = assistant.process_message(
        "Enakku food business start panna poren"
    )

    assert result1["language"] == "Tanglish"
    assert result1["current_question"] == "age"

    # Short age answer
    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Tanglish"
    assert result2["current_question"] == "gender"

    # Tanglish gender answer
    result3 = assistant.process_message("aan")

    assert result3["profile"]["gender"] == "Male"
    assert result3["language"] == "Tanglish"


def test_hinglish_short_answers():
    assistant = AIAssistant()

    # Start conversation in Hinglish
    result1 = assistant.process_message(
        "Mujhe food business shuru karna hai"
    )

    assert result1["language"] == "Hinglish"
    assert result1["current_question"] == "age"

    # Short age answer
    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Hinglish"
    assert result2["current_question"] == "gender"

    # Hinglish gender answer
    result3 = assistant.process_message("male")

    assert result3["profile"]["gender"] == "Male"
    assert result3["language"] == "Hinglish"


def test_hindi_short_answers():
    assistant = AIAssistant()

    # Start conversation in Hindi
    result1 = assistant.process_message(
        "मुझे फूड बिजनेस शुरू करना है"
    )

    assert result1["language"] == "Hindi"
    assert result1["current_question"] == "age"

    # Short age answer
    result2 = assistant.process_message("24")

    assert result2["profile"]["age"] == 24
    assert result2["language"] == "Hindi"
    assert result2["current_question"] == "gender"

    # Hindi gender answer
    result3 = assistant.process_message("पुरुष")

    assert result3["profile"]["gender"] == "Male"
    assert result3["language"] == "Hindi"


def test_multilingual_state_answers():
    # Tamil
    assistant = AIAssistant()

    assistant.process_message(
        "எனக்கு உணவு தொழில் தொடங்க வேண்டும்"
    )

    assistant.process_message("24")
    assistant.process_message("ஆண்")

    result = assistant.process_message("தமிழ்நாடு")

    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["language"] == "Tamil"

    # Tanglish
    assistant = AIAssistant()

    assistant.process_message(
        "Enakku food business start panna poren"
    )

    assistant.process_message("24")
    assistant.process_message("aan")

    result = assistant.process_message("Tamil Nadu")

    assert result["profile"]["state"] == "Tamil Nadu"
    assert result["language"] == "Tanglish"


def test_multilingual_education_answers():
    # Tamil
    assistant = AIAssistant()

    assistant.process_message(
        "எனக்கு உணவு தொழில் தொடங்க வேண்டும்"
    )

    assistant.process_message("24")
    assistant.process_message("ஆண்")
    assistant.process_message("தமிழ்நாடு")

    result = assistant.process_message("பட்டம்")

    assert result["profile"]["education"] == "Degree"
    assert result["language"] == "Tamil"

    # Hindi
    assistant = AIAssistant()

    assistant.process_message(
        "मुझे फूड बिजनेस शुरू करना है"
    )

    assistant.process_message("24")
    assistant.process_message("पुरुष")
    assistant.process_message("Tamil Nadu")

    result = assistant.process_message("डिग्री")

    assert result["profile"]["education"] == "Degree"
    assert result["language"] == "Hindi"