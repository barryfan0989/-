import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.indievox.com/activity/detail/26_iv04071b5"
resp = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')

print(f"Status: {resp.status_code}")
print(f"Title: {soup.title.get_text(strip=True) if soup.title else None}")

# Find event info blocks
# Usually there is an info block containing date, venue, etc.
# Let's inspect all text or elements in the page that might contain these.
for div in soup.find_all('div', class_=lambda c: c and any(x in c for x in ['info', 'detail', 'meta', 'ticket'])):
    print(f"Div class: {div.get('class')}")
    print(f"Clean text: {div.get_text(strip=True)[:200]}")
    print("-" * 30)

# Let's print out the clean text of key sections of the page to find where details are stored
print("\n--- Summary text of key divs ---")
for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'table', 'ul']):
    text = element.get_text(strip=True)
    if text:
        print(f"<{element.name}>: {text[:150]}")
