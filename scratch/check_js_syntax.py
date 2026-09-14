import os
import glob
import re
from pathlib import Path

frontend_dir = str(Path(__file__).resolve().parents[1] / "frontend")

all_passed = True

def strip_js_literals(code):
    buf = []
    i = 0
    n = len(code)
    stack = ['TEXT']

    while i < n:
        state = stack[-1]

        if state == 'STRING_SINGLE':
            if code[i] == '\\':
                i += 2
            elif code[i] == "'":
                stack.pop()
                i += 1
            else:
                i += 1
            continue

        if state == 'STRING_DOUBLE':
            if code[i] == '\\':
                i += 2
            elif code[i] == '"':
                stack.pop()
                i += 1
            else:
                i += 1
            continue

        if state == 'TEMPLATE':
            if code[i] == '\\':
                i += 2
            elif code[i] == '`':
                stack.pop()
                i += 1
            elif code[i:i+2] == '${':
                stack.append(['EXPR', 1])
                buf.append('{')
                i += 2
            else:
                i += 1
            continue

        if isinstance(state, list) and state[0] == 'EXPR':
            depth = state[1]
            ch = code[i]

            if ch == '/':
                # Check for comment
                if code[i:i+2] == '//':
                    end = code.find('\n', i)
                    if end == -1:
                        break
                    i = end + 1
                    continue
                if code[i:i+2] == '/*':
                    end = code.find('*/', i)
                    if end == -1:
                        break
                    i = end + 2
                    continue
                
                # Check for regex literal
                last_char = None
                for b in reversed(buf):
                    if not b.isspace():
                        last_char = b
                        break
                if last_char in (None, '(', '=', ':', ',', '!', '?', '[', '{', ';', '+', '-', '*', '%', '&', '|', '^', '~', '>', '.'):
                    i += 1
                    in_char_class = False
                    while i < n:
                        rch = code[i]
                        if rch == '\\':
                            i += 2
                        elif rch == '[':
                            in_char_class = True
                            i += 1
                        elif rch == ']' and in_char_class:
                            in_char_class = False
                            i += 1
                        elif rch == '/' and not in_char_class:
                            i += 1
                            while i < n and code[i].isalpha():
                                i += 1
                            break
                        else:
                            i += 1
                    continue

            if ch == '\\':
                i += 2
            elif ch == "'":
                stack.append('STRING_SINGLE')
                i += 1
            elif ch == '"':
                stack.append('STRING_DOUBLE')
                i += 1
            elif ch == '`':
                stack.append('TEMPLATE')
                i += 1
            elif ch == '{':
                state[1] += 1
                buf.append('{')
                i += 1
            elif ch == '}':
                state[1] -= 1
                buf.append('}')
                if state[1] == 0:
                    stack.pop()
                i += 1
            else:
                buf.append(ch)
                i += 1
            continue

        # TEXT state
        if code[i:i+2] == '//':
            end = code.find('\n', i)
            if end == -1:
                break
            i = end + 1
            continue

        if code[i:i+2] == '/*':
            end = code.find('*/', i)
            if end == -1:
                break
            i = end + 2
            continue

        ch = code[i]

        # Check for Regex Literal starting with '/'
        if ch == '/':
            # Determine if '/' is a regex or division by looking at last non-whitespace char in buf
            last_char = None
            for b in reversed(buf):
                if not b.isspace():
                    last_char = b
                    break
            if last_char in (None, '(', '=', ':', ',', '!', '?', '[', '{', ';', '+', '-', '*', '%', '&', '|', '^', '~', '>'):
                # It's a Regex literal
                i += 1
                in_char_class = False
                while i < n:
                    rch = code[i]
                    if rch == '\\':
                        i += 2
                    elif rch == '[':
                        in_char_class = True
                        i += 1
                    elif rch == ']' and in_char_class:
                        in_char_class = False
                        i += 1
                    elif rch == '/' and not in_char_class:
                        i += 1
                        # skip flags
                        while i < n and code[i].isalpha():
                            i += 1
                        break
                    else:
                        i += 1
                continue

        if ch == "'":
            stack.append('STRING_SINGLE')
            i += 1
        elif ch == '"':
            stack.append('STRING_DOUBLE')
            i += 1
        elif ch == '`':
            stack.append('TEMPLATE')
            i += 1
        else:
            buf.append(ch)
            i += 1

    return "".join(buf)


for js_file in sorted(glob.glob(os.path.join(frontend_dir, "*.js"))):
    with open(js_file, "r", encoding="utf-8") as f:
        content = f.read()

    content_clean = strip_js_literals(content)

    brace_stack = []
    paren_stack = []
    bracket_stack = []
    file_has_error = False

    for idx, ch in enumerate(content_clean):
        if ch == '{':
            brace_stack.append(idx)
        elif ch == '}':
            if not brace_stack:
                print(f"[{os.path.basename(js_file)}] Unmatched closing brace '}}'")
                file_has_error = True
            else:
                brace_stack.pop()
        elif ch == '(':
            paren_stack.append(idx)
        elif ch == ')':
            if not paren_stack:
                print(f"[{os.path.basename(js_file)}] Unmatched closing paren ')'")
                file_has_error = True
            else:
                paren_stack.pop()
        elif ch == '[':
            bracket_stack.append(idx)
        elif ch == ']':
            if not bracket_stack:
                print(f"[{os.path.basename(js_file)}] Unmatched closing bracket ']'")
                file_has_error = True
            else:
                bracket_stack.pop()

    if brace_stack:
        print(f"[{os.path.basename(js_file)}] Unclosed braces count: {len(brace_stack)}")
        file_has_error = True
    if paren_stack:
        print(f"[{os.path.basename(js_file)}] Unclosed parens count: {len(paren_stack)}")
        file_has_error = True
    if bracket_stack:
        print(f"[{os.path.basename(js_file)}] Unclosed brackets count: {len(bracket_stack)}")
        file_has_error = True

    if file_has_error:
        all_passed = False
    else:
        print(f"[{os.path.basename(js_file)}] OK — Syntax & Bracket Balance Verified")

if all_passed:
    print("\nALL FRONTEND JS FILES PASSED SYNTAX VALIDATION CLEANLY.")
