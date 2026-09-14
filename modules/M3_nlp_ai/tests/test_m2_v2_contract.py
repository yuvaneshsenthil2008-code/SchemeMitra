from nlp.m2_adapter import build_m2_profile

def test_full_v2_contract():
    p=build_m2_profile({"age":24,"gender":"Transgender","income":25000,"income_period":"monthly",
      "business_type":"Existing","registrations":["UDYAM_REGISTRATION"],"certifications":["ZED"],
      "trainings":["EDP"],"documents":["AADHAAR"],"street_vendor":False,"greenfield":True,
      "target_entity":"Individual","entity_type":"Proprietorship","has_dpr":True})
    assert p["annual_income"]==300000
    assert p["business_stage"]=="Existing" and p["existing_business"] is True
    assert p["registrations"]==["UDYAM_REGISTRATION"]
    assert p["extra"]["has_dpr"] is True

def test_unknown_requirement_evidence_is_not_invented():
    p=build_m2_profile({"age":22})
    assert p["registrations"]==[] and p["certifications"]==[] and p["extra"]=={}
