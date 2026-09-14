import sys
import re
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

# 1. Inspect scheme_detail.js
scheme_detail_path = ROOT_DIR / "frontend" / "scheme_detail.js"
scheme_detail_code = scheme_detail_path.read_text(encoding="utf-8")

# Check section order in renderScreen
header_pos = scheme_detail_code.find("Concise Scheme Header Card")
about_pos = scheme_detail_code.find("Scheme Overview Card")
match_pos = scheme_detail_code.find("Personalized Match Card")
pathway_pos = scheme_detail_code.find("Personalized Pathway Block")
copilot_pos = scheme_detail_code.find("AI Pathway Copilot Card Section")
guide_pos = scheme_detail_code.find("Application Guide & Document Checklist")

order_ok = (header_pos < about_pos < match_pos < pathway_pos < copilot_pos < guide_pos)

# Check Support Type mapping helper
has_support_mapping = "formatSupportTypeLabel" in scheme_detail_code and "Loan / Credit" in scheme_detail_code and "Capital Subsidy" in scheme_detail_code

# Check Planning Guidance notice strings
has_planning_badge = "Suggested preparation order" in scheme_detail_code
has_planning_disclaimer = "📌 This order is planning guidance and is not an official government sequence." in scheme_detail_code

# Check Fallback UI message
has_fallback_msg = "Personalized AI explanation is temporarily unavailable. Your verified pathway is still available above." in scheme_detail_code
has_retry_btn = "Retry" in scheme_detail_code

# Check Apply handoff modal integration
has_apply_modal = "applyHandoffModal" in scheme_detail_code and "btn_visit_official_apply" in scheme_detail_code

print("=== FRONTEND DOM & CODE AUDIT RESULTS ===")
print(f"1. SECTION ORDER VALIDATED: {order_ok}")
print(f"   Header ({header_pos}) -> About ({about_pos}) -> Match ({match_pos}) -> Pathway ({pathway_pos}) -> Copilot ({copilot_pos}) -> Guide ({guide_pos})")
print(f"2. SUPPORT TYPE MAPPING: {'Passed' if has_support_mapping else 'Failed'} (Credit;Subsidy -> Loan / Credit, Capital Subsidy)")
print(f"3. PLANNING GUIDANCE NOTICE: {'Passed' if has_planning_badge and has_planning_disclaimer else 'Failed'}")
print(f"4. FAILURE FALLBACK UI: {'Passed' if has_fallback_msg and has_retry_btn else 'Failed'}")
print(f"5. APPLY HANDOFF MODAL: {'Passed' if has_apply_modal else 'Failed'}")
