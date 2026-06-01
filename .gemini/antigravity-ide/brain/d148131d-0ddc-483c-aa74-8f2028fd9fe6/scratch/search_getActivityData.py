import re

with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/main.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's search for "GetActivityData"
matches = [m.start() for m in re.finditer(r"GetActivityData", js)]
print(f"Found {len(matches)} occurrences of GetActivityData:")
for idx, start in enumerate(matches):
    print(f"\n--- Match {idx} ---")
    print(js[max(0, start - 300) : min(len(js), start + 300)])
    
# Let's search for "getActivityData"
matches2 = [m.start() for m in re.finditer(r"getActivityData", js)]
print(f"Found {len(matches2)} occurrences of getActivityData:")
for idx, start in enumerate(matches2):
    print(f"\n--- Match {idx} ---")
    print(js[max(0, start - 300) : min(len(js), start + 300)])
