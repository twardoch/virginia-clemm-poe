# this_file: src/virginia_clemm_poe/browser_manager.py
"""Simplified browser management using playwrightauthor.

This module provides a wrapper that uses playwrightauthor for browser setup
but directly uses playwright for the connection to avoid import issues.
"""

from loguru import logger
from playwright.async_api import Browser, Page, async_playwright

from .exceptions import BrowserManagerError, CDPConnectionError


class BrowserManager:
    """Manages browser lifecycle using playwrightauthor for setup.

    This class uses playwrightauthor's browser management for Chrome setup
    but connects directly via playwright to avoid compatibility issues.
    """

    def __init__(self, debug_port: int = 9222, verbose: bool = False):
        """Initialize the browser manager.

        Args:
            debug_port: Port for Chrome DevTools Protocol.
            verbose: Enable verbose logging.
        """
        self.debug_port = debug_port
        self.verbose = verbose
        self.playwright = None
        self.browser = None
        self.context = None

    async def connect(self) -> Browser:
        """Connect to browser using CDP.

        Returns:
            Connected browser instance.

        Raises:
            CDPConnectionError: If connection fails.
        """
        try:
            # Import and use playwrightauthor's ensure_browser for setup
            from playwrightauthor.browser_manager import ensure_browser

            # Ensure browser is running (this handles installation and launch)
            if self.verbose:
                logger.info("Ensuring browser is available via playwrightauthor...")

            ensure_browser(verbose=self.verbose)

            # Connect via playwright CDP
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.connect_over_cdp(f"http://localhost:{self.debug_port}")

            # Get or create context
            if not self.browser.contexts:
                self.context = await self.browser.new_context()
            else:
                self.context = self.browser.contexts[0]

            if self.verbose:
                logger.info("Successfully connected to browser")

            return self.browser

        except Exception as e:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            raise CDPConnectionError(f"Failed to connect to browser: {e}") from e

    async def new_page(self) -> Page:
        """Create a new page.

        Returns:
            New page instance.

        Raises:
            BrowserManagerError: If browser not connected.
        """
        if not self.context:
            raise BrowserManagerError("Browser not connected")

        return await self.context.new_page()

    async def close(self) -> None:
        """Close browser connection and clean up resources."""
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
            finally:
                self.playwright = None
                self.browser = None
                self.context = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    @staticmethod
    async def setup_chrome() -> bool:
        """Setup Chrome for the system.

        Uses playwrightauthor's browser setup functionality.

        Returns:
            True if setup succeeded.
        """
        try:
            from playwrightauthor.browser_manager import ensure_browser

            ensure_browser()
            return True
        except Exception:
            return False
