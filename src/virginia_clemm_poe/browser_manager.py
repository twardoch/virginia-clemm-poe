# this_file: src/virginia_clemm_poe/browser_manager.py
"""One owned persistent context per Poe engine/account identity."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

import playwrightauthor
from playwright.async_api import Browser, BrowserContext, Page

if TYPE_CHECKING:
    from playwrightauthor.sessions import AsyncBrowserSession as OwnedSession

AsyncBrowserSession = getattr(playwrightauthor, "AsyncBrowserSession", None)

from .browser_auth import probe_poe_context
from .browser_settings import BrowserSettings, browser_settings
from .config import DEFAULT_DEBUG_PORT
from .exceptions import BrowserEngineUnavailable, PoeAuthenticationRequired


class BrowserManager:
    """Serialize session startup and create task pages in its authorized context."""

    def __init__(
        self,
        debug_port: int = DEFAULT_DEBUG_PORT,
        verbose: bool = False,
        reuse_session: bool = True,
        *,
        settings: BrowserSettings | None = None,
    ):
        # Kept for source compatibility; native sessions allocate no CDP port.
        self.debug_port = debug_port
        self.verbose = verbose
        self.reuse_session = reuse_session
        self.settings = settings or browser_settings()
        self._session: OwnedSession | None = None
        self._lock = asyncio.Lock()

    async def get_session(self) -> OwnedSession:
        """Start at most once; failed startup never becomes a cached session."""
        async with self._lock:
            if self._session is None:
                if AsyncBrowserSession is None:
                    raise BrowserEngineUnavailable(
                        "Install a session-capable PlaywrightAuthor or the paired local checkout before browser operations."
                    )
                options = self.settings
                session = cast(
                    "OwnedSession",
                    AsyncBrowserSession(
                        engine=options.engine,
                        profile=options.profile,
                        mode=options.mode,
                        executable_path=options.executable_path,
                        profile_root=options.profile_root,
                        service="Poe",
                        verbose=self.verbose,
                        suppress_dialog=options.mode != "interactive",
                        auth_probe=probe_poe_context if options.mode == "auto" else None,
                    ),
                )
                try:
                    await session.__aenter__()
                except Exception as error:
                    if getattr(error, "code", None) == "AUTH_REQUIRED":
                        raise PoeAuthenticationRequired(options.engine, options.profile) from error
                    raise
                self._session = session
            return self._session

    async def get_browser(self) -> Browser | None:
        """Compatibility accessor; callers must not assume a native browser handle exists."""
        return cast(Browser | None, (await self.get_session()).browser)

    async def get_context(self) -> BrowserContext:
        """Expose the required persistent context, independent of the engine."""
        return cast(BrowserContext, (await self.get_session()).context)

    async def get_page(self) -> Page:
        """Each call creates its own task tab; existing human tabs are never reused."""
        return cast(Page, await (await self.get_session()).new_page())

    @staticmethod
    async def setup_chrome() -> bool:
        """Verify/install CfT without launching a window or claiming a sign-in."""
        if AsyncBrowserSession is None:
            return False
        from loguru import logger
        from playwrightauthor.browser.finder import find_chrome_executable
        from playwrightauthor.browser.installer import install_from_lkgv

        if await asyncio.to_thread(find_chrome_executable, logger) is None:
            await asyncio.to_thread(install_from_lkgv, logger)
        return await asyncio.to_thread(find_chrome_executable, logger) is not None

    async def close(self) -> None:
        """The session owns context/driver teardown and cancellation-safe lease release."""
        async with self._lock:
            if self._session is not None:
                session = self._session
                try:
                    await session.close()
                finally:
                    self._session = None

    async def __aenter__(self) -> "BrowserManager":
        await self.get_session()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()
