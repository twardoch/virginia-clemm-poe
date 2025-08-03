# this_file: src/virginia_clemm_poe/__init__.py

"""Virginia Clemm Poe - Poe.com model data management.

A Python package providing programmatic access to Poe.com model data
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
from .models import Architecture, ModelCollection, PoeModel, Pricing, PricingDetails

__all__ = [
    "__version__",
    "__version_tuple__",
    "api",
    "PoeModel",
    "ModelCollection",
    "Pricing",
    "PricingDetails",
    "Architecture",
]
