# this_file: src/virginia_clemm_poe/browser_manager.py
"""Simplified browser management using playwrightauthor.

This module provides a wrapper that uses playwrightauthor for browser setup
and connection, simplifying the browser management process.
"""

from playwright.async_api import Browser
from playwrightauthor import get_browser

from .config import DEFAULT_DEBUG_PORT
from .exceptions import BrowserManagerError


class BrowserManager:
    """Manages browser lifecycle using playwrightauthor.

    This class uses playwrightauthor for browser management, including
    installation, launch, and connection.
    """

    def __init__(self, debug_port: int = DEFAULT_DEBUG_PORT, verbose: bool = False):
        """Initialize the browser manager.

        Args:
            debug_port: Port for Chrome DevTools Protocol.
            verbose: Enable verbose logging.
        """
        self.debug_port = debug_port
        self.verbose = verbose
        self._browser: Browser | None = None

    async def get_browser(self) -> Browser:
        """
        Gets a browser instance using playwrightauthor.

        Returns:
            A connected browser instance.

        Raises:
            BrowserManagerError: If the browser fails to launch or connect.
        """
        if self._browser is None or not self._browser.is_connected():
            try:
                self._browser = await get_browser(
                    headless=True,
                    port=self.debug_port,
                    verbose=self.verbose
                )
            except Exception as e:
                raise BrowserManagerError(f"Failed to get browser: {e}") from e
        return self._browser

    @staticmethod
    async def setup_chrome() -> bool:
        """
        Ensures Chrome is installed using playwrightauthor.

        Returns:
            True if setup is successful.
        """
        try:
            from playwrightauthor.browser_manager import ensure_browser
            ensure_browser(verbose=True)
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """
        Closes the browser connection.
        """
        if self._browser and self._browser.is_connected():
            await self._browser.close()
        self._browser = None

    async def __aenter__(self) -> "BrowserManager":
        """Async context manager entry."""
        await self.get_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()