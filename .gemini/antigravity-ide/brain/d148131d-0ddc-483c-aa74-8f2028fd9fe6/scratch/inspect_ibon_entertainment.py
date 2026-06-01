from seleniumbase import Driver
from bs4 import BeautifulSoup
import json
import time

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    print("Navigating to ibon...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Exception during navigation: {e}")
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass

    # Let it wait to stabilize
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    # Try one more time to check and accept alerts
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except:
        pass
        
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Let's inspect all links
    links = soup.find_all('a')
    with open("C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_links.txt", "w", encoding="utf-8") as f:
        f.write(f"Total links: {len(links)}\n\n")
        # Find links that are details links
        # Usually they contain ActivityInfo/Details
        detail_links = []
        for a in links:
            href = a.get('href')
            text = a.get_text(strip=True)
            f.write(f"Href: {href}, Text: {text}\n")
            if href and 'ActivityInfo/Details/' in href:
                detail_links.append((href, text))
                
        f.write(f"\n\nFound {len(detail_links)} detail links:\n")
        for href, text in detail_links:
            f.write(f"  Href: {href}, Text: {text}\n")
            
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
