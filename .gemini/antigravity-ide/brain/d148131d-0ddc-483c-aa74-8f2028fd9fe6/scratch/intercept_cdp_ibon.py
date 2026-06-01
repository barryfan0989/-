from seleniumbase import Driver
import time
import json

try:
    print("Launching SeleniumBase UC...")
    driver = Driver(uc=True, headless=True)
    
    # Enable Page and Network domains in CDP
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Page.enable", {})
    
    # Inject script that runs before any page scripts load
    interceptor_js = """
    (function() {
        window.capturedRequests = [];
        
        // Intercept XMLHttpRequest
        const oldOpen = XMLHttpRequest.prototype.open;
        const oldSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url) {
            this._url = url;
            this._method = method;
            return oldOpen.apply(this, arguments);
        };
        
        XMLHttpRequest.prototype.send = function(body) {
            const self = this;
            this._body = body;
            this.addEventListener('load', function() {
                try {
                    let responseText = self.responseText;
                    let responseJson = null;
                    try {
                        responseJson = JSON.parse(responseText);
                    } catch(e) {}
                    
                    window.capturedRequests.push({
                        type: 'XHR',
                        method: self._method,
                        url: self._url,
                        payload: self._body,
                        response: responseJson || responseText.substring(0, 500)
                    });
                } catch(err) {}
            });
            return oldSend.apply(this, arguments);
        };
        
        // Intercept Fetch
        const oldFetch = window.fetch;
        window.fetch = async function(...args) {
            const url = args[0];
            const options = args[1] || {};
            const method = options.method || 'GET';
            const body = options.body;
            
            const response = await oldFetch.apply(this, args);
            const clone = response.clone();
            try {
                let responseJson = null;
                try {
                    responseJson = await clone.json();
                } catch(e) {
                    try {
                        responseJson = await clone.text();
                        responseJson = responseJson.substring(0, 500);
                    } catch(e2) {}
                }
                
                window.capturedRequests.push({
                    type: 'FETCH',
                    method: method,
                    url: url,
                    payload: body,
                    response: responseJson
                });
            } catch(err) {}
            return response;
        };
    })();
    """
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": interceptor_js})
    print("CDP Interceptor script added successfully.")
    
    print("Navigating to ibon...")
    try:
        driver.get("https://ticket.ibon.com.tw/index/entertainment")
    except Exception as e:
        print(f"Exception during navigation: {e}")
        try:
            driver.switch_to.alert.accept()
        except:
            pass

    print("Waiting 12 seconds for API requests...")
    time.sleep(12)
    
    try:
        driver.switch_to.alert.accept()
    except:
        pass
        
    print("Retrieving captured requests...")
    captured = driver.execute_script("return window.capturedRequests;")
    
    if captured:
        print(f"Captured {len(captured)} requests.")
        output_path = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_captured_details.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(captured, f, ensure_ascii=False, indent=2)
        print("Saved detailed requests to ibon_captured_details.json")
    else:
        print("No requests captured.")
        
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
