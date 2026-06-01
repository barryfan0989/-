import requests

try:
    resp = requests.get("https://ibonticket.com", timeout=10)
    print(f"ibonticket.com status: {resp.status_code}")
    print(f"Final URL: {resp.url}")
except Exception as e:
    print(f"Error: {e}")
