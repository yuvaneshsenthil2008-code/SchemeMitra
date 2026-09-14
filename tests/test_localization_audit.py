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
