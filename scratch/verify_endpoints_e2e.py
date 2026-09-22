import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    res = requests.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print("[OK] Health check PASSED:", res.json()["status"])

def test_profile_parse():
    # English
    payload_en = {"message": "I am 24 years old, from Chennai, completed B.Tech in Computer Science Engineering and want to start a retail business."}
    res_en = requests.post(f"{BASE_URL}/api/profile/parse", json=payload_en)
    assert res_en.status_code == 200, f"Profile parse EN failed: {res_en.text}"
    p_en = res_en.json().get("profile", {})
    print("[OK] EN Profile Parse:", json.dumps(p_en, ensure_ascii=False))
    assert p_en.get("age") == 24
    assert p_en.get("district") == "Chennai"
    assert p_en.get("education_course") == "B.Tech"
    assert p_en.get("education_field") == "Computer Science"

    # Tamil
    payload_ta = {"message": "நான் 24 வயதானவன், சென்னையில் இருக்கேன், பி.டெக் கம்ப்யூட்டர் சயின்ஸ் இன்ஜினியரிங் படித்திருக்கிறேன்"}
    res_ta = requests.post(f"{BASE_URL}/api/profile/parse", json=payload_ta)
    assert res_ta.status_code == 200, f"Profile parse TA failed: {res_ta.text}"
    p_ta = res_ta.json().get("profile", {})
    print("[OK] TA Profile Parse:", json.dumps(p_ta, ensure_ascii=False))
    assert p_ta.get("age") == 24
    assert p_ta.get("district") == "Chennai"
    assert p_ta.get("education_course") in ["B.Tech", "Degree"]
    assert p_ta.get("education_field") == "Computer Science"

    # Hindi
    payload_hi = {"message": "मैं 24 साल का हूं, चेन्नई में रहता हूं, बीटेक कंप्यूटर साइंस इंजीनियरिंग किया है"}
    res_hi = requests.post(f"{BASE_URL}/api/profile/parse", json=payload_hi)
    assert res_hi.status_code == 200, f"Profile parse HI failed: {res_hi.text}"
    p_hi = res_hi.json().get("profile", {})
    print("[OK] HI Profile Parse:", json.dumps(p_hi, ensure_ascii=False))
    assert p_hi.get("age") == 24
    assert p_hi.get("district") == "Chennai"
    assert p_hi.get("education_course") in ["B.Tech", "Degree"]
    assert p_hi.get("education_field") == "Computer Science"

def test_analyze():
    profile = {
        "age": 25,
        "gender": "Male",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "education": "Degree",
        "education_course": "B.Tech",
        "education_field": "Computer Science",
        "category": "General",
        "annual_income": 300000,
        "is_employed": False,
        "business_stage": "Idea Stage"
    }
    res = requests.post(f"{BASE_URL}/api/analyze", json={"profile": profile})
    assert res.status_code == 200, f"Analyze failed: {res.text}"
    data = res.json()
    print("[OK] Analyze Service PASSED. Best Matches count:", len(data.get("best_matches", [])))
    assert "best_matches" in data

def test_goal_pathway_mark_completed():
    client_id = "test_e2e_client_999"
    req_id = "REQ0001"

    # Complete
    res_comp = requests.post(f"{BASE_URL}/api/pathway/goal/progress/complete", json={"client_id": client_id, "requirement_id": req_id})
    assert res_comp.status_code == 200, f"Complete failed: {res_comp.text}"
    print("[OK] Mark Completed PASSED:", res_comp.json())

    # Verify DB persistence via completed-actions endpoint
    res_actions = requests.get(f"{BASE_URL}/api/pathway/goal/completed-actions?client_id={client_id}")
    assert res_actions.status_code == 200
    actions = res_actions.json().get("completed_actions", [])
    req_ids = [a["requirement_id"] for a in actions]
    print("[OK] Completed Actions Persistence PASSED:", req_ids)
    assert req_id in req_ids

    # Reopen
    res_reopen = requests.post(f"{BASE_URL}/api/pathway/goal/progress/reopen", json={"client_id": client_id, "requirement_id": req_id})
    assert res_reopen.status_code == 200, f"Reopen failed: {res_reopen.text}"
    print("[OK] Reopen PASSED:", res_reopen.json())

    # Check that it's removed from completed actions
    res_actions2 = requests.get(f"{BASE_URL}/api/pathway/goal/completed-actions?client_id={client_id}")
    actions2 = res_actions2.json().get("completed_actions", [])
    req_ids2 = [a["requirement_id"] for a in actions2]
    assert req_id not in req_ids2
    print("✓ Reopen Persistence PASSED: requirement removed from completed list.")

if __name__ == "__main__":
    test_health()
    test_profile_parse()
    test_analyze()
    test_goal_pathway_mark_completed()
    print("\nALL END-TO-END API STABILIZATION TESTS PASSED SUCCESSFULLY!")
