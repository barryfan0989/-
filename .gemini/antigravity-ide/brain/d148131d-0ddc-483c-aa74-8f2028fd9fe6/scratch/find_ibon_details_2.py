with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_page.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
matches = [m.start() for m in re.finditer("博麗", html)]

for start in matches:
    print("\n--- Match ---")
    print(html[max(0, start - 250) : min(len(html), start + 250)])
