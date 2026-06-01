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
        
    print("Fetching index data via POST FormData...")
    js_code = """
    const formData = new FormData();
    formData.append('pattern', 'entertainment');
    return fetch('/api/ActivityInfo/GetIndexData', {
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
        print("Success! Fetched index data.")
        print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'List of length ' + str(len(data))}")
        
        filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_index_data_formdata.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Saved response to ibon_index_data_formdata.json")
        
        # Let's inspect the data layout
        if isinstance(data, dict):
            # Angular component uses: e.ATAP and e.List
            atap = data.get('ATAP', [])
            lst = data.get('List', [])
            print(f"ATAP count: {len(atap)}, List count: {len(lst)}")
            if lst:
                print("Sample item from List:")
                print(json.dumps(lst[0], ensure_ascii=False, indent=2))
                
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
