# this_file: src/virginia_clemm_poe/config.py

"""Configuration constants for Virginia Clemm Poe."""

from pathlib import Path

# Package paths
PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / "data"
DATA_FILE_PATH = DATA_DIR / "poe_models.json"

# API configuration
POE_API_URL = "https://api.poe.com/v1/models"
POE_BASE_URL = "https://poe.com/{id}"

# Browser configuration
DEFAULT_DEBUG_PORT = 9222
CDP_VERSION_URL = "http://localhost:{port}/json/version"
BROWSER_CONNECT_RETRY_INTERVAL_SECONDS = 1.0
BROWSER_CONNECT_MAX_ATTEMPTS = 10

# Scraping configuration
LOAD_TIMEOUT_MS = 30_000
TABLE_TIMEOUT_MS = 10_000
PAUSE_SECONDS = 2.0
EXPANSION_WAIT_SECONDS = 0.5  # Wait time after clicking "View more" button
DIALOG_WAIT_SECONDS = 1.0     # Wait time for modal dialog to appear
MODAL_CLOSE_WAIT_SECONDS = 0.5  # Wait time after closing modal

# Network configuration
API_TIMEOUT_SECONDS = 5.0     # Timeout for API health checks
NETWORK_TIMEOUT_SECONDS = 5.0 # Timeout for network connectivity checks
