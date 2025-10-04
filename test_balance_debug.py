#!/usr/bin/env python3
# this_file: test_balance_debug.py

"""Debug balance API response."""

import asyncio
import json
from pathlib import Path

import httpx

# Load cookies
cookies_file = Path.home() / "Library" / "Application Support" / "virginia-clemm-poe" / "cookies" / "poe_cookies.json"
with open(cookies_file) as f:
    data = json.load(f)
    cookies = data["cookies"]

for _key in cookies:
    pass


async def test_balance():
    """Test the balance API directly."""
    cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())

    headers = {
        "Cookie": cookie_header,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://poe.com/",
    }

    url = "https://www.quora.com/poe_api/settings"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15, follow_redirects=True)

            if response.status_code == 200:
                try:
                    data = response.json()
                    json.dumps(data, indent=2)

                    # Check specific fields

                except Exception:
                    pass
            else:
                pass

        except Exception:
            pass


asyncio.run(test_balance())
