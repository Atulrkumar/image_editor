#!/usr/bin/env python3
"""Fix Git merge conflicts by keeping the newer version (after =======)"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
skip_mode = False
in_conflict = False

i = 0
while i < len(lines):
    line = lines[i]
    
    if line.startswith('<<<<<<<'):
        # Start of conflict - skip HEAD version, keep incoming version
        in_conflict = True
        skip_mode = True
        i += 1
        continue
    elif line.startswith('=======') and in_conflict:
        # Switch to keeping incoming version
        skip_mode = False
        i += 1
        continue
    elif line.startswith('>>>>>>>') and in_conflict:
        # End of conflict
        in_conflict = False
        skip_mode = False
        i += 1
        continue
    
    if not skip_mode:
        output.append(line)
    
    i += 1

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(output)

print(f"✅ Fixed! Removed conflict markers and kept newer version.")
print(f"   Original: {len(lines)} lines")
print(f"   Fixed: {len(output)} lines")
print(f"   Removed: {len(lines) - len(output)} lines")
