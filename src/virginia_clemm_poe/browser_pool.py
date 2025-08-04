# this_file: src/virginia_clemm_poe/browser_pool.py
"""Browser connection pool for efficient resource management.

This module provides a connection pool that maintains reusable browser
instances to avoid the overhead of repeatedly launching and closing browsers.
It significantly improves performance for bulk operations with comprehensive
timeout handling and graceful error recovery.
"""

import asyncio
import time
from collections import deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page

from .browser_manager import BrowserManager
from .config import (
    BROWSER_OPERATION_TIMEOUT_SECONDS,
    DEFAULT_DEBUG_PORT,
    PAGE_ELEMENT_TIMEOUT_MS,
)
from .exceptions import BrowserManagerError
from .utils.logger import log_performance_metric
from .utils.crash_recovery import (
    CrashDetector,
    get_global_crash_recovery,
)
from .utils.memory import (
    MemoryManagedOperation,
    get_global_memory_monitor,
)
from .utils.timeout import (
    GracefulTimeout,
    timeout_handler,
    with_timeout,
)


class BrowserConnection:
    """Represents a pooled browser connection with usage tracking."""

    def __init__(self, browser: Browser, context: BrowserContext, manager: BrowserManager):
        """Initialize a browser connection.

        Args:
            browser: The browser instance
            context: The browser context
            manager: The browser manager that created this connection
        """
        self.browser = browser
        self.context = context
        self.manager = manager
        self.created_at = time.time()
        self.last_used = time.time()
        self.use_count = 0
        self.is_healthy = True

    def mark_used(self) -> None:
        """Mark this connection as recently used."""
        self.last_used = time.time()
        self.use_count += 1

    def age_seconds(self) -> float:
        """Get the age of this connection in seconds."""
        return time.time() - self.created_at

    def idle_seconds(self) -> float:
        """Get the time since this connection was last used."""
        return time.time() - self.last_used

    async def health_check(self) -> bool:
        """Check if the connection is still healthy using multi-layer validation with crash detection.
        
        This method performs a comprehensive health assessment of the browser connection
        by attempting a lightweight page creation operation. It implements sophisticated
        error detection and classification to distinguish between different failure modes.
        
        Health check workflow:
        1. Creates a new page within the existing browser context (5s timeout)
        2. Immediately closes the page to avoid resource leaks
        3. Analyzes any failures using CrashDetector for error classification
        4. Updates internal health status and logs appropriate messages
        
        Error classification and handling:
        - BROWSER_CRASHED: Browser process died or became unresponsive  
        - CONNECTION_LOST: Network/IPC connection to browser failed
        - TIMEOUT: Operation took longer than 5 seconds (indicates resource issues)
        - GENERIC_ERROR: Other failures that don't indicate browser health issues
        
        Returns:
            True if connection is healthy (page creation succeeded), False otherwise
            
        Side effects:
            - Updates self.is_healthy flag based on test result
            - Logs debug messages for all outcomes
            - Logs warnings for critical crash types (browser/connection failures)
            
        Example usage:
            >>> connection = BrowserConnection(browser, context, manager)  
            >>> if await connection.health_check():
            ...     # Safe to use this connection
            ...     page = await connection.context.new_page()
            >>> else:
            ...     # Connection is unhealthy, should be discarded
            
        Note:
            This is a destructive test that may reveal browser instability.
            Failed health checks should result in connection removal from pool.
        """
        try:
            # Try to create a new page as a health check with timeout
            async with GracefulTimeout(5.0, f"health_check_connection_{id(self)}"):
                page = await self.context.new_page()
                await page.close()
            
            self.is_healthy = True
            logger.debug(f"Connection {id(self)} passed health check")
            return True
        except Exception as e:
            self.is_healthy = False
            
            # Detect crash type for better logging
            crash_type = CrashDetector.detect_crash_type(e, "health_check")
            logger.debug(f"Connection {id(self)} failed health check ({crash_type.value}): {e}")
            
            # If it's a critical crash, log it as a warning
            if crash_type in [crash_type.BROWSER_CRASHED, crash_type.CONNECTION_LOST]:
                logger.warning(f"Connection {id(self)} appears to have crashed: {e}")
            
            return False

    async def close(self) -> None:
        """Close this connection and clean up resources."""
        try:
            await self.manager.close()
        except Exception as e:
            logger.warning(f"Error closing browser connection: {e}")


