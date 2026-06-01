from curl_cffi import requests
import re

url = "https://ticket.ibon.com.tw/main.49b6b7d0cf85065b.js"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://ticket.ibon.com.tw/index/entertainment'
}

try:
    print(f"Downloading: {url}")
    r = requests.get(url, headers=headers, impersonate="chrome120", timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Length: {len(r.text)}")
    
    if r.status_code == 200:
        js = r.text
        # Write to a scratch file first
        with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/main.js", "w", encoding="utf-8") as f:
            f.write(js)
        print("Saved main.js.")
        
        # Let's search for "GetIndexData" in the javascript to see the parameters it sends!
        matches = [m.start() for m in re.finditer("GetIndexData", js)]
        print(f"Found {len(matches)} occurrences of GetIndexData:")
        for idx, start in enumerate(matches):
            print(f"\n--- Match {idx} ---")
            print(js[max(0, start - 300) : min(len(js), start + 300)])
            
    else:
        print(r.text[:500])
except Exception as e:
    print(f"Error: {e}")
