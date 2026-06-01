from seleniumbase import Driver
import time
import json

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    
    # Navigate to about:blank first so we can inject script before loading the target page
    driver.get("about:blank")
    
    # Inject interceptor script
    # This script will intercept both fetch and XMLHttpRequest and store the requested URLs and response JSONs
    print("Injecting interceptor...")
    driver.execute_script("""
        window.capturedRequests = [];
        
        // Intercept XMLHttpRequest
        const oldOpen = XMLHttpRequest.prototype.open;
        const oldSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url) {
            this._url = url;
            this._method = method;
            return oldOpen.apply(this, arguments);
        };
        
        XMLHttpRequest.prototype.send = function() {
            this.addEventListener('load', function() {
                try {
                    let responseText = this.responseText;
                    let responseJson = null;
                    try {
                        responseJson = JSON.parse(responseText);
                    } catch(e) {}
                    
                    window.capturedRequests.push({
                        type: 'XHR',
                        method: this._method,
                        url: this._url,
                        response: responseJson || responseText.substring(0, 1000)
                    });
                } catch(err) {}
            });
            return oldSend.apply(this, arguments);
        };
        
        // Intercept fetch
        const oldFetch = window.fetch;
        window.fetch = async function(...args) {
            const response = await oldFetch.apply(this, args);
            const clone = response.clone();
            try {
                const url = args[0];
                let responseJson = null;
                try {
                    responseJson = await clone.json();
                } catch(e) {
                    try {
                        responseJson = await clone.text();
                        responseJson = responseJson.substring(0, 1000);
                    } catch(e2) {}
                }
                
                window.capturedRequests.push({
                    type: 'FETCH',
                    url: url,
                    response: responseJson
                });
            } catch(err) {}
            return response;
        };
    """)
    
    print("Navigating to ibon entertainment...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Navigation Exception/Alert: {e}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass
            
    print("Waiting 10 seconds for page to load and API requests to complete...")
    time.sleep(10)
    
    # Accept alert if still open
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    # Get captured requests
    captured = driver.execute_script("return window.capturedRequests;")
    print(f"Captured {len(captured) if captured else 0} requests.")
    
    output_path = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_captured_apis.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(captured, f, ensure_ascii=False, indent=2)
        
    driver.quit()
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
