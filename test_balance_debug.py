#!/usr/bin/env python3
# this_file: test_balance_debug.py

"""Debug balance API response."""

import asyncio
import json
import httpx
from pathlib import Path

# Load cookies
cookies_file = Path.home() / "Library" / "Application Support" / "virginia-clemm-poe" / "cookies" / "poe_cookies.json"
with open(cookies_file) as f:
    data = json.load(f)
    cookies = data["cookies"]

print("Cookies loaded:")
for key in cookies:
    print(f"  {key}: {cookies[key][:10]}...")

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
    
    print(f"\nFetching: {url}")
    print(f"Cookie header length: {len(cookie_header)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=15, follow_redirects=True)
            print(f"Status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"\nResponse JSON (first 500 chars):")
                    json_str = json.dumps(data, indent=2)
                    print(json_str[:500])
                    
                    # Check specific fields
                    print("\nKey fields:")
                    print(f"  computePointsAvailable: {data.get('computePointsAvailable')}")
                    print(f"  dailyComputePointsAvailable: {data.get('dailyComputePointsAvailable')}")
                    print(f"  subscription: {data.get('subscription')}")
                    
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Response text: {response.text[:500]}")
            else:
                print(f"Response text: {response.text[:500]}")
                
        except Exception as e:
            print(f"Request failed: {e}")

asyncio.run(test_balance())