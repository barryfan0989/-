import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# We will test Era (ticket.com.tw) detail page:
# https://ticket.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P1AFRHGU
# We will test Kham detail page:
# https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P1B1P9TA

with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/utk_events_debug.txt", "w", encoding="utf-8") as f:
    for site, url in [("Era", "https://ticket.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P1AFRHGU"),
                     ("Kham", "https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P1B1P9TA")]:
        f.write(f"\n=========================================\n")
        f.write(f"Site: {site}, URL: {url}\n")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Print page title
            title = soup.title.get_text(strip=True) if soup.title else "No Title"
            f.write(f"Title: {title}\n")
            
            # Look for Event Name, Date, Venue, Tickets on detail page
            # Usually there is an event info box
            # Let's search for elements with class 'info' or 'detail' or printing some text
            f.write("\n--- Key text sections ---\n")
            for elem in soup.find_all(['h1', 'h2', 'h3', 'span', 'p', 'table', 'li']):
                cls = elem.get('class')
                text = elem.get_text(strip=True)
                if text:
                    f.write(f"<{elem.name} class='{cls}'>: {text[:200]}\n")
                    
        except Exception as e:
            f.write(f"Error fetching/parsing: {e}\n")
