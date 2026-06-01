from curl_cffi import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://ticket.ibon.com.tw/index/entertainment'
}

endpoints = [
    "https://ticket.ibon.com.tw/api/ActivityInfo/GetIndexData",
    "https://ticket.ibon.com.tw/api/Guard/GetActivityData"
]

for url in endpoints:
    print(f"\nFetching: {url}")
    try:
        r = requests.get(url, headers=headers, impersonate="chrome120", timeout=15)
        print(f"Status: {r.status_code}")
        print(f"Content length: {len(r.text)}")
        if r.status_code == 200:
            try:
                data = r.json()
                print("JSON Data loaded successfully.")
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'List of ' + str(len(data))}")
                
                # Save first 5000 chars of json to check
                snippet = json.dumps(data, ensure_ascii=False, indent=2)
                print("Snippet:")
                print(snippet[:500])
                
                # Save to file
                filename = url.split('/')[-1] + ".json"
                filepath = f"C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/{filename}"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(snippet)
                print(f"Saved to {filename}")
            except Exception as je:
                print(f"JSON Parse error: {je}")
                print(r.text[:500])
        else:
            print(r.text[:500])
    except Exception as e:
        print(f"Request error: {e}")
