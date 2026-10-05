# this_file: src/virginia_clemm_poe/vendors.py
"""Discover created bots from curated Poe vendor profiles."""

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import Page

from .bots import Architecture, BotInfo, PoeBot
from .config import PAGE_NAVIGATION_TIMEOUT_MS

PROFILE_WAIT_MS = 1000
PROFILE_SCROLL_WAIT_MS = 1500
MAX_PROFILE_SCROLLS = 200
MAX_STALLED_SCROLLS = 3

VENDOR_FILE = Path(__file__).parent / "data" / "good_vendors.txt"


def load_vendors() -> list[str]:
    """Read unique profile handles from the packaged vendor list."""
    handles = [
        line.strip() for line in VENDOR_FILE.read_text().splitlines() if line.strip() and not line.startswith("#")
    ]
    if any(not re.fullmatch(r"[A-Za-z0-9_]+", handle) for handle in handles):
        raise ValueError("Vendor file must contain Poe profile handles, not URLs")
    return list(dict.fromkeys(handles))


def parse_profile(html: str, vendor: str) -> tuple[list[PoeBot], int]:
    """Parse profile hydration data and the rendered Created panel, excluding other links."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.select_one("#__NEXT_DATA__")
    payload = json.loads(script.get_text()) if script else {}
    user = payload.get("props", {}).get("pageProps", {}).get("data", {}).get("mainQuery", {}).get("user")
    if not isinstance(user, dict) or user.get("handle", "").casefold() != vendor.casefold():
        raise ValueError(f"Missing or mismatched vendor profile: {vendor}")
    nodes = [edge["node"] for edge in user.get("createdBotsConnection", {}).get("edges", [])]
    found = {
        node["handle"]: node.get("description")
        for node in nodes
        if node.get("handle") and node.get("deletionState", "not_deleted") == "not_deleted"
    }
    # Hydration contains only the first page; the rendered panel grows on scroll.
    for item in soup.select("#profile-created-bots [data-bot-list-item]"):
        name = item.select_one("[class*=botName]")
        description = item.select_one("[class*=botDescription]")
        if name:
            found.setdefault(name.get_text(strip=True), description.get_text(strip=True) if description else None)
    bots = [
        PoeBot(
            id=handle,
            owned_by=vendor,
            root=handle,
            vendor_profile=vendor,
            architecture=Architecture(input_modalities=[], output_modalities=[], modality="unknown"),
            bot_info=BotInfo(creator=f"@{vendor}", description=description),
        )
        for handle, description in found.items()
        if re.fullmatch(r"[A-Za-z0-9_.-]+", handle)
    ]
    return bots, int(user["createdBotCount"])


async def scrape_profile(page: Page, vendor: str) -> list[PoeBot]:
    """Scroll a vendor profile to its advertised bot count; fail on incomplete discovery."""
    response = await page.goto(
        f"https://poe.com/{vendor}", wait_until="domcontentloaded", timeout=PAGE_NAVIGATION_TIMEOUT_MS
    )
    if response and isinstance(response.status, int) and response.status >= 400:
        raise ValueError(f"Profile {vendor} returned HTTP {response.status}")
    await page.wait_for_timeout(PROFILE_WAIT_MS)
    previous_count, stalled = -1, 0
    for _ in range(MAX_PROFILE_SCROLLS):
        bots, expected = parse_profile(await page.content(), vendor)
        if len(bots) >= expected:
            return bots
        stalled = stalled + 1 if len(bots) == previous_count else 0
        if stalled >= MAX_STALLED_SCROLLS:
            break
        previous_count = len(bots)
        await page.evaluate("""() => {
            const panel = document.querySelector('#profile-created-bots');
            for (let element = panel; element; element = element.parentElement) {
                if (['auto', 'scroll'].includes(getComputedStyle(element).overflowY)) {
                    element.scrollTop = element.scrollHeight;
                    return;
                }
            }
            window.scrollTo(0, document.body.scrollHeight);
        }""")
        await page.wait_for_timeout(PROFILE_SCROLL_WAIT_MS)
    raise ValueError(f"Incomplete profile {vendor}: found {len(bots)} of {expected} bots")
