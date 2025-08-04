# this_file: src/virginia_clemm_poe/browser_manager.py
"""Simplified browser management using playwrightauthor.

This module provides a wrapper that uses playwrightauthor for browser setup
but directly uses playwright for the connection to avoid import issues.
Includes comprehensive timeout handling and graceful error recovery.
"""

import asyncio
from typing import Any

from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from .config import (
    BROWSER_CONNECT_TIMEOUT_SECONDS,
    BROWSER_LAUNCH_TIMEOUT_SECONDS,
    DEFAULT_DEBUG_PORT,
)
from .exceptions import BrowserManagerError, CDPConnectionError
from .utils.crash_recovery import (
    crash_recovery_handler,
    get_global_crash_recovery,
)
from .utils.timeout import (
    GracefulTimeout,
    retry_handler,
    timeout_handler,
    with_retries,
)


class BrowserManager:
    """Manages browser lifecycle using playwrightauthor for setup.

    This class uses playwrightauthor's browser management for Chrome setup
    but connects directly via playwright to avoid compatibility issues.
    """

    def __init__(self, debug_port: int = DEFAULT_DEBUG_PORT, verbose: bool = False):
        """Initialize the browser manager.

        Args:
            debug_port: Port for Chrome DevTools Protocol.
            verbose: Enable verbose logging.
        """
        self.debug_port = debug_port
        self.verbose = verbose
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    @timeout_handler(BROWSER_CONNECT_TIMEOUT_SECONDS, "browser_connection")
    @crash_recovery_handler("browser_connection", max_retries=5)
    async def connect(self) -> Browser:
        """Connect to browser using CDP with timeout and retry handling.

        Returns:
            Connected browser instance.

        Raises:
            CDPConnectionError: If connection fails after retries.
        """
        async def cleanup_on_failure() -> None:
            """Clean up resources on connection failure."""
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception:
                    pass
                finally:
                    self.playwright = None

        async with GracefulTimeout(
            BROWSER_CONNECT_TIMEOUT_SECONDS,
            "browser_connection",
            cleanup_on_failure,
        ):
            try:
                # Import and use playwrightauthor's ensure_browser for setup
                from playwrightauthor.browser_manager import ensure_browser

                # Ensure browser is running (this handles installation and launch)
                if self.verbose:
                    logger.info("Ensuring browser is available via playwrightauthor...")

                # Run browser setup with timeout
                await asyncio.to_thread(ensure_browser, verbose=self.verbose)

                # Connect via playwright CDP with timeout
                self.playwright = await async_playwright().start()
                
                # Add retry logic for CDP connection
                connection_url = f"http://localhost:{self.debug_port}"
                self.browser = await with_retries(
                    self.playwright.chromium.connect_over_cdp,
                    connection_url,
                    max_retries=3,
                    base_delay=1.0,
                    retryable_exceptions=(Exception,),
                    operation_name=f"CDP connection to {connection_url}",
                )

                # Get or create context with timeout
                if not self.browser.contexts:
                    self.context = await asyncio.wait_for(
                        self.browser.new_context(),
                        timeout=10.0
                    )
                else:
                    self.context = self.browser.contexts[0]

                if self.verbose:
                    logger.info(f"Successfully connected to browser on port {self.debug_port}")

                return self.browser

            except asyncio.TimeoutError as e:
                await cleanup_on_failure()
                raise CDPConnectionError(
                    f"Browser connection timed out after {BROWSER_CONNECT_TIMEOUT_SECONDS}s"
                ) from e
            except Exception as e:
                await cleanup_on_failure()
                raise CDPConnectionError(f"Failed to connect to browser: {e}") from e

    @timeout_handler(10.0, "new_page_creation")
    async def new_page(self) -> Page:
        """Create a new page with timeout handling.

        Returns:
            New page instance.

        Raises:
            BrowserManagerError: If browser not connected or page creation fails.
        """
        if not self.context:
            raise BrowserManagerError("Browser not connected")

        try:
            page = await self.context.new_page()
            
            # Set default timeouts for the page
            page.set_default_timeout(30000)  # 30 seconds for most operations
            page.set_default_navigation_timeout(45000)  # 45 seconds for navigation
            
            return page
        except Exception as e:
            raise BrowserManagerError(f"Failed to create new page: {e}") from e

    @timeout_handler(15.0, "browser_cleanup")
    async def close(self) -> None:
        """Close browser connection and clean up resources with timeout."""
        if self.playwright:
            try:
                logger.debug("Closing browser connection...")
                await self.playwright.stop()
                logger.debug("Browser connection closed successfully")
            except Exception as e:
                logger.warning(f"Error during browser cleanup: {e}")
            finally:
                self.playwright = None
                self.browser = None
                self.context = None

    async def __aenter__(self) -> "BrowserManager":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
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
