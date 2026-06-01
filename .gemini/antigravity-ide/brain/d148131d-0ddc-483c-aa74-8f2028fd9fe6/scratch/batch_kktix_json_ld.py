from curl_cffi import requests
from bs4 import BeautifulSoup
import json

r = requests.get("https://kktix.com/events.json", impersonate="chrome120")
data = r.json()

events_to_test = data.get('entry', [])[:10]

for idx, entry in enumerate(events_to_test):
    url = entry.get('url')
    try:
        r_detail = requests.get(url, impersonate="chrome120", timeout=10)
        soup = BeautifulSoup(r_detail.text, 'html.parser')
        json_ld_tags = soup.find_all('script', type='application/ld+json')
        print(f"\n[{idx}] Event: {entry.get('title')}")
        print(f"  URL: {url}")
        print(f"  JSON-LD Blocks: {len(json_ld_tags)}")
        for tag in json_ld_tags:
            try:
                ld = json.loads(tag.string)
                if isinstance(ld, list):
                    ld = ld[0]
                print(f"  Start: {ld.get('startDate')}")
                print(f"  Location: {ld.get('location', {}).get('name')}")
                offers = ld.get('offers', [])
                print(f"  Offers: {len(offers)} ticket types")
                for offer in offers[:3]:
                    print(f"    - {offer.get('name')}: {offer.get('price')} {offer.get('priceCurrency')}")
            except Exception as je:
                print(f"  JSON parse error: {je}")
    except Exception as e:
        print(f"  Fetch error: {e}")
