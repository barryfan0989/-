from curl_cffi import requests

try:
    print("Testing ibon entertainment page...")
    r = requests.get("https://ticket.ibon.com.tw/index/entertainment", impersonate="chrome120", timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
    print(r.text[:300])
except Exception as e:
    print(f"Error: {e}")
