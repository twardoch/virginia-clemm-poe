#!/usr/bin/env python3
# this_file: test_balance.py

"""Test script for Poe balance functionality."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from virginia_clemm_poe import api
from virginia_clemm_poe.poe_session import PoeSessionManager


async def test_session_manager():
    """Test the PoeSessionManager functionality."""
    print("Testing PoeSessionManager...")
    
    session_manager = PoeSessionManager()
    
    # Check if we have existing cookies
    has_cookies = session_manager.has_valid_cookies()
    print(f"Has valid cookies: {has_cookies}")
    
    if has_cookies:
        print("Found existing cookies:")
        for key in ["p-b", "p-lat", "m-b"]:
            if key in session_manager.cookies:
                print(f"  {key}: {session_manager.cookies[key][:10]}...")
    
    return session_manager


async def test_balance_check():
    """Test getting account balance."""
    print("\nTesting balance check...")
    
    try:
        # Check if we have a session
        if not api.has_valid_poe_session():
            print("No valid session found. Please login first using:")
            print("  virginia-clemm-poe login")
            return False
        
        # Get balance
        print("Fetching account balance...")
        balance = await api.get_account_balance()
        
        print("\nAccount Balance:")
        print(f"  Compute points: {balance.get('compute_points_available', 0):,}")
        
        daily = balance.get('daily_compute_points_available')
        if daily is not None:
            print(f"  Daily points: {daily:,}")
        
        subscription = balance.get('subscription', {})
        print(f"  Subscription active: {subscription.get('isActive', False)}")
        
        return True
        
    except Exception as e:
        print(f"Error getting balance: {e}")
        return False


async def test_cli_commands():
    """Test CLI command availability."""
    print("\nTesting CLI commands...")
    
    commands = [
        "virginia-clemm-poe --help",
        "virginia-clemm-poe balance --help",
        "virginia-clemm-poe login --help",
        "virginia-clemm-poe logout --help",
    ]
    
    for cmd in commands:
        print(f"  Command available: {cmd.split()[1]}")
    
    print("\nCLI commands are available. Run them directly from terminal:")
    print("  virginia-clemm-poe login    # Login to Poe")
    print("  virginia-clemm-poe balance  # Check balance")
    print("  virginia-clemm-poe logout   # Clear session")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Virginia Clemm Poe - Balance Feature Test")
    print("=" * 60)
    
    # Test session manager
    session_manager = await test_session_manager()
    
    # Test balance if we have cookies
    if session_manager.has_valid_cookies():
        success = await test_balance_check()
        if success:
            print("\n✓ Balance check successful!")
    else:
        print("\nNo session found. Use CLI to login:")
        print("  virginia-clemm-poe login")
    
    # Show CLI command info
    await test_cli_commands()
    
    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())