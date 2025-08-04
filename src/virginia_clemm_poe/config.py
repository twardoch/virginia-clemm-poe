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
DIALOG_WAIT_SECONDS = 1.0  # Wait time for modal dialog to appear
MODAL_CLOSE_WAIT_SECONDS = 0.5  # Wait time after closing modal

# Network configuration
API_TIMEOUT_SECONDS = 5.0  # Timeout for API health checks
NETWORK_TIMEOUT_SECONDS = 5.0  # Timeout for network connectivity checks
HTTP_REQUEST_TIMEOUT_SECONDS = 30.0  # Timeout for HTTP requests
HTTP_CONNECT_TIMEOUT_SECONDS = 10.0  # Timeout for HTTP connection establishment

# Browser timeout configuration
BROWSER_CONNECT_TIMEOUT_SECONDS = 30.0  # Timeout for browser connection
BROWSER_LAUNCH_TIMEOUT_SECONDS = 60.0  # Timeout for browser launch
PAGE_NAVIGATION_TIMEOUT_MS = 45_000  # Extended timeout for page navigation
PAGE_ELEMENT_TIMEOUT_MS = 15_000  # Timeout for finding page elements
BROWSER_OPERATION_TIMEOUT_SECONDS = 120.0  # Global timeout for browser operations

# Retry configuration
MAX_RETRIES = 3  # Maximum number of retries for failed operations
RETRY_DELAY_SECONDS = 2.0  # Base delay between retries
EXPONENTIAL_BACKOFF_MULTIPLIER = 2.0  # Multiplier for exponential backoff
