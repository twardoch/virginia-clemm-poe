#!/usr/bin/env python3
# this_file: test_session.py

"""Test PoeSessionManager directly."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from virginia_clemm_poe.poe_session import PoeSessionManager

# Create session manager
session_manager = PoeSessionManager()


# Check what cookies we need
