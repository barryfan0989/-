import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://ticket.com.tw"
try:
    print(f"Fetching: {url}")
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Content length: {len(resp.text)}")
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Save a portion of links to see what is there
    links = soup.find_all('a')
    print(f"Total links: {len(links)}")
    for idx, a in enumerate(links[:50]):
        print(f"  {idx}: text='{a.get_text(strip=True)}', href='{a.get('href')}'")
        
except Exception as e:
    print(f"Error: {e}")
