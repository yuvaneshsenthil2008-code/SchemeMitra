import os

js_file = r"d:\SCHOOL\Yuvan studies\OppoOS/OpportunityOS_v2_FULL_ANTIGRAVITY_PACKAGE\frontend\my_opportunities.js"

with open(js_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

stack = []
in_string = False
string_char = None
in_comment_single = False
in_comment_multi = False

for line_num, line in enumerate(lines, 1):
    in_comment_single = False
    i = 0
    while i < len(line):
        ch = line[i]
        
        if in_comment_multi:
            if ch == '*' and i + 1 < len(line) and line[i+1] == '/':
                in_comment_multi = False
                i += 1
            i += 1
            continue

        if in_comment_single:
            i += 1
            continue

        if in_string:
            if ch == '\\':
                i += 2
                continue
            if ch == string_char:
                in_string = False
                string_char = None
            i += 1
            continue

        if ch == '/' and i + 1 < len(line):
            if line[i+1] == '/':
                in_comment_single = True
                i += 2
                continue
            elif line[i+1] == '*':
                in_comment_multi = True
                i += 2
                continue

        if ch in ['"', "'", '`']:
            in_string = True
            string_char = ch
            i += 1
            continue

        if ch == '{':
            stack.append((line_num, line.strip()))
        elif ch == '}':
            if stack:
                stack.pop()
            else:
                print(f"Extra closing brace at line {line_num}: {line.strip()}")

        i += 1

print(f"\nRemaining unclosed braces on stack ({len(stack)}):")
for ln, text in stack:
    print(f"Line {ln}: {text}")
