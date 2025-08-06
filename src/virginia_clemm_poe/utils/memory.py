# this_file: src/virginia_clemm_poe/utils/memory.py
"""Memory management utilities for Virginia Clemm Poe.

This module provides utilities for monitoring and managing memory usage
during long-running operations, ensuring steady-state usage stays below
200MB with automatic cleanup and garbage collection.
"""

import asyncio
import gc
import os
import time
from collections.abc import Callable
from typing import Any

import psutil
from loguru import logger

from ..utils.logger import log_performance_metric

# Memory thresholds in MB
MEMORY_WARNING_THRESHOLD_MB = 150
MEMORY_CRITICAL_THRESHOLD_MB = 200
MEMORY_CLEANUP_THRESHOLD_MB = 180
MEMORY_MONITORING_INTERVAL_SECONDS = 30.0

# Memory cleanup configuration
GC_COLLECT_THRESHOLD_OPERATIONS = 50  # Run GC after this many operations
FORCE_GC_MEMORY_THRESHOLD_MB = 160  # Force GC when memory exceeds this


class MemoryMonitor:
    """Monitors and manages memory usage for long-running operations."""

    def __init__(
        self,
        warning_threshold_mb: float = MEMORY_WARNING_THRESHOLD_MB,
        critical_threshold_mb: float = MEMORY_CRITICAL_THRESHOLD_MB,
    ):
        """Initialize memory monitor.

        Args:
            warning_threshold_mb: Threshold to log warnings
            critical_threshold_mb: Threshold to trigger cleanup
        """
        self.warning_threshold_mb = warning_threshold_mb
        self.critical_threshold_mb = critical_threshold_mb
        self.process = psutil.Process(os.getpid())
        self.operation_count = 0
        self.last_cleanup_time = time.time()
        self.peak_memory_mb = 0.0

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB.

        Returns:
            Current memory usage in megabytes
        """
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB

            # Track peak memory usage
            self.peak_memory_mb = max(self.peak_memory_mb, memory_mb)

            return memory_mb
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0

    def check_memory_usage(self) -> dict[str, Any]:
        """Check current memory usage and return status.

        Returns:
            Dictionary with memory status information
        """
        current_mb = self.get_memory_usage_mb()

        status = {
            "current_mb": current_mb,
            "peak_mb": self.peak_memory_mb,
            "warning_threshold_mb": self.warning_threshold_mb,
            "critical_threshold_mb": self.critical_threshold_mb,
            "above_warning": current_mb > self.warning_threshold_mb,
            "above_critical": current_mb > self.critical_threshold_mb,
            "operation_count": self.operation_count,
        }

        # Log performance metric
        log_performance_metric(
            "memory_usage",
            current_mb,
            "MB",
            {
                "peak_mb": self.peak_memory_mb,
                "above_warning": status["above_warning"],
                "above_critical": status["above_critical"],
            },
        )

        return status

    def should_run_cleanup(self) -> bool:
        """Check if memory cleanup should be performed using multi-criteria decision logic.

        This method evaluates three independent criteria to determine if memory cleanup
        is needed, implementing a comprehensive memory management strategy:

        Decision criteria (evaluated in order):
        1. Memory threshold check: Current usage > MEMORY_CLEANUP_THRESHOLD_MB (180MB)
        2. Operation count check: >= GC_COLLECT_THRESHOLD_OPERATIONS (50 operations)
        3. Time-based check: > MEMORY_MONITORING_INTERVAL_SECONDS (30s) since last cleanup

        Returns:
            True if ANY criteria is met (OR logic), False if all criteria fail

        Example usage:
            >>> monitor = MemoryMonitor()
            >>> if monitor.should_run_cleanup():
            ...     await monitor.cleanup_memory()

        Note:
            This uses OR logic rather than AND logic to be proactive about memory management.
            Any single condition being true triggers cleanup to prevent memory buildup.
        """
        current_mb = self.get_memory_usage_mb()

        # Check if we're above the cleanup threshold
        if current_mb > MEMORY_CLEANUP_THRESHOLD_MB:
            return True

        # Check if we've done enough operations to warrant cleanup
        if self.operation_count >= GC_COLLECT_THRESHOLD_OPERATIONS:
            return True

        # Check if it's been a while since last cleanup
        time_since_cleanup = time.time() - self.last_cleanup_time
        return time_since_cleanup > MEMORY_MONITORING_INTERVAL_SECONDS

    async def cleanup_memory(self, force: bool = False) -> dict[str, Any]:
        """Perform memory cleanup operations.

        Args:
            force: Force cleanup regardless of thresholds

        Returns:
            Dictionary with cleanup results
        """
        if not force and not self.should_run_cleanup():
            return {"cleanup_performed": False, "reason": "thresholds_not_met"}

        memory_before = self.get_memory_usage_mb()
        logger.debug(f"Running memory cleanup, current usage: {memory_before:.1f}MB")

        cleanup_start = time.time()

        try:
            # Run garbage collection
            collected_objects = gc.collect()

            # Force garbage collection for all generations
            for generation in [0, 1, 2]:
                gc.collect(generation)

            # Allow async tasks to yield
            await asyncio.sleep(0.01)

            memory_after = self.get_memory_usage_mb()
            cleanup_time = time.time() - cleanup_start
            memory_freed = memory_before - memory_after

            # Reset counters
            self.operation_count = 0
            self.last_cleanup_time = time.time()

            result = {
                "cleanup_performed": True,
                "memory_before_mb": memory_before,
                "memory_after_mb": memory_after,
                "memory_freed_mb": memory_freed,
                "cleanup_time_seconds": cleanup_time,
                "objects_collected": collected_objects,
                "forced": force,
            }

            # Log performance metric
            log_performance_metric(
                "memory_cleanup",
                memory_freed,
                "MB",
                {
                    "cleanup_time_seconds": cleanup_time,
                    "objects_collected": collected_objects,
                    "memory_after_mb": memory_after,
                },
            )

            logger.info(
                f"Memory cleanup completed: freed {memory_freed:.1f}MB, "
                f"collected {collected_objects} objects in {cleanup_time:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            return {
                "cleanup_performed": False,
                "error": str(e),
                "memory_before_mb": memory_before,
            }

    def increment_operation_count(self) -> None:
        """Increment the operation counter."""
        self.operation_count += 1

        # Check if we should force garbage collection
        current_mb = self.get_memory_usage_mb()
        if current_mb > FORCE_GC_MEMORY_THRESHOLD_MB:
            logger.debug(f"Memory usage {current_mb:.1f}MB exceeds force GC threshold, running cleanup")
            # Schedule cleanup for next event loop iteration
            asyncio.create_task(self.cleanup_memory(force=True))

    def log_memory_status(self, operation_name: str = "operation") -> None:
        """Log current memory status.

        Args:
            operation_name: Name of the operation for context
        """
        status = self.check_memory_usage()

        if status["above_critical"]:
            logger.error(
                f"{operation_name}: Memory usage {status['current_mb']:.1f}MB "
                f"exceeds critical threshold {self.critical_threshold_mb}MB"
            )
        elif status["above_warning"]:
            logger.warning(
                f"{operation_name}: Memory usage {status['current_mb']:.1f}MB "
                f"exceeds warning threshold {self.warning_threshold_mb}MB"
            )
        else:
            logger.debug(
                f"{operation_name}: Memory usage {status['current_mb']:.1f}MB (peak: {status['peak_mb']:.1f}MB)"
            )


class MemoryManagedOperation:
    """Context manager for memory-managed operations."""

    def __init__(self, operation_name: str, monitor: MemoryMonitor | None = None, cleanup_on_exit: bool = True):
        """Initialize memory-managed operation.

        Args:
            operation_name: Name of the operation
            monitor: Memory monitor to use (creates new one if None)
            cleanup_on_exit: Whether to run cleanup on exit
        """
        self.operation_name = operation_name
        self.monitor = monitor or MemoryMonitor()
        self.cleanup_on_exit = cleanup_on_exit
        self.start_memory_mb = 0.0

    async def __aenter__(self) -> MemoryMonitor:
        """Enter the memory-managed operation context."""
        self.start_memory_mb = self.monitor.get_memory_usage_mb()
        logger.debug(f"Starting {self.operation_name}, memory usage: {self.start_memory_mb:.1f}MB")
        return self.monitor

    async def __aexit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """Exit the memory-managed operation context."""
        end_memory_mb = self.monitor.get_memory_usage_mb()
        memory_delta = end_memory_mb - self.start_memory_mb

        logger.debug(
            f"Completed {self.operation_name}, memory usage: {end_memory_mb:.1f}MB (delta: {memory_delta:+.1f}MB)"
        )

        # Run cleanup if requested or if memory usage is high
        if self.cleanup_on_exit or end_memory_mb > MEMORY_CLEANUP_THRESHOLD_MB:
            await self.monitor.cleanup_memory()


# Global memory monitor instance
_global_monitor: MemoryMonitor | None = None


def get_global_memory_monitor() -> MemoryMonitor:
    """Get or create the global memory monitor.

    Returns:
        The global memory monitor instance
    """
    global _global_monitor

    if _global_monitor is None:
        _global_monitor = MemoryMonitor()

    return _global_monitor


async def monitor_memory_usage(
    func: Callable[[], Any],
    operation_name: str,
    monitor: MemoryMonitor | None = None,
) -> Any:
    """Monitor memory usage during a function call.

    Args:
        func: Function to monitor
        operation_name: Name of the operation
        monitor: Memory monitor to use

    Returns:
        Result of the function call
    """
    async with MemoryManagedOperation(operation_name, monitor) as mem_monitor:
        mem_monitor.increment_operation_count()
        result = await func() if asyncio.iscoroutinefunction(func) else func()
        mem_monitor.log_memory_status(operation_name)
        return result


def memory_managed(operation_name: str | None = None) -> Callable[[Callable], Callable]:
    """Decorator to add memory management to functions.

    Args:
        operation_name: Name of the operation (defaults to function name)

    Returns:
        Decorated function with memory management
    """

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            monitor = get_global_memory_monitor()

            async with MemoryManagedOperation(op_name, monitor):
                monitor.increment_operation_count()
                result = await func(*args, **kwargs)
                monitor.log_memory_status(op_name)
                return result

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            monitor = get_global_memory_monitor()

            monitor.increment_operation_count()
            result = func(*args, **kwargs)
            monitor.log_memory_status(op_name)
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
