import re

with open("scratch/build_i18n.py", "r", encoding="utf-8") as f:
    text = f.read()

parts = text.split('js_code = f"""')

def fix_dict_str(dict_str):
    lines = dict_str.split("\n")
    fixed_lines = []
    for line in lines:
        m = re.match(r'^(\s*)([a-zA-Z0-9_]+)\s*:(.*)$', line)
        if m:
            indent, key, rest = m.groups()
            if not key.startswith('"'):
                line = f'{indent}"{key}":{rest}'
        fixed_lines.append(line)
    return "\n".join(fixed_lines)

parts[0] = fix_dict_str(parts[0])
new_text = 'js_code = f"""'.join(parts)

with open("scratch/build_i18n.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Updated scratch/build_i18n.py successfully.")
