import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

resp = requests.get("https://www.indievox.com/events", headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')

print(f"Status: {resp.status_code}")

links = soup.find_all('a', href=lambda h: h and ('/activity/detail/' in h or '/activity/game/' in h))

for idx, a in enumerate(links[:20]):
    href = a.get('href')
    # Print the link tag itself
    print(f"\n[{idx}] Link tag: {a}")
    print(f"  Parent: <{a.parent.name} class='{a.parent.get('class')}'>")
    # Print content of parent
    print(f"  Parent text: {a.parent.get_text(strip=True)[:150]}")
    # Print siblings
    siblings = [s.name for s in a.next_siblings if s.name]
    print(f"  Next siblings: {siblings}")
    
    # If the text is empty inside the link, check if there is an image inside it
    img = a.find('img')
    if img:
        print(f"  Has image: src={img.get('src')}, alt={img.get('alt')}")
