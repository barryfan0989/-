import sys
sys.stdout.reconfigure(encoding='utf-8')
from scrapling.fetchers import Fetcher

url = "https://kktix.com/events.json"
r = Fetcher.get(url, impersonate="chrome120", follow_redirects=True)
data = r.json()
print("Total entries:", len(data.get('entry', [])))
for idx, entry in enumerate(data.get('entry', [])[:10]):
    print(f"[{idx}] Title: {entry.get('title')}")
    print(f"    Summary: {entry.get('summary')[:100] if entry.get('summary') else ''}")
