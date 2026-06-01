import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Era Ticket (ticket.com.tw) Concerts Category
url1 = "https://ticket.com.tw/application/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=163"
# Kham Concerts Category
url2 = "https://kham.com.tw/application/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=205"

for url in [url1, url2]:
    try:
        print(f"\nFetching: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for links with PRODUCT_ID
        links = soup.find_all('a', href=lambda h: h and 'PRODUCT_ID=' in h)
        print(f"Found {len(links)} event links with PRODUCT_ID")
        
        # Let's inspect some links and their containing divs/cards
        seen = set()
        for idx, a in enumerate(links):
            href = a.get('href')
            if href in seen:
                continue
            seen.add(href)
            print(f"  Event link: {href}")
            print(f"    Text: {a.get_text(strip=True)}")
            
            # Print parent block
            p = a.parent
            while p and p.name != 'body':
                if p.name in ['div', 'li'] and p.get('class'):
                    print(f"    Parent: <{p.name} class='{' '.join(p.get('class'))}'>")
                    print(f"    Parent Text: {p.get_text(strip=True)[:200]}")
                    break
                p = p.parent
            print("-" * 40)
            if len(seen) >= 3:
                break
                
    except Exception as e:
        print(f"Error: {e}")
