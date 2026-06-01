import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get("https://www.indievox.com/events", headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')

print(f"Status: {resp.status_code}")

links = soup.find_all('a', href=lambda h: h and ('/activity/detail/' in h or '/activity/game/' in h))

non_banner_count = 0
for idx, a in enumerate(links):
    classes = a.get('class', [])
    if 'banner-url' in classes:
        continue
    
    non_banner_count += 1
    if non_banner_count > 10:
        break
        
    print(f"\n--- Non-banner Link {non_banner_count} ---")
    print(f"Tag: {a}")
    print(f"Text: {a.get_text(strip=True)}")
    print(f"Href: {a.get('href')}")
    # Print the parent tag and text
    parent = a.parent
    print(f"Parent: <{parent.name} class='{parent.get('class')}'>")
    print(f"Parent Text: {parent.get_text(strip=True)[:300]}")
    # Print grandparent tag and text
    grandparent = parent.parent
    print(f"Grandparent: <{grandparent.name} class='{grandparent.get('class')}'>")
    print(f"Grandparent Text: {grandparent.get_text(strip=True)[:300]}")
