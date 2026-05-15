"""Replace problematic quote patterns inside Python source strings."""
import sys, re

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    s = f.read()

# Step 1: replace German typographic opening quotes with escaped ASCII
s = s.replace('„', '\\"')

# Step 2: find paired `\"<text>"` (escaped open + ASCII close inside a string)
# and replace the ASCII close with escaped close.
# Pattern: \\" followed by chars (no quotes), then a single " that is the unmatched close.
s = re.sub(r'\\"([^"\\]*?)"', r'\\"\1\\"', s)

# Step 3: closing typographic quotes
s = s.replace('“', '\\"')
s = s.replace('”', '\\"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(s)

print(f"Fixed {path}")
