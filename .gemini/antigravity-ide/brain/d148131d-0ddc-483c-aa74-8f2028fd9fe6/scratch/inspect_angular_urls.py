import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# The javascript file from the HTML we dumped
url = "https://ticket.ibon.com.tw/main.49b6b7d0cf85065b.js"

try:
    print(f"Downloading: {url}")
    resp = requests.get(url, headers=headers, timeout=20)
    print(f"Status: {resp.status_code}")
    print(f"Content length: {len(resp.text)}")
    
    js = resp.text
    
    # Find all API-like paths (e.g. /api/... or similar)
    api_paths = re.findall(r'"/api/[^"]+"|\'/api/[^\']+\'', js)
    print(f"Found {len(api_paths)} API paths:")
    for path in set(api_paths)[:30]:
        print(f"  {path}")
        
    # Find all occurrences of "Activity" or "Details"
    activity_matches = re.findall(r'/[A-Za-z0-9]+/Details/[A-Za-z0-9_]+', js)
    print(f"Activity matches: {set(activity_matches)}")
    
except Exception as e:
    print(f"Error: {e}")
