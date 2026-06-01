from bs4 import BeautifulSoup
import re

file_path = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_page.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a')

output_path = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_parsed_links.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"Total links: {len(links)}\n\n")
    
    # Let's write all links with their texts
    for idx, a in enumerate(links):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        f.write(f"[{idx}] Href: {href}, Text: {text}\n")
        
    # Search for ActivityInfo patterns
    activity_ids = re.findall(r'ActivityInfo/Details/[A-Za-z0-9_]+', html)
    f.write(f"\nActivity detail patterns: {set(activity_ids)}\n")

print("Saved parsed links to ibon_parsed_links.txt")
