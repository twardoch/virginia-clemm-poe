#!/usr/bin/env python3
# this_file: test_balance.py

"""Test script for Poe balance functionality."""

import asyncio
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from virginia_clemm_poe import api
from virginia_clemm_poe.poe_session import PoeSessionManager


async def test_session_manager():
    """Test the PoeSessionManager functionality."""
    session_manager = PoeSessionManager()

    # Check if we have existing cookies
    has_cookies = session_manager.has_valid_cookies()

    if has_cookies:
        for key in ["p-b", "p-lat", "m-b"]:
            if key in session_manager.cookies:
                pass

    return session_manager


async def test_balance_check():
    """Test getting account balance."""
    try:
        # Check if we have a session
        if not api.has_valid_poe_session():
            return False

        # Get balance
        balance = await api.get_account_balance()

        daily = balance.get("daily_compute_points_available")
        if daily is not None:
            pass

        balance.get("subscription", {})

        return True

    except Exception:
        return False


async def test_cli_commands():
    """Test CLI command availability."""
    commands = [
        "virginia-clemm-poe --help",
        "virginia-clemm-poe balance --help",
        "virginia-clemm-poe login --help",
        "virginia-clemm-poe logout --help",
    ]

    for _cmd in commands:
        pass


async def main():
    """Run all tests."""
    # Test session manager
    session_manager = await test_session_manager()

    # Test balance if we have cookies
    if session_manager.has_valid_cookies():
        success = await test_balance_check()
        if success:
            pass
    else:
        pass

    # Show CLI command info
    await test_cli_commands()


if __name__ == "__main__":
    asyncio.run(main())
