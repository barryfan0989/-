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
        print(f"Alert/Exception: {e}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass

    print("Waiting 10 seconds for XHR requests to complete...")
    time.sleep(10)
    
    # Accept alert if any
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    # Get all network entries via Performance API
    urls = driver.execute_script("return window.performance.getEntries().map(e => e.name)")
    
    output_path = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_network_urls.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Total entries: {len(urls)}\n\n")
        # Filter for API or json endpoints
        api_urls = []
        for url in urls:
            f.write(f"{url}\n")
            if 'api' in url.lower() or 'json' in url.lower() or 'query' in url.lower() or 'post' in url.lower():
                api_urls.append(url)
                
        f.write(f"\n\nAPI / JSON URLs:\n")
        for url in api_urls:
            f.write(f"  {url}\n")
            
    print(f"Captured {len(urls)} URLs. Saved to ibon_network_urls.txt")
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
