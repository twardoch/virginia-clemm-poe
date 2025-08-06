# this_file: src/virginia_clemm_poe/utils/paths.py
"""Cross-platform path management module.

This module provides utilities for managing application paths across different
platforms following the PlaywrightAuthor architecture pattern.
"""

import platform
from pathlib import Path

from loguru import logger


def get_app_name() -> str:
    """Get the application name for directory creation."""
    return "virginia-clemm-poe"


def get_cache_dir() -> Path:
    """Get the platform-appropriate cache directory.

    Uses platformdirs for cross-platform compatibility, with fallbacks
    for systems where platformdirs might not work as expected.

    Returns:
        Path to the cache directory for the application.
    """
    try:
        import platformdirs

        cache_dir = Path(platformdirs.user_cache_dir(get_app_name()))
    except ImportError:
        # Fallback if platformdirs not available
        cache_dir = _get_fallback_cache_dir()
    except Exception as e:
        logger.warning(f"Error using platformdirs: {e}, using fallback")
        cache_dir = _get_fallback_cache_dir()

    # Ensure directory exists
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Using cache directory: {cache_dir}")

    return cache_dir


def get_data_dir() -> Path:
    """Get the platform-appropriate data directory.

    Uses platformdirs for cross-platform compatibility, with fallbacks
    for systems where platformdirs might not work as expected.

    Returns:
        Path to the data directory for the application.
    """
    try:
        import platformdirs

        data_dir = Path(platformdirs.user_data_dir(get_app_name()))
    except ImportError:
        # Fallback if platformdirs not available
        data_dir = _get_fallback_data_dir()
    except Exception as e:
        logger.warning(f"Error using platformdirs: {e}, using fallback")
        data_dir = _get_fallback_data_dir()

    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Using data directory: {data_dir}")

    return data_dir


def get_config_dir() -> Path:
    """Get the platform-appropriate config directory.

    Uses platformdirs for cross-platform compatibility, with fallbacks
    for systems where platformdirs might not work as expected.

    Returns:
        Path to the config directory for the application.
    """
    try:
        import platformdirs

        config_dir = Path(platformdirs.user_config_dir(get_app_name()))
    except ImportError:
        # Fallback if platformdirs not available
        config_dir = _get_fallback_config_dir()
    except Exception as e:
        logger.warning(f"Error using platformdirs: {e}, using fallback")
        config_dir = _get_fallback_config_dir()

    # Ensure directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Using config directory: {config_dir}")

    return config_dir


def _get_fallback_cache_dir() -> Path:
    """Get fallback cache directory when platformdirs is not available."""
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        return home / "Library" / "Caches" / get_app_name()
    if system == "Windows":
        local_app_data = Path.home() / "AppData" / "Local"
        if local_app_data.exists():
            return local_app_data / get_app_name() / "Cache"
        return home / f".{get_app_name()}" / "cache"
    # Linux and others
    xdg_cache = Path.home() / ".cache"
    return xdg_cache / get_app_name()


def _get_fallback_data_dir() -> Path:
    """Get fallback data directory when platformdirs is not available."""
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        return home / "Library" / "Application Support" / get_app_name()
    if system == "Windows":
        local_app_data = Path.home() / "AppData" / "Local"
        if local_app_data.exists():
            return local_app_data / get_app_name()
        return home / f".{get_app_name()}" / "data"
    # Linux and others
    xdg_data = Path.home() / ".local" / "share"
    return xdg_data / get_app_name()


def _get_fallback_config_dir() -> Path:
    """Get fallback config directory when platformdirs is not available."""
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        return home / "Library" / "Preferences" / get_app_name()
    if system == "Windows":
        app_data = Path.home() / "AppData" / "Roaming"
        if app_data.exists():
            return app_data / get_app_name()
        return home / f".{get_app_name()}" / "config"
    # Linux and others
    xdg_config = Path.home() / ".config"
    return xdg_config / get_app_name()


def get_chrome_install_dir() -> Path:
    """Get the directory for Chrome for Testing installations.

    Returns:
        Path to Chrome installation directory within cache.
    """
    return get_cache_dir() / "chrome-for-testing"


def get_models_data_path() -> Path:
    """Get the path to the models data file.

    Returns:
        Path to the poe_models.json file.
    """
    # First check if we're in development mode (package data exists)
    package_data = Path(__file__).parent.parent / "data" / "poe_models.json"
    if package_data.exists():
        return package_data

    # Otherwise use user data directory
    return get_data_dir() / "poe_models.json"
