#!/usr/bin/env python3
# this_file: test_balance_numeric.py

"""Test that balance values are stored as integers."""

import asyncio
import json
from pathlib import Path
from virginia_clemm_poe import api
from virginia_clemm_poe.poe_session import PoeSessionManager

async def test_balance_numeric():
    """Test that balance is stored as numeric value."""
    
    # Get session manager
    session_manager = api.get_session_manager()
    
    # Check if we have cached balance
    if session_manager._balance_cache:
        balance = session_manager._balance_cache
        points = balance.get("compute_points_available")
        
        print(f"Cached balance type: {type(points)}")
        print(f"Cached balance value: {points}")
        print(f"Cached balance repr: {repr(points)}")
        
        if isinstance(points, int):
            print(f"✅ Balance is correctly stored as integer: {points}")
            print(f"   Formatted display: {points:,}")
        else:
            print(f"❌ Balance is NOT an integer, it's a {type(points)}: {points}")
    
    # Try to get fresh balance
    print("\nFetching fresh balance...")
    try:
        balance = await api.get_account_balance(force_refresh=True, use_browser=False)
        points = balance.get("compute_points_available")
        
        print(f"Fresh balance type: {type(points)}")
        print(f"Fresh balance value: {points}")
        print(f"Fresh balance repr: {repr(points)}")
        
        if points is not None:
            if isinstance(points, int):
                print(f"✅ Fresh balance is correctly stored as integer: {points}")
                print(f"   Formatted display: {points:,}")
            else:
                print(f"❌ Fresh balance is NOT an integer, it's a {type(points)}: {points}")
                
        # Check cache file directly
        cache_path = session_manager.balance_cache_path
        if cache_path.exists():
            print(f"\nCache file location: {cache_path}")
            with open(cache_path) as f:
                cache_data = json.load(f)
                cached_points = cache_data.get("balance", {}).get("compute_points_available")
                print(f"Cache file balance type: {type(cached_points)}")
                print(f"Cache file balance value: {cached_points}")
                
    except Exception as e:
        print(f"Error fetching balance: {e}")

if __name__ == "__main__":
    asyncio.run(test_balance_numeric())