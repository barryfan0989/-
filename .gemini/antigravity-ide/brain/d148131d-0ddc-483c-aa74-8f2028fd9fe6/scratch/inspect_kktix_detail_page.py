from curl_cffi import requests
from bs4 import BeautifulSoup
import json

url = "https://newtaipeikings.kktix.cc/events/c8bb7293"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    print(f"Fetching KKTIX event detail: {url}")
    r = requests.get(url, impersonate="chrome120", timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/kktix_detail.txt", "w", encoding="utf-8") as f:
        f.write(f"Title: {soup.title.get_text(strip=True) if soup.title else None}\n")
        
        # Let's inspect some key divs for tickets (prices/types) or JSON-LD
        # KKTIX event pages usually have a JSON-LD block with Schema.org Event data (which contains tickets and dates!)
        json_ld_tags = soup.find_all('script', type='application/ld+json')
        f.write(f"\nFound {len(json_ld_tags)} JSON-LD blocks\n")
        for idx, tag in enumerate(json_ld_tags):
            f.write(f"--- JSON-LD Block {idx} ---\n")
            f.write(tag.string + "\n")
            
        # Also look for elements with class 'ticket' or similar
        f.write("\n--- HTML Text Elements ---\n")
        for tag in soup.find_all(['h1', 'h2', 'span', 'p', 'table']):
            cls = tag.get('class')
            text = tag.get_text(strip=True)
            if text and cls:
                f.write(f"<{tag.name} class='{cls}'>: {text[:150]}\n")
                
except Exception as e:
    print(f"Error: {e}")
