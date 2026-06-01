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
        
    print("Fetching detail data for ID 39527 via POST FormData...")
    js_code = """
    const formData = new FormData();
    formData.append('id', '39527');
    return fetch('/api/ActivityInfo/GetDetailData', {
        method: 'POST',
        body: formData
    })
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
        print("Success! Fetched detail data.")
        filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_detail_data_formdata.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Saved response to ibon_detail_data_formdata.json")
        
        # Let's inspect the keys and content
        print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
