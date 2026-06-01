from seleniumbase import Driver
from bs4 import BeautifulSoup
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
            
    print("Waiting 10 seconds...")
    time.sleep(10)
    
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all cover links or other links inside the event cards
    # We saw: <a _ngcontent-uai-c42="" href="javascript:void" class="cover ng-star-inserted" ...>
    covers = soup.find_all('a', class_='cover')
    print(f"Found {len(covers)} cover elements.")
    for idx, cov in enumerate(covers[:10]):
        print(f"\n[{idx}] Cover Element:")
        print(f"  Tag: {cov.name}")
        print(f"  Attributes: {cov.attrs}")
        print(f"  Title: {cov.get('title')}")
        print(f"  Text: {cov.get_text(strip=True)}")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
