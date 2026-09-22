import re
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"

def extract_keys_from_block(block_text: str) -> set[str]:
    matches = re.findall(r"^\s*([a-zA-Z0-9_]+)\s*:\s*[\"']", block_text, re.MULTILINE)
    return set(matches)

def test_i18n_keys_parity():
    """Verify that all keys in English dictionary have Tamil and Hindi translations."""
    i18n_path = FRONTEND_DIR / "i18n.js"
    assert i18n_path.exists()

    content = i18n_path.read_text(encoding="utf-8")

    en_block = re.search(r"en:\s*\{(.*?)\},\s*ta:", content, re.DOTALL)
    ta_block = re.search(r"ta:\s*\{(.*?)\},\s*hi:", content, re.DOTALL)
    hi_block = re.search(r"hi:\s*\{(.*?)\}\s*\};", content, re.DOTALL)

    assert en_block is not None, "English translations block missing in i18n.js"
    assert ta_block is not None, "Tamil translations block missing in i18n.js"
    assert hi_block is not None, "Hindi translations block missing in i18n.js"

    en_keys = extract_keys_from_block(en_block.group(1))
    ta_keys = extract_keys_from_block(ta_block.group(1))
    hi_keys = extract_keys_from_block(hi_block.group(1))

    assert len(en_keys) > 50, f"Failed to extract enough keys from en block, got {len(en_keys)}"

    missing_in_ta = en_keys - ta_keys
    missing_in_hi = en_keys - hi_keys

    assert not missing_in_ta, f"Keys missing in Tamil translation: {missing_in_ta}"
    assert not missing_in_hi, f"Keys missing in Hindi translation: {missing_in_hi}"

def test_m1_canonical_sector_keys_exist():
    """Verify that all 10 canonical M1 sectors have corresponding i18n keys."""
    i18n_path = FRONTEND_DIR / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    sector_keys = [
        "sector_agri",
        "sector_food",
        "sector_msme",
        "sector_finance",
        "sector_startup",
        "sector_skills",
        "sector_women",
        "sector_social",
        "sector_handicrafts",
        "sector_export"
    ]

    for key in sector_keys:
        assert f"{key}:" in content, f"Canonical sector translation key '{key}' missing in i18n.js"

def test_profile_builder_localization_keys_exist():
    """Verify specific Profile Builder strings requested by user are localized."""
    i18n_path = FRONTEND_DIR / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    required_keys = [
        "profile_builder_sub",
        "tab_conversational",
        "tab_structured_form",
        "voice_status_default",
        "tell_us_label",
        "txt_message_placeholder",
        "btn_extract_fields",
        "review_title",
        "review_sub",
        "btn_start_over",
        "btn_show_my_schemes"
    ]

    for key in required_keys:
        assert f"{key}:" in content, f"Required i18n key '{key}' missing from i18n.js"

def test_no_hardcoded_profile_builder_english():
    """Verify profile_builder.js has zero hardcoded user-visible English strings."""
    pb_path = FRONTEND_DIR / "profile_builder.js"
    content = pb_path.read_text(encoding="utf-8")

    hardcoded_strings = [
        "Use your voice or answer in plain language to extract your canonical profile",
        "Conversational / Voice Assistant",
        "Structured Form Input",
        "Click the microphone button to start speaking, or type below.",
        "Tell us about yourself & your business goal:",
        "Example: I am a 24-year-old female from Tamil Nadu with a degree wanting to start a food processing business with Rs 3 lakh income...",
        "Extract Profile Fields",
        "Review & Confirm Your Extracted Profile"
    ]

    for raw in hardcoded_strings:
        assert raw not in content, f"Hardcoded English string found in profile_builder.js: '{raw}'"

def test_scheme_names_remain_canonical_english():
    """Verify that getLocalizedSchemeName returns localized: null and retains canonical English official scheme names."""
    i18n_path = FRONTEND_DIR / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    assert "getLocalizedSchemeName" in content
    assert "localized: null" in content
    assert "official: rawName" in content

