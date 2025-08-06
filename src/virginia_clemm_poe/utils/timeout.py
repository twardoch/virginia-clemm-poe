# this_file: src/virginia_clemm_poe/utils/timeout.py
"""Timeout and retry utilities for Virginia Clemm Poe.

This module provides utilities for handling timeouts, retries, and graceful
degradation of operations. It ensures no operations hang indefinitely and
provides proper error handling with exponential backoff.
"""

import asyncio
import functools
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from loguru import logger

from ..config import (
    EXPONENTIAL_BACKOFF_MULTIPLIER,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
)
from ..exceptions import BrowserManagerError, NetworkError

T = TypeVar("T")


class TimeoutError(Exception):
    """Custom timeout error with context information."""

    def __init__(self, message: str, timeout_seconds: float, operation: str):
        """Initialize timeout error.

        Args:
            message: Error message
            timeout_seconds: The timeout value that was exceeded
            operation: Description of the operation that timed out
        """
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


async def with_timeout[T](
    awaitable: Awaitable[T],
    timeout_seconds: float,
    operation_name: str = "operation",
) -> T:
    """Execute an awaitable with a timeout.

    Args:
        awaitable: The awaitable to execute
        timeout_seconds: Timeout in seconds
        operation_name: Name of the operation for error reporting

    Returns:
        The result of the awaitable

    Raises:
        TimeoutError: If the operation times out
    """
    try:
        return await asyncio.wait_for(awaitable, timeout=timeout_seconds)
    except TimeoutError as e:
        error_msg = f"{operation_name} timed out after {timeout_seconds} seconds"
        logger.error(error_msg)
        raise TimeoutError(error_msg, timeout_seconds, operation_name) from e


async def with_retries[T](
    func: Callable[..., Awaitable[T]],
    *args: Any,
    max_retries: int = MAX_RETRIES,
    base_delay: float = RETRY_DELAY_SECONDS,
    backoff_multiplier: float = EXPONENTIAL_BACKOFF_MULTIPLIER,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    operation_name: str = "operation",
    **kwargs: Any,
) -> T:
    """Execute a function with retries and exponential backoff.

    Args:
        func: The async function to execute
        *args: Arguments to pass to the function
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
        retryable_exceptions: Tuple of exception types that should trigger a retry
        operation_name: Name of the operation for logging
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function

    Raises:
        The last exception encountered if all retries fail
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            if attempt > 0:
                logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
            return result

        except Exception as e:
            last_exception = e

            # Check if this exception type is retryable
            if not isinstance(e, retryable_exceptions):
                logger.error(f"{operation_name} failed with non-retryable error: {e}")
                raise

            if attempt < max_retries:
                delay = base_delay * (backoff_multiplier**attempt)
                logger.warning(
                    f"{operation_name} attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f} seconds..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"{operation_name} failed after {max_retries + 1} attempts")

    if last_exception:
        raise last_exception

    # This should never happen, but just in case
    raise RuntimeError(f"{operation_name} failed with unknown error")


def timeout_handler(
    timeout_seconds: float,
    operation_name: str | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator to add timeout handling to async functions.

    Args:
        timeout_seconds: Timeout in seconds
        operation_name: Name of the operation (defaults to function name)

    Returns:
        Decorated function with timeout handling

    Example:
        ```python
        @timeout_handler(30.0, "database_query")
        async def query_database():
            # This will timeout after 30 seconds
            return await slow_db_operation()
        ```
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            op_name = operation_name or func.__name__
            return await with_timeout(func(*args, **kwargs), timeout_seconds, op_name)

        return wrapper

    return decorator


def retry_handler(
    max_retries: int = MAX_RETRIES,
    base_delay: float = RETRY_DELAY_SECONDS,
    backoff_multiplier: float = EXPONENTIAL_BACKOFF_MULTIPLIER,
    retryable_exceptions: tuple[type[Exception], ...] = (NetworkError, BrowserManagerError),
    operation_name: str | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator to add retry handling to async functions.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries
        backoff_multiplier: Multiplier for exponential backoff
        retryable_exceptions: Exception types that should trigger retries
        operation_name: Name of the operation (defaults to function name)

    Returns:
        Decorated function with retry handling

    Example:
        ```python
        @retry_handler(max_retries=3, operation_name="api_call")
        async def call_api():
            # This will retry up to 3 times on network errors
            return await make_http_request()
        ```
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            op_name = operation_name or func.__name__
            return await with_retries(
                func,
                *args,
                max_retries=max_retries,
                base_delay=base_delay,
                backoff_multiplier=backoff_multiplier,
                retryable_exceptions=retryable_exceptions,
                operation_name=op_name,
                **kwargs,
            )

        return wrapper

    return decorator


class GracefulTimeout:
    """Context manager for graceful timeout handling with cleanup.

    This class provides a way to execute operations with a timeout while
    ensuring proper cleanup even if the operation times out.
    """

    def __init__(
        self,
        timeout_seconds: float,
        operation_name: str,
        cleanup_func: Callable[[], Awaitable[None]] | None = None,
    ):
        """Initialize graceful timeout.

        Args:
            timeout_seconds: Timeout in seconds
            operation_name: Name of the operation for logging
            cleanup_func: Optional cleanup function to call on timeout
        """
        self.timeout_seconds = timeout_seconds
        self.operation_name = operation_name
        self.cleanup_func = cleanup_func
        self.start_time: float | None = None
        self.task: asyncio.Task[Any] | None = None

    async def __aenter__(self) -> "GracefulTimeout":
        """Enter the timeout context."""
        self.start_time = time.time()
        logger.debug(f"Starting {self.operation_name} with {self.timeout_seconds}s timeout")
        return self

    async def __aexit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """Exit the timeout context with cleanup."""
        if self.start_time:
            elapsed = time.time() - self.start_time

            if exc_type is asyncio.TimeoutError:
                logger.error(f"{self.operation_name} timed out after {elapsed:.1f}s")
                if self.cleanup_func:
                    try:
                        await self.cleanup_func()
                        logger.debug(f"Cleanup completed for {self.operation_name}")
                    except Exception as cleanup_error:
                        logger.error(f"Cleanup failed for {self.operation_name}: {cleanup_error}")
            else:
                logger.debug(f"{self.operation_name} completed in {elapsed:.1f}s")

    async def run(self, awaitable: Awaitable[T]) -> T:
        """Run an awaitable with timeout handling.

        Args:
            awaitable: The awaitable to execute

        Returns:
            The result of the awaitable

        Raises:
            TimeoutError: If the operation times out
        """
        return await with_timeout(awaitable, self.timeout_seconds, self.operation_name)


def log_operation_timing(operation_name: str) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator to log operation timing.

    Args:
        operation_name: Name of the operation to log

    Returns:
        Decorated function with timing logs
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"{operation_name} completed successfully in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{operation_name} failed after {elapsed:.2f}s: {e}")
                raise

        return wrapper

    return decorator
