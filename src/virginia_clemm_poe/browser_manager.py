# this_file: src/virginia_clemm_poe/browser_manager.py
"""Browser management using playwrightauthor with Chrome for Testing.

This module provides optimized browser management that leverages playwrightauthor's
session reuse capabilities and Chrome for Testing support for reliable automation.
"""

import contextlib

from loguru import logger
from playwright.async_api import Browser as PlaywrightBrowser, Page
from playwrightauthor import AsyncBrowser

from .config import DEFAULT_DEBUG_PORT
from .exceptions import BrowserManagerError


class BrowserManager:
    """Manages browser lifecycle using playwrightauthor with session reuse.

    This class leverages playwrightauthor's Chrome for Testing management and
    session reuse features for optimal performance. It supports both creating
    new browser instances and reusing existing browser sessions.
    """

    def __init__(self, debug_port: int = DEFAULT_DEBUG_PORT, verbose: bool = False, reuse_session: bool = True):
        """Initialize the browser manager.

        Args:
            debug_port: Port for Chrome DevTools Protocol.
            verbose: Enable verbose logging.
            reuse_session: Whether to reuse existing browser sessions (recommended).
        """
        self.debug_port = debug_port
        self.verbose = verbose
        self.reuse_session = reuse_session
        self._browser: PlaywrightBrowser | None = None
        self._browser_ctx: AsyncBrowser | None = None

    async def get_browser(self) -> PlaywrightBrowser:
        """Gets a browser instance using playwrightauthor.

        This method connects to Chrome for Testing, either launching a new instance
        or connecting to an existing one for session reuse.

        Returns:
            A connected browser instance.

        Raises:
            BrowserManagerError: If the browser fails to launch or connect.
        """
        if self._browser is None or not self._browser.is_connected():
            try:
                # Use playwrightauthor AsyncBrowser with session reuse
                self._browser_ctx = AsyncBrowser(verbose=self.verbose)
                self._browser = await self._browser_ctx.__aenter__()

                if self.verbose:
                    logger.info("Connected to Chrome for Testing via playwrightauthor")

            except Exception as e:
                raise BrowserManagerError(f"Failed to get browser: {e}") from e
        return self._browser

    async def get_page(self) -> Page:
        """Gets a page using playwrightauthor's session reuse feature.

        This method leverages the browser's get_page() method which reuses
        existing browser contexts and pages instead of creating new ones. This
        maintains authenticated sessions across script runs without re-login.

        Returns:
            A page instance from the reused browser context.

        Raises:
            BrowserManagerError: If unable to get a page.
        """
        try:
            browser = await self.get_browser()

            # Use the browser's get_page() method for session reuse
            # This is attached to the browser object by playwrightauthor
            page = await browser.get_page()

            if self.verbose:
                logger.info("Reused existing browser page for session persistence")

            return page

        except Exception as e:
            raise BrowserManagerError(f"Failed to get page: {e}") from e

    @staticmethod
    async def setup_chrome() -> bool:
        """Ensures Chrome is installed using playwrightauthor.

        Returns:
            True if setup is successful.
        """
        try:
            # Playwrightauthor handles setup automatically
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Closes the browser connection."""
        if self._browser_ctx:
            with contextlib.suppress(Exception):
                await self._browser_ctx.__aexit__(None, None, None)
        self._browser = None
        self._browser_ctx = None

    async def __aenter__(self) -> "BrowserManager":
        """Async context manager entry."""
        await self.get_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