def test_dynamic_localization_keys_exist():
    """Verify new dynamic localization keys added for Profile Summary, Best Match, Inline Roadmap, Clarifications, and Opportunity Graph exist in i18n.js."""
    i18n_path = FRONTEND_DIR / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    new_keys = [
        "badge_best_match_1",
        "badge_best_match",
        "lbl_your_next_actions",
        "btn_view_scheme_details",
        "btn_view_roadmap_steps",
        "btn_hide_roadmap_steps",
        "roadmap_your_roadmap",
        "roadmap_what_you_have",
        "roadmap_please_confirm",
        "roadmap_my_next_steps",
        "roadmap_age_available",
        "roadmap_state_confirmed",
        "roadmap_sector_available",
        "roadmap_stage_confirmed",
        "roadmap_gender_specified",
        "roadmap_qualification_specified",
        "roadmap_confirm_missing",
        "roadmap_review_guide",
        "roadmap_proceed_portal",
        "more_info_title",
        "more_info_sub",
        "q_is_new_unit",
        "q_prior_subsidy",
        "q_family_pmegp",
        "btn_yes",
        "btn_no",
        "graph_your_profile",
        "graph_opportunity",
        "graph_mode_top3",
        "graph_mode_top5",
        "graph_mode_all",
        "graph_fit_view",
        "graph_reset",
        "graph_outstanding_reqs",
        "graph_verified_benefits",
        "graph_node_types_lbl",
        "graph_status_lbl",
        "graph_req_state_lbl",
        "graph_footnote",
        "lbl_annual_income",
        "lbl_available_capital",
        "lbl_disability",
        "lbl_yrs"
    ]

    for key in new_keys:
        assert f"{key}:" in content, f"Required dynamic i18n key '{key}' missing from i18n.js"

def test_dynamic_localization_helpers_exist():
    """Verify dynamic translation helper functions exist in i18n.js."""
    i18n_path = FRONTEND_DIR / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    helpers = [
        "localizeProfileValue",
        "localizeRequirementAction",
        "localizeBenefit",
        "localizeRoadmapText",
        "getGenderLabel",
        "getStateLabel",
        "getSectorLabel",
        "getStageLabel",
        "getGoalLabel",
        "getDisabilityLabel",
        "getSupportTypeLabel"
    ]

    for h in helpers:
        assert h in content, f"Required i18n helper function '{h}' missing from i18n.js"


def test_all_runtime_i18n_references_exist_in_all_languages():
    """Every static runtime translation key referenced by active frontend code must exist in en/ta/hi."""
    i18n_content = (FRONTEND_DIR / "i18n.js").read_text(encoding="utf-8")
    en_block = re.search(r"en:\s*\{(.*?)\},\s*ta:", i18n_content, re.DOTALL)
    ta_block = re.search(r"ta:\s*\{(.*?)\},\s*hi:", i18n_content, re.DOTALL)
    hi_block = re.search(r"hi:\s*\{(.*?)\}\s*\};", i18n_content, re.DOTALL)
    assert en_block and ta_block and hi_block

    lang_keys = {
        "en": extract_keys_from_block(en_block.group(1)),
        "ta": extract_keys_from_block(ta_block.group(1)),
        "hi": extract_keys_from_block(hi_block.group(1)),
    }

    referenced = set()
    patterns = [
        re.compile(r"\bt\(\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)"),
        re.compile(r"\bi18n\.get\(\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)"),
        re.compile(r"data-i18n=['\"]([A-Za-z0-9_]+)['\"]"),
    ]
    for path in FRONTEND_DIR.glob("*.js"):
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            referenced.update(pattern.findall(text))
    html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    for pattern in patterns:
        referenced.update(pattern.findall(html))

    assert referenced, "No runtime i18n references were detected"
    for lang, keys in lang_keys.items():
        missing = referenced - keys
        assert not missing, f"Runtime i18n keys missing in {lang}: {sorted(missing)}"


def test_goal_pathway_and_graph_use_localized_runtime_labels():
    src = (FRONTEND_DIR / "my_opportunities.js").read_text(encoding="utf-8")
    forbidden_visible_literals = [
        ">WHAT NEEDS ATTENTION<",
        ">NEXT ACTIONS TO REVIEW",
        ">YOUR REQUIREMENT PROGRESS<",
        ">YOUR GOAL DESTINATION<",
        ">Retry Graph Generation<",
        ">No relevant opportunities yet<",
        ">No outstanding requirements<",
        ">Verified details unavailable<",
    ]
    for literal in forbidden_visible_literals:
        assert literal not in src, f"Hardcoded pathway/graph English remains: {literal}"
    assert "rerenderDashboardFromState" in src
    assert "graphOpportunityNodes" in src
