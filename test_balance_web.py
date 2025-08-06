#!/usr/bin/env python3
# this_file: test_balance_web.py

"""Test getting balance via web scraping."""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

# Load cookies
cookies_file = Path.home() / "Library" / "Application Support" / "virginia-clemm-poe" / "cookies" / "poe_cookies.json"
with open(cookies_file) as f:
    data = json.load(f)
    stored_cookies = data["cookies"]

print("Stored cookies:")
for key in stored_cookies:
    print(f"  {key}: {stored_cookies[key][:10]}...")

async def test_balance_web():
    """Get balance using browser with cookies."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Add cookies to context
        cookies_to_add = []
        for name, value in stored_cookies.items():
            cookies_to_add.append({
                "name": name,
                "value": value,
                "domain": ".poe.com",
                "path": "/"
            })
            # Also add to quora.com domain
            if name in ["p-b", "m-b"]:
                cookies_to_add.append({
                    "name": name,
                    "value": value,
                    "domain": ".quora.com",
                    "path": "/"
                })
        
        await context.add_cookies(cookies_to_add)
        
        page = await context.new_page()
        
        print("\nNavigating to Poe settings...")
        await page.goto("https://poe.com/settings")
        
        # Wait a bit for page to load
        await asyncio.sleep(3)
        
        # Check if we're logged in
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if "/login" in current_url:
            print("Not logged in - cookies might be expired")
        else:
            print("Logged in successfully!")
            
            # Try to find compute points info
            # Look for elements that might contain balance info
            selectors = [
                "text=/Compute points/i",
                "text=/points available/i",
                "text=/subscription/i",
                "[class*='points']",
                "[class*='balance']",
                "[class*='compute']",
            ]
            
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"Found {len(elements)} elements matching: {selector}")
                        for elem in elements[:3]:  # First 3 matches
                            text = await elem.text_content()
                            if text:
                                print(f"  Text: {text[:100]}")
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
        
        print("\nPress Enter to close browser...")
        input()
        await browser.close()

asyncio.run(test_balance_web())