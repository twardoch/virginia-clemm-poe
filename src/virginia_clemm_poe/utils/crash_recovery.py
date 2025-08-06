# this_file: src/virginia_clemm_poe/utils/crash_recovery.py
"""Browser crash recovery utilities for Virginia Clemm Poe.

This module provides utilities for detecting and recovering from browser crashes
with exponential backoff and automatic retry mechanisms. It ensures resilient
operation even when browser instances become unresponsive or crash.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, TypeVar

from loguru import logger
from playwright.async_api import Error as PlaywrightError

from ..config import (
    EXPONENTIAL_BACKOFF_MULTIPLIER,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
)
from ..exceptions import BrowserManagerError, CDPConnectionError
from ..utils.logger import log_performance_metric

T = TypeVar("T")


class CrashType(Enum):
    """Types of browser crashes and failures."""

    CONNECTION_LOST = "connection_lost"  # Browser connection dropped
    BROWSER_CRASHED = "browser_crashed"  # Browser process crashed
    PAGE_UNRESPONSIVE = "page_unresponsive"  # Page not responding
    CONTEXT_INVALID = "context_invalid"  # Browser context invalid
    TIMEOUT_ERROR = "timeout_error"  # Operation timed out
    NETWORK_ERROR = "network_error"  # Network connectivity issues
    UNKNOWN_ERROR = "unknown_error"  # Other unidentified errors


class CrashInfo:
    """Information about a browser crash or failure."""

    def __init__(
        self, crash_type: CrashType, error: Exception, operation: str, attempt: int = 1, timestamp: float | None = None
    ):
        """Initialize crash information.

        Args:
            crash_type: Type of crash that occurred
            error: The original exception
            operation: Name of the operation that failed
            attempt: Which attempt this was (1-indexed)
            timestamp: When the crash occurred (defaults to now)
        """
        self.crash_type = crash_type
        self.error = error
        self.operation = operation
        self.attempt = attempt
        self.timestamp = timestamp or time.time()

    def __str__(self) -> str:
        """String representation of the crash."""
        return f"{self.crash_type.value} during {self.operation} (attempt {self.attempt}): {self.error}"


class CrashDetector:
    """Detects different types of browser crashes from exceptions."""

    @staticmethod
    def detect_crash_type(error: Exception, operation: str = "unknown") -> CrashType:
        """Detect the type of crash from an exception.

        Args:
            error: The exception that occurred
            operation: The operation that was being performed

        Returns:
            The detected crash type
        """
        error_msg = str(error).lower()

        # Check for specific Playwright errors
        if isinstance(error, PlaywrightError):
            if "target closed" in error_msg or "connection closed" in error_msg:
                return CrashType.CONNECTION_LOST
            if "browser has been closed" in error_msg:
                return CrashType.BROWSER_CRASHED
            if "context has been closed" in error_msg:
                return CrashType.CONTEXT_INVALID
            if "timeout" in error_msg:
                return CrashType.TIMEOUT_ERROR
            if "navigation" in error_msg and "timeout" in error_msg:
                return CrashType.PAGE_UNRESPONSIVE

        # Check for connection-related errors
        if isinstance(error, CDPConnectionError | ConnectionError):
            return CrashType.CONNECTION_LOST

        # Check for timeout errors
        if isinstance(error, asyncio.TimeoutError | TimeoutError):
            return CrashType.TIMEOUT_ERROR

        # Check for browser manager errors
        if isinstance(error, BrowserManagerError):
            if "connection" in error_msg:
                return CrashType.CONNECTION_LOST
            if "context" in error_msg:
                return CrashType.CONTEXT_INVALID

        # Check for network-related errors
        if any(keyword in error_msg for keyword in ["network", "dns", "connection refused", "connect"]):
            return CrashType.NETWORK_ERROR

        return CrashType.UNKNOWN_ERROR

    @staticmethod
    def is_recoverable(crash_type: CrashType) -> bool:
        """Check if a crash type is recoverable.

        Args:
            crash_type: The type of crash

        Returns:
            True if the crash is recoverable with retry
        """
        recoverable_types = {
            CrashType.CONNECTION_LOST,
            CrashType.BROWSER_CRASHED,
            CrashType.PAGE_UNRESPONSIVE,
            CrashType.CONTEXT_INVALID,
            CrashType.TIMEOUT_ERROR,
            CrashType.NETWORK_ERROR,
        }
        return crash_type in recoverable_types


class CrashRecovery:
    """Manages crash recovery with exponential backoff."""

    def __init__(
        self,
        max_retries: int = MAX_RETRIES,
        base_delay: float = RETRY_DELAY_SECONDS,
        backoff_multiplier: float = EXPONENTIAL_BACKOFF_MULTIPLIER,
        max_delay: float = 60.0,
    ):
        """Initialize crash recovery manager.

        Args:
            max_retries: Maximum number of recovery attempts
            base_delay: Base delay between retries in seconds
            backoff_multiplier: Multiplier for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self.crash_history: list[CrashInfo] = []

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt with exponential backoff.

        Args:
            attempt: The attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.backoff_multiplier**attempt)
        return min(delay, self.max_delay)

    def record_crash(self, crash_info: CrashInfo) -> None:
        """Record a crash in the history.

        Args:
            crash_info: Information about the crash
        """
        self.crash_history.append(crash_info)

        # Keep only the last 100 crashes to prevent memory growth
        if len(self.crash_history) > 100:
            self.crash_history = self.crash_history[-100:]

        logger.warning(f"Recorded crash: {crash_info}")

        # Log performance metric
        log_performance_metric(
            "browser_crash",
            1,
            "count",
            {
                "crash_type": crash_info.crash_type.value,
                "operation": crash_info.operation,
                "attempt": crash_info.attempt,
            },
        )

    async def _execute_attempt(
        self, func: Callable[..., Awaitable[T]], attempt: int, operation_name: str, *args: Any, **kwargs: Any
    ) -> T:
        """Execute a single attempt of the function.

        Args:
            func: Function to execute
            attempt: Current attempt number (0-indexed)
            operation_name: Name of the operation
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        if attempt > 0:
            delay = self.get_delay(attempt - 1)
            logger.info(f"Attempting recovery for {operation_name} (attempt {attempt + 1}) after {delay:.1f}s delay")
            await asyncio.sleep(delay)

        result = await func(*args, **kwargs)

        if attempt > 0:
            logger.info(f"Successfully recovered {operation_name} on attempt {attempt + 1}")
            log_performance_metric("browser_recovery_success", attempt + 1, "attempts", {"operation": operation_name})

        return result

    def _handle_crash(self, exception: Exception, operation_name: str, attempt: int) -> CrashInfo:
        """Handle and record a crash.

        Args:
            exception: The exception that occurred
            operation_name: Name of the operation
            attempt: Current attempt number (0-indexed)

        Returns:
            CrashInfo object

        Raises:
            Exception: If crash is not recoverable
        """
        crash_type = CrashDetector.detect_crash_type(exception, operation_name)
        crash_info = CrashInfo(crash_type, exception, operation_name, attempt + 1)
        self.record_crash(crash_info)

        # Check if this type of crash is recoverable
        if not CrashDetector.is_recoverable(crash_type):
            logger.error(f"Non-recoverable crash in {operation_name}: {crash_info}")
            raise exception

        return crash_info

    async def _run_cleanup(self, cleanup_func: Callable[[], Awaitable[None]] | None, operation_name: str) -> None:
        """Run cleanup function if provided.

        Args:
            cleanup_func: Optional cleanup function
            operation_name: Name of the operation for logging
        """
        if cleanup_func:
            try:
                await cleanup_func()
                logger.debug(f"Cleanup completed for {operation_name}")
            except Exception as cleanup_error:
                logger.warning(f"Cleanup failed for {operation_name}: {cleanup_error}")

    def _log_retry_attempt(self, crash_info: CrashInfo, attempt: int, operation_name: str) -> None:
        """Log retry attempt with delay information.

        Args:
            crash_info: Information about the crash
            attempt: Current attempt number (0-indexed)
            operation_name: Name of the operation
        """
        if attempt < self.max_retries:
            delay = self.get_delay(attempt)
            logger.warning(
                f"Recoverable crash in {operation_name} (attempt {attempt + 1}): {crash_info}. "
                f"Will retry in {delay:.1f}s"
            )
        else:
            logger.error(f"All recovery attempts failed for {operation_name}: {crash_info}")

    async def recover_with_backoff(
        self,
        func: Callable[..., Awaitable[T]],
        operation_name: str,
        cleanup_func: Callable[[], Awaitable[None]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Recover from crashes with exponential backoff.

        Args:
            func: The async function to execute with recovery
            operation_name: Name of the operation for logging
            cleanup_func: Optional cleanup function to call on crash
            *args: Arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            Result of the function

        Raises:
            The last exception if all recovery attempts fail
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return await self._execute_attempt(func, attempt, operation_name, *args, **kwargs)

            except Exception as e:
                last_exception = e
                crash_info = self._handle_crash(e, operation_name, attempt)

                # Run cleanup
                await self._run_cleanup(cleanup_func, operation_name)

                # Log retry attempt
                self._log_retry_attempt(crash_info, attempt, operation_name)

        # If we get here, all attempts failed
        if last_exception:
            log_performance_metric(
                "browser_recovery_failure", self.max_retries + 1, "attempts", {"operation": operation_name}
            )
            raise last_exception

        raise RuntimeError(f"Recovery failed for {operation_name} with unknown error")

    def get_crash_stats(self) -> dict[str, Any]:
        """Get statistics about crashes and recovery.

        Returns:
            Dictionary with crash statistics
        """
        if not self.crash_history:
            return {"total_crashes": 0}

        # Count crashes by type
        crash_counts = {}
        for crash in self.crash_history:
            crash_type = crash.crash_type.value
            crash_counts[crash_type] = crash_counts.get(crash_type, 0) + 1

        # Recent crashes (last hour)
        recent_threshold = time.time() - 3600  # 1 hour ago
        recent_crashes = [c for c in self.crash_history if c.timestamp > recent_threshold]

        return {
            "total_crashes": len(self.crash_history),
            "recent_crashes": len(recent_crashes),
            "crash_types": crash_counts,
            "last_crash": str(self.crash_history[-1]) if self.crash_history else None,
        }


def crash_recovery_handler(
    operation_name: str | None = None,
    max_retries: int = MAX_RETRIES,
    cleanup_func: Callable[[], Awaitable[None]] | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator to add crash recovery to async functions.

    Args:
        operation_name: Name of the operation (defaults to function name)
        max_retries: Maximum number of recovery attempts
        cleanup_func: Optional cleanup function to call on crash

    Returns:
        Decorated function with crash recovery

    Example:
        ```python
        @crash_recovery_handler("browser_operation", max_retries=5)
        async def risky_browser_operation():
            # This will automatically retry up to 5 times on crashes
            return await some_browser_operation()
        ```
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        recovery_manager = CrashRecovery(max_retries=max_retries)

        async def wrapper(*args: Any, **kwargs: Any) -> T:
            op_name = operation_name or func.__name__
            return await recovery_manager.recover_with_backoff(func, op_name, cleanup_func, *args, **kwargs)

        return wrapper

    return decorator


# Global crash recovery manager
_global_recovery_manager: CrashRecovery | None = None


def get_global_crash_recovery() -> CrashRecovery:
    """Get or create the global crash recovery manager.

    Returns:
        The global crash recovery manager instance
    """
    global _global_recovery_manager

    if _global_recovery_manager is None:
        _global_recovery_manager = CrashRecovery()

    return _global_recovery_manager
