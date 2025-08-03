# this_file: src/virginia_clemm_poe/utils.py

"""Utility functions for Virginia Clemm Poe."""

from datetime import datetime
from typing import Any


def json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def format_points_cost(points: str) -> str:
    """Format points cost string for display."""
    # Extract numeric value and unit
    # e.g., "12 points/1k tokens" -> "12 pts/1k"
    parts = points.split()
    if len(parts) >= 3:
        value = parts[0]
        unit = parts[2] if len(parts) > 2 else ""
        return f"{value} pts/{unit}"
    return points
