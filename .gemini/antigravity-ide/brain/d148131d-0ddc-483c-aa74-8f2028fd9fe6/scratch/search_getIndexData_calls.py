import re

with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/main.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's search for "getIndexData(" in the javascript file
matches = [m.start() for m in re.finditer(r"getIndexData\(", js)]
print(f"Found {len(matches)} calls to getIndexData:")
for idx, start in enumerate(matches):
    print(f"\n--- Call Match {idx} ---")
    print(js[max(0, start - 300) : min(len(js), start + 300)])
