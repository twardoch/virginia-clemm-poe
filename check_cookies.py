#!/usr/bin/env python3
# this_file: check_cookies.py

"""Check if Poe cookies are stored."""

import json
from pathlib import Path

# Check for cookies file
cookies_dir = Path.home() / "Library" / "Application Support" / "virginia-clemm-poe" / "cookies"
cookies_file = cookies_dir / "poe_cookies.json"


if cookies_file.exists():
    with open(cookies_file) as f:
        data = json.load(f)

    cookies = data.get("cookies", {})
    for key in cookies:
        value = cookies[key]
        # Show only first 10 chars for security
        display_value = value[:10] + "..." if len(value) > 10 else value

else:
    pass
