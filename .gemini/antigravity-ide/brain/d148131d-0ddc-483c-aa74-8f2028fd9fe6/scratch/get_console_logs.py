from seleniumbase import Driver
import time

try:
    print("Launching SeleniumBase UC with console logging enabled...")
    # Enable browser logging
    driver = Driver(uc=True, headless=True, log_cdp=True)
    
    print("Navigating to ibon...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Exception: {e}")
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
        
    print("Retrieving console logs...")
    logs = driver.get_log("browser")
    print(f"Found {len(logs)} logs.")
    for entry in logs:
        print(f"[{entry['level']}] {entry['message']}")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
