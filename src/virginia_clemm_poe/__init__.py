# this_file: src/virginia_clemm_poe/__init__.py

"""Virginia Clemm Poe - Poe.com bot data management.

A Python package providing programmatic access to Poe.com bot data
with pricing information.
"""

# Version handling
try:
    from ._version import __version__, __version_tuple__
except ImportError:
    __version__ = "0.0.0.dev0"
    __version_tuple__ = (0, 0, 0, "dev0")

# Public API exports
from . import api
from .bots import Architecture, BotCollection, PoeBot, Pricing, PricingDetails

__all__ = [
    "__version__",
    "__version_tuple__",
    "api",
    "PoeBot",
    "BotCollection",
    "Pricing",
    "PricingDetails",
    "Architecture",
]
