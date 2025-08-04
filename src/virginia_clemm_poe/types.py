# this_file: src/virginia_clemm_poe/types.py
"""Shared type definitions for Virginia Clemm Poe.

This module defines complex types used across multiple modules to improve
type safety, code documentation, and maintainability. It follows the
Python 3.12+ type hint standards using modern syntax.
"""

from collections.abc import Callable
from typing import Any, Literal, NotRequired, TypedDict

# API Response Types


class PoeApiModelData(TypedDict):
    """Type definition for model data from Poe API response.

    Represents the structure of individual model objects returned
    by the Poe.com API endpoint.
    """

    id: str
    object: Literal["model"]
    created: int
    owned_by: str
    permission: list[Any]
    root: str
    parent: NotRequired[str]
    architecture: dict[str, Any]


class PoeApiResponse(TypedDict):
    """Type definition for Poe API /models endpoint response.

    Represents the complete API response structure containing
    metadata and model data.
    """

    object: Literal["list"]
    data: list[PoeApiModelData]


# Filter and Search Types


class ModelFilterCriteria(TypedDict, total=False):
    """Filter criteria for model search and filtering operations.

    Used by API functions to specify search and filter parameters.
    All fields are optional to allow flexible filtering.
    """

    has_pricing: bool
    needs_update: bool
    owned_by: str
    input_modalities: list[str]
    output_modalities: list[str]
    created_after: int
    created_before: int


class SearchOptions(TypedDict, total=False):
    """Options for model search operations.

    Controls search behavior and result formatting in API functions.
    """

    case_sensitive: bool
    exact_match: bool
    include_description: bool
    max_results: int
    sort_by: Literal["id", "created", "owned_by"]
    sort_order: Literal["asc", "desc"]


# Browser and Scraping Types


class BrowserConfig(TypedDict, total=False):
    """Configuration options for browser management.

    Used by BrowserManager and related classes for browser setup
    and operation configuration.
    """

    debug_port: int
    headless: bool
    viewport_width: int
    viewport_height: int
    user_agent: str
    timeout_ms: int
    extra_flags: list[str]


class ScrapingResult(TypedDict):
    """Result of web scraping operations.

    Standardized return type for scraping functions to ensure
    consistent error handling and result processing.
    """

    success: bool
    data: dict[str, Any] | None
    error_message: str | None
    scraped_fields: list[str]
    duration_seconds: float


# Logging and Context Types


class LogContext(TypedDict, total=False):
    """Context information for structured logging.

    Base type for logging context that can be extended with
    operation-specific fields.
    """

    operation: str
    operation_id: str
    duration_seconds: float
    user_id: str | None
    session_id: str | None


class ApiLogContext(LogContext, total=False):
    """Extended context for API operation logging.

    Includes API-specific context information for request/response
    logging and monitoring.
    """

    method: str
    url: str
    status_code: int
    response_size: int
    models_fetched: int
    endpoint: str
    api_version: str


class BrowserLogContext(LogContext, total=False):
    """Extended context for browser operation logging.

    Includes browser-specific context for automation operations
    and debugging.
    """

    browser_operation: str
    model_id: str
    debug_port: int
    page_url: str
    scraped_fields: list[str]
    timeout_ms: int


class PerformanceMetric(TypedDict):
    """Performance metric data structure.

    Standardized format for performance monitoring and
    optimization tracking.
    """

    metric_name: str
    metric_value: float
    metric_unit: str
    timestamp: float
    context: dict[str, Any]


# CLI and User Interface Types


class CliCommand(TypedDict):
    """CLI command execution context.

    Tracks user command execution for analytics and debugging.
    """

    command: str
    action: str
    arguments: dict[str, Any]
    flags: dict[str, bool]
    timestamp: float


class DisplayOptions(TypedDict, total=False):
    """Options for controlling CLI output display.

    Used by CLI commands to control table formatting and
    information display.
    """

    show_pricing: bool
    show_bot_info: bool
    show_architecture: bool
    show_timestamps: bool
    max_description_length: int
    color_output: bool
    table_style: str


# Error and Exception Types


class ErrorContext(TypedDict, total=False):
    """Context information for error reporting and debugging.

    Provides structured error context for better debugging
    and user support.
    """

    error_type: str
    error_message: str
    operation: str
    model_id: str | None
    url: str | None
    status_code: int | None
    stack_trace: str | None
    recovery_suggestions: list[str]


# Update and Synchronization Types


class UpdateOptions(TypedDict, total=False):
    """Options for model data update operations.

    Controls what data is updated and how the update process
    behaves.
    """

    update_pricing: bool
    update_info: bool
    force_update: bool
    batch_size: int
    concurrent_limit: int
    retry_attempts: int
    retry_delay: float


class SyncProgress(TypedDict):
    """Progress tracking for synchronization operations.

    Provides structured progress information for long-running
    update operations.
    """

    total_models: int
    processed_models: int
    successful_updates: int
    failed_updates: int
    current_model: str | None
    estimated_remaining: float | None
    start_time: float
    errors: list[ErrorContext]


# Type Aliases for Convenience

# Common type aliases for frequently used complex types
ModelId = str
ApiKey = str
Timestamp = int
Duration = float
Url = str

# Union types for common optional patterns
OptionalString = str | None
OptionalInt = int | None
OptionalDict = dict[str, Any] | None
OptionalList = list[Any] | None

# Callback and handler types
LogHandler = Callable[[str, LogContext], None]
ErrorHandler = Callable[[Exception, ErrorContext], None]
ProgressCallback = Callable[[SyncProgress], None]
