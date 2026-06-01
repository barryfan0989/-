import time
from scrapling.fetchers import DynamicFetcher

result_holder = {}

def my_action(page):
    print("Page navigated. Waiting for stability...")
    # Wait for page load
    page.wait_for_timeout(5000)
    
    # Try accepting any dialog/alert
    page.on("dialog", lambda dialog: dialog.accept())
    
    print("Executing GetIndexData fetch inside page...")
    js_code = """
    (() => {
        const formData = new FormData();
        formData.append('pattern', 'entertainment');
        return fetch('/api/ActivityInfo/GetIndexData', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .catch(err => {
            return { error: err.message };
        });
    })()
    """
    try:
        res = page.evaluate(js_code)
        result_holder["data"] = res
        print("Fetch executed successfully.")
    except Exception as e:
        print("Error evaluating JS:", e)

print("Starting DynamicFetcher fetch...")
response = DynamicFetcher.fetch(
    "https://ticket.ibon.com.tw/index/entertainment",
    page_action=my_action,
    timeout=60000
)

print("Finished fetch.")
data = result_holder.get("data")
if data:
    if "error" in data:
        print("API error:", data["error"])
    else:
        activities = data.get('Item', {}).get('List', [])
        print(f"Successfully retrieved {len(activities)} activities.")
        if activities:
            print("First activity name:", activities[0].get('ActivityName'))
else:
    print("No data retrieved.")
