#!/usr/bin/env python3
# this_file: test_session.py

"""Test PoeSessionManager directly."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from virginia_clemm_poe.poe_session import PoeSessionManager

# Create session manager
session_manager = PoeSessionManager()

print(f"Cookies directory: {session_manager.cookies_dir}")
print(f"Cookies file: {session_manager.cookies_path}")
print(f"File exists: {session_manager.cookies_path.exists()}")
print(f"Cookies loaded: {session_manager.cookies}")
print(f"Has valid cookies: {session_manager.has_valid_cookies()}")

# Check what cookies we need
print("\nChecking for required cookies:")
print(f"  p-b: {'p-b' in session_manager.cookies}")
print(f"  p-lat: {'p-lat' in session_manager.cookies}")