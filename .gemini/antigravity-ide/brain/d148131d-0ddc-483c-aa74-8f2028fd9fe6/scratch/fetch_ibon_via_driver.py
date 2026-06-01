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

    print("Waiting 10 seconds for page to load and cookies to set...")
    time.sleep(10)
    
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    print("Fetching index data via browser JS...")
    # Execute fetch in the page context
    js_code = """
    return fetch('/api/ActivityInfo/GetIndexData')
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .catch(err => {
            return { error: err.message };
        });
    """
    data = driver.execute_script(js_code)
    
    if "error" in data:
        print(f"Fetch failed: {data['error']}")
    else:
        print("Success! Fetched index data.")
        filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_index_data.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Saved to ibon_index_data.json")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
