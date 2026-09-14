import os, re
with open('frontend/my_opportunities.js', 'r', encoding='utf-8') as f:
    content = f.read()

no_comm = re.sub(r'//.*', '', content)
no_comm = re.sub(r'/\*[\s\S]*?\*/', '', no_comm)
no_str = re.sub(r'`[\s\S]*?`|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '', no_comm)
clean = re.sub(r'/(?:\\.|[^/\\\n])+/[gimsuy]*', '', no_str)

lines = clean.splitlines()
b_stack = []
p_stack = []
for i, l in enumerate(lines, 1):
    for ch in l:
        if ch == '{': b_stack.append((i, l.strip()))
        elif ch == '}':
            if b_stack: b_stack.pop()
        elif ch == '(': p_stack.append((i, l.strip()))
        elif ch == ')':
            if p_stack: p_stack.pop()

print('Unclosed braces lines:', [(x[0], x[1][:60]) for x in b_stack])
print('Unclosed parens lines:', [(x[0], x[1][:60]) for x in p_stack])
