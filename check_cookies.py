#!/usr/bin/env python3
# this_file: check_cookies.py

"""Check if Poe cookies are stored."""

import json
from pathlib import Path

# Check for cookies file
cookies_dir = Path.home() / "Library" / "Application Support" / "virginia-clemm-poe" / "cookies"
cookies_file = cookies_dir / "poe_cookies.json"

print(f"Checking for cookies at: {cookies_file}")
print(f"Directory exists: {cookies_dir.exists()}")
print(f"File exists: {cookies_file.exists()}")

if cookies_file.exists():
    with open(cookies_file) as f:
        data = json.load(f)
    
    print("\nStored cookies:")
    cookies = data.get("cookies", {})
    for key in cookies:
        value = cookies[key]
        # Show only first 10 chars for security
        display_value = value[:10] + "..." if len(value) > 10 else value
        print(f"  {key}: {display_value}")
    
    print(f"\nSaved at: {data.get('saved_at', 'Unknown')}")
else:
    print("\nNo cookies found. Run 'virginia-clemm-poe login' to authenticate.")