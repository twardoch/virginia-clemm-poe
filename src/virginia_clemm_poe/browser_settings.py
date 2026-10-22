# this_file: src/virginia_clemm_poe/browser_settings.py
"""Explicit engine/account/visibility selection for every Poe browser operation."""

import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrowserSettings:
    """An identity is independent of saved HTTP cookie exports."""

    engine: str = "chrome"
    profile: str = "poe-primary"
    mode: str = "auto"
    executable_path: Path | None = None
    profile_root: Path | None = None

    def __post_init__(self) -> None:
        if self.engine not in {"chrome", "chromium", "firefox", "cloak", "camoufox"}:
            raise ValueError("browser_engine must be chrome, chromium, firefox or cloak")
        if self.mode not in {"auto", "headless", "interactive"}:
            raise ValueError("browser_mode must be auto, headless or interactive")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", self.profile):
            raise ValueError("browser_profile must be a single safe account name")


def browser_settings(
    engine: str | None = None,
    profile: str | None = None,
    mode: str | None = None,
    executable_path: str | Path | None = None,
) -> BrowserSettings:
    """Explicit command settings override VCP_BROWSER_* environment defaults."""
    binary = executable_path if executable_path is not None else os.environ.get("VCP_BROWSER_EXECUTABLE_PATH")
    return BrowserSettings(
        engine=engine if engine is not None else os.environ.get("VCP_BROWSER_ENGINE", "chrome"),
        profile=profile if profile is not None else os.environ.get("VCP_BROWSER_PROFILE", "poe-primary"),
        mode=mode if mode is not None else os.environ.get("VCP_BROWSER_MODE", "auto"),
        executable_path=Path(binary) if binary else None,
    )
