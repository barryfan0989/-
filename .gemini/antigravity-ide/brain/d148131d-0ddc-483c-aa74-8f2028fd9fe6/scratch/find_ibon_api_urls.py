from seleniumbase import Driver
import time

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    print("Navigating to ibon...")
    driver.get("https://ticket.ibon.com.tw/index/entertainment")
    
    # Wait for the alert to pop up and dismiss it
    time.sleep(2)
    try:
        alert = driver.switch_to.alert
        print(f"Dismissing alert: {alert.text}")
        alert.accept()
    except Exception as e:
        print(f"No alert or error: {e}")
        
    print("Waiting 10 seconds for SPA requests to complete...")
    time.sleep(10)
    
    # Try one more time in case alert popped up again
    try:
        alert = driver.switch_to.alert
        print(f"Dismissing second alert: {alert.text}")
        alert.accept()
    except:
        pass
        
    # Get all URLs via Performance API
    urls = driver.execute_script("return window.performance.getEntries().map(e => e.name)")
    print(f"Total urls: {len(urls)}")
    
    with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_api_found.txt", "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")
            
    driver.quit()
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
