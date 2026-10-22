# this_file: src/virginia_clemm_poe/browser_auth.py
"""Poe authorization checks and passive interactive-login observation."""

import asyncio
import re
from urllib.parse import urlsplit

from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeout

from .exceptions import AuthenticationError

SETTINGS_URL = "https://poe.com/settings?tab=subscription"
POINTS_SELECTOR = (
    "[class*='SettingsComputePointsSection_value'], [class*='SettingsComputePointsSection_inlinePointsRow']"
)
USER_MENU_SELECTOR = "button[aria-label='User menu']"


class ProviderRejected(AuthenticationError):
    """The provider explicitly refused this browser; no bypass is attempted."""

    code = "AUTH_REJECTED_BY_PROVIDER"


def _is_poe(url: str) -> bool:
    return urlsplit(url).hostname in {"poe.com", "www.poe.com"}


def parse_points_value(text: str) -> int | None:
    """Parse only a points row, including the current inline 'available' label."""
    match = re.fullmatch(r"(\d+(?:[,\s]\d+)*)\s*(?:available)?", text.strip())
    return int(re.sub(r"[,\s]", "", match.group(1))) if match else None


async def page_is_signed_in(page: Page) -> bool:
    """Inspect only a Poe account UI, not a public bot URL or cookie names."""
    if page.is_closed() or not _is_poe(page.url) or urlsplit(page.url).path.startswith("/login"):
        return False
    if await page.locator(USER_MENU_SELECTOR).first.is_visible():
        return True
    return await page.get_by_role("tab", name="Subscription and points", exact=True).is_visible()


async def probe_poe_context(context: BrowserContext) -> bool:
    """Verify a fresh settings response and rendered account points in a task-owned tab.

    The selector comes from this project's existing balance scraper. Live-provider
    compatibility remains an acceptance gate, not a promise made by this probe.
    """
    page = await context.new_page()
    try:
        response = await page.goto(SETTINGS_URL, wait_until="domcontentloaded", timeout=30000)
        if (
            response is None
            or response.status != 200
            or not _is_poe(page.url)
            or urlsplit(page.url).path != "/settings"
        ):
            return False
        points = page.locator(POINTS_SELECTOR).first
        await points.wait_for(state="visible", timeout=10000)
        return parse_points_value(await points.text_content() or "") is not None
    except PlaywrightTimeout:
        return False
    finally:
        await page.close()


async def wait_for_poe_login(page: Page, timeout_seconds: float = 300) -> None:
    """Observe context pages/popups without navigating the user's OAuth/MFA flow."""
    if timeout_seconds <= 0:
        raise ValueError("Login timeout must be positive")
    async with asyncio.timeout(timeout_seconds):
        while not page.is_closed():
            for candidate in list(page.context.pages):
                if candidate.is_closed():
                    continue
                if urlsplit(candidate.url).hostname == "accounts.google.com":
                    refusal = candidate.get_by_text("This browser or app may not be secure", exact=False)
                    if await refusal.first.is_visible():
                        raise ProviderRejected(
                            "Google refused this browser. Use a supported manual sign-in method; no automated bypass is available."
                        )
                if await page_is_signed_in(candidate) and await probe_poe_context(page.context):
                    return
            await asyncio.sleep(1)
    raise AuthenticationError("Login page closed before authorization was verified.")
