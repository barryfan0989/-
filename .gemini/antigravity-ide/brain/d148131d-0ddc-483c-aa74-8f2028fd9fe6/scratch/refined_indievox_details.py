import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.indievox.com/activity/detail/26_iv04071b5"
resp = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')

with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/indievox_detail.txt", "w", encoding="utf-8") as f:
    f.write(f"URL: {url}\n")
    f.write(f"Title: {soup.title.get_text(strip=True) if soup.title else None}\n")
    
    # Indievox details section
    # Let's find all divs and print their class and text
    f.write("\n=== ALL DIVS WITH CLASSES ===\n")
    for div in soup.find_all('div'):
        cls = div.get('class')
        if cls:
            f.write(f"Div Class: {cls}\n")
            f.write(f"Text: {div.get_text(strip=True)[:300]}\n")
            f.write("-" * 50 + "\n")
            
    f.write("\n=== ALL LI/P/TABLE ELEMENTS ===\n")
    for elem in soup.find_all(['li', 'p', 'table', 'h1', 'h2', 'h3', 'h4']):
        f.write(f"<{elem.name}>: {elem.get_text(strip=True)}\n")
