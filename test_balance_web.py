#!/usr/bin/env python3
# this_file: test_balance_web.py

"""Test getting balance via web scraping."""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

# Load cookies
cookies_file = Path.home() / "Library" / "Application Support" / "virginia-clemm-poe" / "cookies" / "poe_cookies.json"
with open(cookies_file) as f:
    data = json.load(f)
    stored_cookies = data["cookies"]

for _key in stored_cookies:
    pass


async def test_balance_web():
    """Get balance using browser with cookies."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Add cookies to context
        cookies_to_add = []
        for name, value in stored_cookies.items():
            cookies_to_add.append({"name": name, "value": value, "domain": ".poe.com", "path": "/"})
            # Also add to quora.com domain
            if name in ["p-b", "m-b"]:
                cookies_to_add.append({"name": name, "value": value, "domain": ".quora.com", "path": "/"})

        await context.add_cookies(cookies_to_add)

        page = await context.new_page()

        await page.goto("https://poe.com/settings")

        # Wait a bit for page to load
        await asyncio.sleep(3)

        # Check if we're logged in
        current_url = page.url

        if "/login" in current_url:
            pass
        else:
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
                        for elem in elements[:3]:  # First 3 matches
                            text = await elem.text_content()
                            if text:
                                pass
                except Exception:
                    pass

        input()
        await browser.close()


asyncio.run(test_balance_web())