class BrowserPool:
    """Connection pool for browser instances.

    Maintains a pool of reusable browser connections to improve performance
    for bulk operations. Connections are reused when possible and automatically
    cleaned up when they become stale or unhealthy.
    """

    def __init__(
        self,
        max_size: int = 3,
        max_age_seconds: int = 300,  # 5 minutes
        max_idle_seconds: int = 60,  # 1 minute
        debug_port: int = DEFAULT_DEBUG_PORT,
        verbose: bool = False,
    ):
        """Initialize the browser pool.

        Args:
            max_size: Maximum number of connections to maintain
            max_age_seconds: Maximum age of a connection before replacement
            max_idle_seconds: Maximum idle time before connection is closed
            debug_port: Port for Chrome DevTools Protocol
            verbose: Enable verbose logging
        """
        self.max_size = max_size
        self.max_age_seconds = max_age_seconds
        self.max_idle_seconds = max_idle_seconds
        self.debug_port = debug_port
        self.verbose = verbose

        self._pool: deque[BrowserConnection] = deque()
        self._active_connections: set[BrowserConnection] = set()
        self._lock = asyncio.Lock()
        self._closed = False
        self._cleanup_task: asyncio.Task[None] | None = None
        self._memory_monitor = get_global_memory_monitor()
        self._crash_recovery = get_global_crash_recovery()
        self._connections_created = 0
        self._connection_failures = 0

    async def start(self) -> None:
        """Start the pool and its cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info(f"Browser pool started with max_size={self.max_size}")

    async def stop(self) -> None:
        """Stop the pool and close all connections."""
        self._closed = True

        if self._cleanup_task:
            self._cleanup_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._cleanup_task

        # Close all connections
        async with self._lock:
            all_connections = list(self._pool) + list(self._active_connections)
            self._pool.clear()
            self._active_connections.clear()

        close_tasks = [conn.close() for conn in all_connections]
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

        logger.info("Browser pool stopped")

    async def _cleanup_loop(self) -> None:
        """Background task that cleans up stale connections and manages memory."""
        while not self._closed:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Clean up stale connections
                await self._cleanup_stale_connections()
                
                # Check memory usage and run cleanup if needed
                memory_status = self._memory_monitor.check_memory_usage()
                if memory_status["above_warning"]:
                    logger.info(f"Memory usage {memory_status['current_mb']:.1f}MB above warning threshold, running cleanup")
                    await self._memory_monitor.cleanup_memory()
                    
                # Log memory status periodically
                if self._connections_created % 10 == 0:  # Every 10th connection
                    self._memory_monitor.log_memory_status("browser_pool_cleanup_loop")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_stale_connections(self) -> None:
        """Remove stale or unhealthy connections from the pool."""
        async with self._lock:
            to_remove = []

            for conn in self._pool:
                # Check if connection is too old or idle too long
                if conn.age_seconds() > self.max_age_seconds or conn.idle_seconds() > self.max_idle_seconds:
                    to_remove.append(conn)
                    continue

                # Check health
                if not await conn.health_check():
                    to_remove.append(conn)

            # Remove stale connections
            for conn in to_remove:
                self._pool.remove(conn)
                asyncio.create_task(conn.close())

            if to_remove:
                logger.debug(f"Cleaned up {len(to_remove)} stale connections")

    async def _create_connection(self) -> BrowserConnection:
        """Create a new browser connection with memory monitoring and crash recovery.

        Returns:
            New browser connection

        Raises:
            BrowserManagerError: If connection creation fails after recovery attempts
        """
        async def _do_create_connection() -> BrowserConnection:
            """Internal function to create connection with recovery."""
            async with MemoryManagedOperation(f"create_browser_connection_{self._connections_created}"):
                start_time = time.time()
                self._connections_created += 1

                manager = BrowserManager(debug_port=self.debug_port, verbose=self.verbose)
                try:
                    browser = await manager.get_browser()
                    context = browser.contexts[0] if browser.contexts else await browser.new_context()

                    if not context:
                        raise BrowserManagerError("No browser context available")

                    connection = BrowserConnection(browser, context, manager)

                    # Log performance metric
                    creation_time = time.time() - start_time
                    log_performance_metric(
                        "browser_connection_created", 
                        creation_time, 
                        "seconds", 
                        {
                            "pool_size": len(self._pool),
                            "connections_created": self._connections_created,
                            "connection_failures": self._connection_failures,
                            "memory_mb": self._memory_monitor.get_memory_usage_mb(),
                        }
                    )

                    logger.debug(f"Created new browser connection #{self._connections_created} in {creation_time:.2f}s")
                    
                    # Increment operation count for memory monitoring
                    self._memory_monitor.increment_operation_count()
                    
                    return connection

                except Exception as e:
                    self._connection_failures += 1
                    await manager.close()
                    
                    # Detect crash type and log appropriately
                    crash_type = CrashDetector.detect_crash_type(e, "create_connection")
                    logger.warning(f"Browser connection creation failed ({crash_type.value}): {e}")
                    
                    raise BrowserManagerError(f"Failed to create browser connection: {e}") from e

        async def cleanup_on_failure() -> None:
            """Cleanup function for crash recovery."""
            logger.debug("Running cleanup after connection creation failure")
            # Force memory cleanup on repeated failures
            if self._connection_failures > 2:
                await self._memory_monitor.cleanup_memory(force=True)

        try:
            return await self._crash_recovery.recover_with_backoff(
                _do_create_connection,
                "browser_connection_creation",
                cleanup_on_failure
            )
        except Exception as e:
            logger.error(f"Failed to create browser connection after recovery attempts: {e}")
            raise

    async def _get_connection_from_pool(self) -> tuple[BrowserConnection | None, bool]:
        """Try to get a connection from the pool.
        
        Returns:
            Tuple of (connection, acquired_from_pool)
        """
        async with self._lock:
            if self._pool:
                connection = self._pool.popleft()
                self._active_connections.add(connection)
                logger.debug(f"Acquired connection from pool (pool_size={len(self._pool)})")
                return connection, True
        return None, False
    
    async def _ensure_connection(self, connection: BrowserConnection | None) -> BrowserConnection:
        """Ensure we have a connection, creating one if needed.
        
        Args:
            connection: Existing connection or None
            
        Returns:
            Valid connection
            
        Raises:
            BrowserManagerError: If pool is exhausted
        """
        if connection:
            return connection
            
        # Check pool capacity
        if len(self._active_connections) >= self.max_size:
            raise BrowserManagerError(f"Pool exhausted: {len(self._active_connections)} active connections")

        # Create new connection
        connection = await with_timeout(
            self._create_connection(),
            30.0,
            "new_connection_creation"
        )
        
        async with self._lock:
            self._active_connections.add(connection)
            
        return connection
    
    async def _create_page_from_connection(self, connection: BrowserConnection) -> Page:
        """Create a new page from a connection with proper timeouts.
        
        Args:
            connection: Browser connection to use
            
        Returns:
            Configured page instance
        """
        connection.mark_used()
        
        # Create page with timeout
        page = await with_timeout(
            connection.context.new_page(),
            15.0,
            "new_page_creation"
        )

        # Set timeouts on the page
        page.set_default_timeout(PAGE_ELEMENT_TIMEOUT_MS)
        page.set_default_navigation_timeout(45000)  # 45 seconds for navigation
        
        return page
    
    async def _close_page_safely(self, page: Page | None) -> None:
        """Safely close a page with timeout.
        
        Args:
            page: Page to close, may be None
        """
        if page:
            try:
                await with_timeout(page.close(), 10.0, "page_close")
            except Exception as e:
                logger.warning(f"Error closing page: {e}")
    
    async def _return_or_close_connection(self, connection: BrowserConnection | None) -> None:
        """Return connection to pool if healthy, otherwise close it.
        
        Args:
            connection: Connection to return or close
        """
        if not connection:
            return
            
        async with self._lock:
            self._active_connections.discard(connection)

            # Check if connection is still healthy and young enough
            if (not self._closed and 
                connection.is_healthy and 
                connection.age_seconds() < self.max_age_seconds):
                self._pool.append(connection)
                logger.debug(f"Returned connection to pool (pool_size={len(self._pool)})")
            else:
                # Close unhealthy or old connection
                asyncio.create_task(connection.close())
                logger.debug("Closed connection instead of returning to pool")

    @asynccontextmanager
    async def acquire_page(self) -> AsyncIterator[Page]:
        """Acquire a page from the pool with comprehensive timeout handling.

        This context manager handles getting a connection from the pool,
        creating a new page, and returning the connection to the pool.
        All operations are protected by timeouts to prevent hanging.

        Yields:
            A new page instance

        Raises:
            BrowserManagerError: If no connection is available or timeout occurs

        Example:
            ```python
            pool = BrowserPool()
            await pool.start()

            async with pool.acquire_page() as page:
                await page.goto("https://example.com")
                # Use the page...
            # Page is automatically closed and connection returned to pool
            ```
        """
        if self._closed:
            raise BrowserManagerError("Browser pool is closed")

        connection: BrowserConnection | None = None
        page: Page | None = None
        acquired_from_pool = False

        async def cleanup_resources() -> None:
            """Clean up resources on failure."""
            nonlocal page, connection
            
            # Clean up page
            if page:
                try:
                    await with_timeout(page.close(), 5.0, "page_cleanup")
                except Exception as e:
                    logger.warning(f"Error closing page during cleanup: {e}")

            # Return or close connection
            if connection:
                async with self._lock:
                    self._active_connections.discard(connection)

                # Close connection on failure instead of returning to pool
                try:
                    await with_timeout(connection.close(), 10.0, "connection_cleanup")
                except Exception as e:
                    logger.warning(f"Error closing connection during cleanup: {e}")

        try:
            # Use timeout for the entire page acquisition process
            async with GracefulTimeout(
                BROWSER_OPERATION_TIMEOUT_SECONDS,
                "browser_pool_page_acquisition",
                cleanup_resources,
            ):
                # Get or create connection
                connection, acquired_from_pool = await self._get_connection_from_pool()
                connection = await self._ensure_connection(connection)
                
                # Create page from connection
                page = await self._create_page_from_connection(connection)

                # Log performance metric
                log_performance_metric(
                    "browser_pool_acquisition",
                    1,
                    "count",
                    {
                        "from_pool": acquired_from_pool,
                        "pool_size": len(self._pool),
                        "active_connections": len(self._active_connections),
                    },
                )

                yield page

        finally:
            # Clean up page
            await self._close_page_safely(page)
            
            # Return connection to pool or close it
            await self._return_or_close_connection(connection)

    async def get_stats(self) -> dict[str, Any]:
        """Get pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        async with self._lock:
            pool_connections = list(self._pool)
            active_connections = list(self._active_connections)

        stats = {
            "pool_size": len(pool_connections),
            "active_connections": len(active_connections),
            "total_connections": len(pool_connections) + len(active_connections),
            "max_size": self.max_size,
            "closed": self._closed,
            "connections_created": self._connections_created,
            "connection_failures": self._connection_failures,
            "memory_usage_mb": self._memory_monitor.get_memory_usage_mb(),
            "crash_recovery_stats": self._crash_recovery.get_crash_stats(),
            "pool_connections": [
                {
                    "age_seconds": conn.age_seconds(),
                    "idle_seconds": conn.idle_seconds(),
                    "use_count": conn.use_count,
                    "is_healthy": conn.is_healthy,
                }
                for conn in pool_connections
            ],
            "active_connection_details": [
                {"age_seconds": conn.age_seconds(), "use_count": conn.use_count, "is_healthy": conn.is_healthy}
                for conn in active_connections
            ],
        }

        return stats


# Global pool instance
_global_pool: BrowserPool | None = None


async def get_global_pool(
    max_size: int = 3, debug_port: int = DEFAULT_DEBUG_PORT, verbose: bool = False
) -> BrowserPool:
    """Get or create the global browser pool.

    Args:
        max_size: Maximum pool size
        debug_port: Chrome DevTools port
        verbose: Enable verbose logging

    Returns:
        The global browser pool instance
    """
    global _global_pool

    if _global_pool is None or _global_pool._closed:
        _global_pool = BrowserPool(max_size=max_size, debug_port=debug_port, verbose=verbose)
        await _global_pool.start()

    return _global_pool


async def close_global_pool() -> None:
    """Close the global browser pool."""
    global _global_pool

    if _global_pool is not None:
        await _global_pool.stop()
        _global_pool = None

