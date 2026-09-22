import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"

def extract_keys_from_frontend():
    referenced_keys = set()

    # Regex patterns
    patterns = [
        r"data-i18n=[\"']([a-zA-Z0-9_]+)[\"']",
        r"\bt\(\s*[\"']([a-zA-Z0-9_]+)[\"']\s*\)",
        r"window\.i18n\.get\(\s*[\"']([a-zA-Z0-9_]+)[\"']\s*\)",
        r"i18n\.get\(\s*[\"']([a-zA-Z0-9_]+)[\"']\s*\)"
    ]

    for file_path in FRONTEND_DIR.glob("*"):
        if file_path.suffix in [".html", ".js"]:
            text = file_path.read_text(encoding="utf-8")
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for m in matches:
                    referenced_keys.add(m)

    return referenced_keys

def get_keys_in_dict(block_text):
    matches = re.findall(r"^\s*[\"']?([a-zA-Z0-9_]+)[\"']?\s*:\s*[\"']", block_text, re.MULTILINE)
    return set(matches)

def main():
    referenced = extract_keys_from_frontend()
    print(f"Total referenced runtime keys found in frontend: {len(referenced)}")

    i18n_path = FRONTEND_DIR / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    en_match = re.search(r"en:\s*\{(.*?)\},\s*ta:", content, re.DOTALL)
    ta_match = re.search(r"ta:\s*\{(.*?)\},\s*hi:", content, re.DOTALL)
    hi_match = re.search(r"hi:\s*\{(.*?)\}\s*\};", content, re.DOTALL)

    en_keys = get_keys_in_dict(en_match.group(1)) if en_match else set()
    ta_keys = get_keys_in_dict(ta_match.group(1)) if ta_match else set()
    hi_keys = get_keys_in_dict(hi_match.group(1)) if hi_match else set()

    missing_en = referenced - en_keys
    missing_ta = referenced - ta_keys
    missing_hi = referenced - hi_keys

    print(f"Missing in English ({len(missing_en)}): {sorted(list(missing_en))}")
    print(f"Missing in Tamil ({len(missing_ta)}): {sorted(list(missing_ta))}")
    print(f"Missing in Hindi ({len(missing_hi)}): {sorted(list(missing_hi))}")

if __name__ == "__main__":
    main()
