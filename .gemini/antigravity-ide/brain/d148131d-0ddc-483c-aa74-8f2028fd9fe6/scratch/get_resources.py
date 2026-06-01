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

    print("Waiting 10 seconds...")
    time.sleep(10)
    
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    # Get all resource entries
    resources = driver.execute_script("return window.performance.getEntriesByType('resource').map(e => ({name: e.name, initiatorType: e.initiatorType}))")
    print(f"Found {len(resources)} resources.")
    for idx, r in enumerate(resources):
        print(f"[{idx}] {r['initiatorType']}: {r['name']}")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
