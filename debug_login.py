#!/usr/bin/env python3
# this_file: debug_login.py

"""Debug script to check Poe login detection."""

import asyncio

from playwright.async_api import async_playwright


async def check_poe_login():
    """Check if we can detect Poe login status."""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://poe.com")

        # Wait a bit for page to load
        await asyncio.sleep(2)

        # Try different selectors
        selectors_to_try = [
            ("button[aria-label='User menu']", "User menu button"),
            ("button[aria-label*='menu']", "Any menu button"),
            ("button[class*='UserMenu']", "UserMenu class button"),
            ("button[class*='user']", "Any user class button"),
            ("div[class*='UserMenu']", "UserMenu div"),
            ("img[alt*='avatar']", "Avatar image"),
            ("img[alt*='profile']", "Profile image"),
            ("[data-testid='user-menu']", "User menu test id"),
            ("button:has-text('New chat')", "New chat button"),
            ("button:has-text('Settings')", "Settings button"),
        ]

        found_any = False
        for selector, _description in selectors_to_try:
            try:
                element = await page.query_selector(selector)
                if element:
                    found_any = True
                    # Try to get more info
                    try:
                        text = await element.text_content()
                        if text:
                            pass
                    except:
                        pass
                else:
                    pass
            except Exception:
                pass

        if not found_any:
            pass
        else:
            pass

        # Check the page URL

        # Take a screenshot for debugging
        await page.screenshot(path="poe_debug.png")

        input()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(check_poe_login())
