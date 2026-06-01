from seleniumbase import Driver
import time
import json

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    print("Navigating to ibon...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Exception during navigation: {e}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass

    print("Waiting 10 seconds...")
    time.sleep(10)
    
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    # Let's try to send POST request with different payloads
    payloads = [
        "{}",
        '{"CategoryCode": "homepage"}',
        '{"inATAPWebType": "homepage"}'
    ]
    
    for payload in payloads:
        print(f"\nFetching index data via POST with payload: {payload}")
        js_code = f"""
        return fetch('/api/ActivityInfo/GetIndexData', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: '{payload}'
        }})
        .then(response => {{
            if (!response.ok) {{
                throw new Error('HTTP error ' + response.status);
            }}
            return response.json();
        }})
        .catch(err => {{
            return {{ error: err.message }};
        }});
        """
        data = driver.execute_script(js_code)
        
        if "error" in data:
            print(f"Fetch failed: {data['error']}")
        else:
            print("Success! Fetched index data.")
            print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'List of length ' + str(len(data))}")
            snippet = json.dumps(data, ensure_ascii=False, indent=2)
            print(snippet[:500])
            
            filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_index_data_post.json"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(snippet)
            print("Saved response to ibon_index_data_post.json")
            break
            
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
