from curl_cffi import requests
import json

r = requests.get("https://kktix.com/events.json", impersonate="chrome120")
data = r.json()

print(f"Keys in JSON: {list(data.keys())}")
print(f"Total entries: {len(data.get('entry', []))}")

# Print first entry details
if data.get('entry'):
    entry = data['entry'][0]
    print("\nFirst Entry Keys:", list(entry.keys()))
    print(f"Title: {entry.get('title')}")
    print(f"Url: {entry.get('url')}")
    print(f"Published: {entry.get('published')}")
    print(f"Content: {entry.get('content')[:300] if entry.get('content') else None}")
    print(f"Author name: {entry.get('author', {}).get('name') if entry.get('author') else None}")
    
    # Save a snippet of JSON to verify
    with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/kktix_sample.json", "w", encoding="utf-8") as f:
        json.dump(data.get('entry', [])[:5], f, ensure_ascii=False, indent=2)
