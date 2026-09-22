"""End-to-end regressions for bugs reproduced in the live SchemeMitra UI."""
from pathlib import Path
from fastapi.testclient import TestClient

from server.app import app
from modules.M3_nlp_ai.nlp.profile_extractor import ProfileExtractor
from modules.M3_nlp_ai.nlp.rule_extractor import RuleExtractor

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_profile_parse_preserves_degree_course_and_field():
    res = client.post('/api/profile/parse', json={
        'message': 'I am 24 from Chennai. I completed B.Tech in Computer Science Engineering and want to start a retail shop.',
        'existing_profile': {},
    })
    assert res.status_code == 200
    profile = res.json()['profile']
    assert profile['age'] == 24
    assert profile['district'] == 'Chennai'
    assert profile['state'] == 'Tamil Nadu'
    assert profile['education'] == 'Degree'
    assert profile['education_course'] == 'B.Tech'
    assert profile['education_field'] == 'Computer Science'
    assert profile['sector'] == 'MSME & Manufacturing'
    assert profile['business_stage'] == 'Idea'


def test_tamil_native_city_and_education_end_to_end():
    msg = 'எனக்கு 24 வயது. நான் சென்னையில் இருக்கேன். நான் பி.டெக் கம்ப்யூட்டர் சயின்ஸ் இன்ஜினியரிங் படிக்கிறேன்.'
    res = client.post('/api/profile/parse', json={'message': msg, 'existing_profile': {}})
    assert res.status_code == 200
    p = res.json()['profile']
    assert p['age'] == 24
    assert p['district'] == 'Chennai'
    assert p['state'] == 'Tamil Nadu'
    assert p['education'] == 'Degree'
    assert p['education_course'] == 'B.Tech'
    assert p['education_field'] == 'Computer Science'


def test_hindi_native_city_degree_field_and_sector_end_to_end():
    msg = 'मैं 25 साल का हूं. मैं चेन्नई में रहता हूं. मैं बीटेक कंप्यूटर साइंस इंजीनियरिंग पढ़ रहा हूं. मेरे को एग्रीकल्चर एंड फार्मिंग में बिजनेस शुरू करना है.'
    res = client.post('/api/profile/parse', json={'message': msg, 'existing_profile': {}})
    assert res.status_code == 200
    p = res.json()['profile']
    assert p['age'] == 25
    assert p['district'] == 'Chennai'
    assert p['state'] == 'Tamil Nadu'
    assert p['education'] == 'Degree'
    assert p['education_course'] == 'B.Tech'
    assert p['education_field'] == 'Computer Science'
    assert p['sector'] == 'Agriculture & Allied'
    assert p['business_stage'] == 'Idea'


def test_conversational_tamil_clothing_shop_start_intent():
    p = ProfileExtractor().extract('நான் துணிக்கடை ஆரம்பிக்கணும்னு ஆசை', use_llm='never')['profile']
    assert p['sector'] == 'MSME & Manufacturing'
    assert p['business_stage'] == 'Idea'
    assert p['business_goal'] == 'START_BUSINESS'


def test_native_third_party_locations_do_not_pollute_user_profile():
    rules = RuleExtractor()
    assert rules.extract('என் நண்பன் சென்னையில் இருக்கான்').get('district') is None
    assert rules.extract('मेरा दोस्त चेन्नई में रहता है').get('district') is None


def test_notice_text_runtime_reference_is_declared():
    src = (ROOT / 'frontend' / 'profile_builder.js').read_text(encoding='utf-8')
    assert 'let noticeText = "";' in src
    assert 'Error parsing profile message: " + err.message' not in src


def test_profile_form_exposes_education_course_field():
    src = (ROOT / 'frontend' / 'profile_form.js').read_text(encoding='utf-8')
    assert "handleInput('education_course'" in src
    assert 'badge_education_course' in src
