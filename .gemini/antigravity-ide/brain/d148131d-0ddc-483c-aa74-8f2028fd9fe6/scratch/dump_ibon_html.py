from seleniumbase import Driver
import time

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    print("Navigating to ibon...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Exception: {e}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass
            
    print("Waiting 10 seconds for Angular/SPA loading...")
    time.sleep(10)
    
    # Try one more time to close alert if popped up
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    html = driver.page_source
    print(f"Content length: {len(html)}")
    
    with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_page.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    driver.quit()
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
