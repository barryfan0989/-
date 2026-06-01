with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Look for script tags
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
scripts = soup.find_all('script')

print(f"Total script tags: {len(scripts)}")
for idx, s in enumerate(scripts):
    src = s.get('src')
    if src:
        print(f"  [{idx}] Src: {src}")
    else:
        content = s.string or ""
        print(f"  [{idx}] Inline Script (len={len(content)}): {content[:100]}...")

# Check if there are any JSON-like structures in the HTML body or script tags
import re
json_strings = re.findall(r'\{"[^"]+":.*\}', html)
print(f"JSON-like patterns: {len(json_strings)}")
