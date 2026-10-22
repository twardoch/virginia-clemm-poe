# this_file: src/virginia_clemm_poe/browser_commands.py
"""CLI browser-operation scope: close pools and return structured failures."""

import asyncio
from collections.abc import Coroutine
from typing import Any

from rich.console import Console

from .exceptions import AuthenticationError


def run_browser_command(operation: Coroutine[Any, Any, None]) -> None:
    """Close loop-owned pools on success/error/cancellation; never request login UI."""

    async def scoped() -> None:
        from .browser_pool import close_global_pool

        try:
            await operation
        finally:
            await close_global_pool()

    try:
        asyncio.run(scoped())
    except Exception as error:
        code = getattr(
            error, "code", "AUTH_REQUIRED" if isinstance(error, AuthenticationError) else "BROWSER_COMMAND_FAILED"
        )
        message = str(error) or (
            "Browser operation timed out; retry explicit login if authorization was not verified."
            if isinstance(error, TimeoutError)
            else type(error).__name__
        )
        detail = {"code": code, "message": message}
        command = getattr(error, "command", None)
        if command:
            detail["login_command"] = command
        Console(stderr=True).print_json(data={"error": detail})
        raise SystemExit(3 if code == "AUTH_REQUIRED" else 1) from error
