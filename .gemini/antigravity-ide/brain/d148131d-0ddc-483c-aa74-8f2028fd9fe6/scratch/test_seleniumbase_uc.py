from seleniumbase import Driver
import time

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    print("Navigating to ibon...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Exception during navigation: {e}")
        # Try to accept alert if open
        try:
            alert = driver.switch_to.alert
            print(f"Alert text: {alert.text}")
            alert.accept()
            print("Alert accepted!")
        except Exception as alert_err:
            print(f"No alert found or error accepting: {alert_err}")

    # Let it wait to stabilize
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    # Try one more time to check and accept alerts
    try:
        alert = driver.switch_to.alert
        print(f"Alert text found on second check: {alert.text}")
        alert.accept()
        print("Alert accepted on second check!")
    except:
        pass
        
    title = driver.title
    print(f"Title: {title}")
    print(f"URL: {driver.current_url}")
    
    content = driver.page_source
    print(f"Content length: {len(content)}")
    print(content[:300])
    
    if "Enable JavaScript and cookies to continue" in content or "Just a moment..." in title:
        print("Failed: Still stuck on Turnstile.")
    else:
        print("Success: Bypassed Turnstile and handled alert!")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
