import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("Launching chromium...")
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print("Navigating to ibon...")
            await page.goto("https://ticket.ibon.com.tw/index/entertainment", timeout=30000)
            
            # Wait for content to stabilize
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            print(f"Title: {title}")
            print(f"URL: {page.url}")
            
            # Print page content snippet
            content = await page.content()
            print(f"Content length: {len(content)}")
            print(content[:300])
            
            # Check if we got the page or still Turnstile
            if "Enable JavaScript and cookies to continue" in content:
                print("Failed: Still stuck on Turnstile.")
            else:
                print("Success: Bypassed Turnstile!")
                
            await browser.close()
        except Exception as e:
            print(f"Playwright error: {e}")

asyncio.run(main())
