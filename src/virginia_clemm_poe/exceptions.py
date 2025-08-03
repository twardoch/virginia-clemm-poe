# this_file: src/virginia_clemm_poe/exceptions.py
"""Exception hierarchy for Virginia Clemm Poe.

This module defines custom exceptions following the PlaywrightAuthor
architecture pattern for better error handling and debugging.
"""


class VirginiaPoeError(Exception):
    """Base exception for all Virginia Clemm Poe errors.

    All custom exceptions in this package inherit from this base class,
    allowing for easy catching of all package-specific errors.
    """


class BrowserManagerError(VirginiaPoeError):
    """Exception raised for browser management related errors.

    This includes errors during Chrome detection, installation, launching,
    or connection to Chrome DevTools Protocol.
    """


class ChromeNotFoundError(BrowserManagerError):
    """Exception raised when Chrome executable cannot be found.

    This error occurs when no Chrome or Chromium installation is detected
    on the system and installation attempts have failed.
    """


class ChromeLaunchError(BrowserManagerError):
    """Exception raised when Chrome fails to launch properly.

    This can occur due to port conflicts, permission issues, or other
    system-specific problems preventing Chrome from starting.
    """


class CDPConnectionError(BrowserManagerError):
    """Exception raised when connection to Chrome DevTools Protocol fails.

    This indicates that Chrome is running but the CDP endpoint is not
    accessible or responding properly.
    """


class ModelDataError(VirginiaPoeError):
    """Exception raised for model data related errors.

    This includes errors during data loading, parsing, or validation
    of Poe model information.
    """


class ModelNotFoundError(ModelDataError):
    """Exception raised when a requested model cannot be found.

    This occurs when searching for a model by ID or name that doesn't
    exist in the current dataset.
    """


class DataUpdateError(ModelDataError):
    """Exception raised when model data update fails.

    This can occur during API calls, web scraping, or data persistence
    operations.
    """


class APIError(VirginiaPoeError):
    """Exception raised for Poe API related errors.

    This includes authentication failures, rate limiting, or other
    API-specific issues.
    """


class AuthenticationError(APIError):
    """Exception raised when Poe API authentication fails.

    This typically occurs when the API key is missing, invalid, or
    has been revoked.
    """


class RateLimitError(APIError):
    """Exception raised when Poe API rate limit is exceeded.

    This indicates that too many requests have been made in a given
    time period and the client should back off.
    """


class ScrapingError(VirginiaPoeError):
    """Exception raised during web scraping operations.

    This includes errors during pricing data extraction or other
    web-based data collection activities.
    """


class NetworkError(VirginiaPoeError):
    """Exception raised for network-related errors.

    This includes connection timeouts, DNS failures, or other
    network connectivity issues.
    """
