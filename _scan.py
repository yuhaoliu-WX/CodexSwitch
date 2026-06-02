import os

root = "F:\\VibeCoding\\CodexSwitch"
path = os.path.join(root, "main.py")

with open(path, "rb") as f:
    raw = f.read()

text = raw.decode("utf-8")
chars = [(i, ch, hex(ord(ch))) for i, ch in enumerate(text) if ord(ch) > 127]

print(f"Found {len(chars)} non-ASCII chars")

# Build a mapping: for each line, show the corrupted chars
lines = text.split("\n")
for line_no, line in enumerate(lines, 1):
    bad = [(j, ch, hex(ord(ch))) for j, ch in enumerate(line) if ord(ch) > 127]
    if bad:
        print(f"  Line {line_no}: {bad}")
        print(f"    Content: {line}")