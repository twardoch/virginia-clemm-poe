# this_file: src/virginia_clemm_poe/utils/logger.py
"""Centralized logging configuration module.

This module configures loguru for consistent logging across the application
following the PlaywrightAuthor architecture pattern. It provides structured
logging with context managers for operation tracking and performance monitoring.
"""

import sys
import time
from contextlib import contextmanager
from typing import Any

from loguru import logger


def configure_logger(verbose: bool = False, log_file: str | None = None, format_string: str | None = None) -> None:
    """Configure loguru logger with consistent settings.

    Sets up logging configuration for the entire application with
    appropriate log levels and formatting.

    Args:
        verbose: Enable verbose (DEBUG) logging.
        log_file: Optional path to log file for persistent logging.
        format_string: Custom format string for log messages.
    """
    # Remove default logger
    logger.remove()

    # Default format if not provided
    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

    # Console handler
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, format=format_string, level=level, colorize=True, backtrace=True, diagnose=True)

    # File handler if specified
    if log_file:
        logger.add(
            log_file,
            format=format_string,
            level="DEBUG",  # Always log DEBUG to file
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )

    # Log configuration
    logger.debug(f"Logger configured with level: {level}")
    if log_file:
        logger.debug(f"Logging to file: {log_file}")


def get_logger(name: str) -> Any:
    """Get a logger instance with the given name.

    This is a convenience function that returns the loguru logger
    but allows for future customization per module if needed.

    Args:
        name: Name for the logger (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logger.bind(name=name)


@contextmanager
def log_operation(operation_name: str, context: dict[str, Any] | None = None, log_level: str = "INFO") -> Any:
    """Context manager for logging operations with timing and context.

    This context manager provides structured logging for operations with:
    - Start and completion logging
    - Automatic timing measurement
    - Exception handling and logging
    - Contextual information tracking

    Args:
        operation_name: Human-readable name of the operation (e.g., "API request", "Browser launch")
        context: Optional dictionary of contextual information to include in logs
        log_level: Log level for success messages (DEBUG, INFO, WARNING, ERROR)

    Yields:
        dict: Context dictionary that can be updated during operation

    Examples:
        ```python
        with log_operation("API request", {"endpoint": "models", "method": "GET"}):
            response = await client.get("/models")

        with log_operation("Browser launch", {"port": 9222}) as ctx:
            browser = await playwright.launch()
            ctx["browser_pid"] = browser.pid
        ```
    """
    start_time = time.time()
    ctx = context or {}
    operation_id = f"{operation_name}_{int(start_time * 1000)}"

    # Bind operation context to logger
    op_logger = logger.bind(operation=operation_name, operation_id=operation_id, **ctx)

    op_logger.log(log_level, f"Starting {operation_name}", **ctx)

    try:
        yield ctx

        duration = time.time() - start_time
        op_logger.bind(duration_seconds=duration).log(
            log_level, f"Completed {operation_name} in {duration:.2f}s", **ctx
        )

    except Exception as e:
        duration = time.time() - start_time
        op_logger.bind(duration_seconds=duration, error_type=type(e).__name__, error_message=str(e)).error(
            f"Failed {operation_name} after {duration:.2f}s: {e}", **ctx
        )
        raise


@contextmanager
def log_api_request(method: str, url: str, headers: dict[str, str] | None = None) -> Any:
    """Context manager for logging API requests with timing and response info.

    Specialized context manager for HTTP API requests that logs request details,
    response status, timing, and any errors that occur.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Optional request headers (sensitive data will be masked)

    Yields:
        dict: Context dictionary with request info

    Examples:
        ```python
        with log_api_request("GET", "https://api.poe.com/models") as ctx:
            response = await client.get(url)
            ctx["status_code"] = response.status_code
            ctx["response_size"] = len(response.content)
        ```
    """
    # Mask sensitive headers
    safe_headers = {}
    if headers:
        for key, value in headers.items():
            if key.lower() in ("authorization", "x-api-key", "cookie"):
                safe_headers[key] = "***MASKED***"
            else:
                safe_headers[key] = value

    context = {"method": method, "url": url, "headers": safe_headers}

    with log_operation(f"API {method} request", context, "DEBUG") as ctx:
        yield ctx


@contextmanager
def log_browser_operation(operation: str, model_id: str | None = None, debug_port: int | None = None) -> Any:
    """Context manager for logging browser operations with model context.

    Specialized context manager for browser automation operations that includes
    model-specific context and browser configuration details.

    Args:
        operation: Browser operation name (e.g., "scrape_model", "launch_browser")
        model_id: Optional model ID being processed
        debug_port: Optional Chrome debug port

    Yields:
        dict: Context dictionary with browser operation info

    Examples:
        ```python
        with log_browser_operation("scrape_model", "Claude-3-Opus", 9222) as ctx:
            await page.goto(url)
            ctx["scraped_fields"] = ["pricing", "bot_info"]
        ```
    """
    context: dict[str, Any] = {"browser_operation": operation}

    if model_id:
        context["model_id"] = model_id
    if debug_port:
        context["debug_port"] = debug_port

    with log_operation(f"Browser {operation}", context, "DEBUG") as ctx:
        yield ctx


def log_performance_metric(
    metric_name: str, value: float, unit: str = "seconds", context: dict[str, Any] | None = None
) -> None:
    """Log performance metrics for monitoring and optimization.

    Records performance metrics with structured logging for analysis and monitoring.
    Useful for tracking response times, throughput, resource usage, etc.

    Args:
        metric_name: Name of the metric (e.g., "api_response_time", "models_processed")
        value: Numeric value of the metric
        unit: Unit of measurement (e.g., "seconds", "count", "bytes")
        context: Optional additional context information

    Examples:
        ```python
        log_performance_metric("api_response_time", 0.245, "seconds", {"endpoint": "/models"})
        log_performance_metric("models_scraped", 42, "count", {"session_id": "abc123"})
        ```
    """
    ctx = context or {}
    logger.bind(metric_name=metric_name, metric_value=value, metric_unit=unit, **ctx).info(
        f"Performance metric: {metric_name}={value} {unit}"
    )


def log_user_action(action: str, command: str | None = None, **kwargs: Any) -> None:
    """Log user actions for CLI usage tracking and debugging.

    Records user interactions with the CLI for usage analytics and debugging
    user workflows. Helps understand how the tool is being used.

    Args:
        action: The action performed (e.g., "search", "update", "setup")
        command: Full command executed (optional)
        **kwargs: Additional context about the action

    Examples:
        ```python
        log_user_action("search", query="claude", results_count=5)
        log_user_action("update", force=True, pricing=True, models_updated=42)
        ```
    """
    logger.bind(user_action=action, command=command, **kwargs).info(f"User action: {action}")
