#!/usr/bin/env -S uv run --no-sync
# this_file: scripts/verify_owned_pool.py
"""Exercise real Poe adapter/pool/probe code against intercepted fixture responses.

Use the local paired PlaywrightAuthor checkout in this environment. This proves
browser/session wiring and cancellation, not live Poe/provider authorization.
"""

import asyncio
import json
import subprocess
import tempfile
import threading
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import fire
from playwright.async_api import BrowserContext, Route

from virginia_clemm_poe import browser_manager
from virginia_clemm_poe.browser_auth import probe_poe_context
from virginia_clemm_poe.browser_pool import BrowserPool
from virginia_clemm_poe.browser_settings import BrowserSettings
from virginia_clemm_poe.exceptions import PoeAuthenticationRequired

_OBSERVE = """ObjC.import('AppKit'); ObjC.import('CoreGraphics');
var w=ObjC.deepUnwrap(ObjC.castRefToObject($.CGWindowListCopyWindowInfo(1,0)));
JSON.stringify({frontmost:$.NSWorkspace.sharedWorkspace.frontmostApplication.bundleIdentifier.js,
windows:w.filter(x=>['Google Chrome for Testing','Chromium','Firefox','Nightly'].indexOf(x.kCGWindowOwnerName)>=0).length});"""


def observe() -> dict:
    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", "-e", _OBSERVE],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return json.loads(result.stdout)


async def check_engine(settings: BrowserSettings) -> dict:
    authorized = True

    async def route(request: Route) -> None:
        if not authorized and request.request.url.split("?")[0].endswith("/settings"):
            await request.fulfill(status=302, headers={"Location": "https://poe.com/login"})
        else:
            html = "<title>fixture</title>" + (
                "<button aria-label='User menu'>Account</button><div class='SettingsComputePointsSection_value'>1,234</div>"
                if authorized
                else "<p>Login required</p>"
            )
            await request.fulfill(status=200, content_type="text/html", body=html)

    async def fixture_probe(context: BrowserContext) -> bool:
        await context.route("https://poe.com/**", route)
        return await probe_poe_context(context)

    original = browser_manager.probe_poe_context
    browser_manager.probe_poe_context = fixture_probe
    pool = BrowserPool(max_size=2, settings=settings)
    browser_version = None
    try:
        await pool.start()
        async with pool.acquire_page() as first:
            active = await pool._manager.get_session()
            browser_version = active.browser.version if active.browser else None
            await first.goto("https://poe.com/fixture")
            async with pool.acquire_page() as second:
                assert first is not second and first.context is second.context
                await second.goto("https://poe.com/fixture")
            assert await first.title() == "fixture"
        ready = asyncio.Event()
        cancelled_page = None

        async def job() -> None:
            nonlocal cancelled_page
            async with pool.acquire_page() as page:
                cancelled_page = page
                ready.set()
                await asyncio.Event().wait()

        task = asyncio.create_task(job())
        await asyncio.wait_for(ready.wait(), 30)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert cancelled_page.is_closed()
        async with pool.acquire_page() as page:
            await page.goto("https://poe.com/fixture")
            assert await page.title() == "fixture"
        await pool.stop()
        authorized = False
        rejected = BrowserPool(settings=settings)
        try:
            async with rejected.acquire_page():
                raise AssertionError("Unauthenticated auto mode entered")
        except PoeAuthenticationRequired:
            pass
        finally:
            await rejected.stop()
    finally:
        await pool.stop()
        browser_manager.probe_poe_context = original
    return {
        "engine": settings.engine,
        "browser_version": browser_version,
        "shared_owned_context": True,
        "distinct_job_tabs": True,
        "cancelled_job_tab_closed": True,
        "remaining_jobs_survive": True,
        "unauthenticated_auto_rejected": True,
    }


def verify(chrome_binary: str, output: str = "issues/340-poe-owned-pool.json") -> dict:
    baseline = observe()
    samples, errors, engines = [], [], []
    phase = {"engine": "startup"}
    stop = threading.Event()

    def sample() -> None:
        while not stop.is_set():
            try:
                samples.append(observe() | {"engine": phase["engine"]})
            except Exception as error:
                errors.append(type(error).__name__)
                return
            stop.wait(0.1)

    sampling = threading.Thread(target=sample)
    sampling.start()
    try:
        with tempfile.TemporaryDirectory(prefix="poe340-") as temporary:
            for engine in ("chrome", "chromium", "firefox"):
                phase["engine"] = engine
                settings = BrowserSettings(
                    engine=engine,
                    profile_root=Path(temporary),
                    executable_path=Path(chrome_binary) if engine == "chrome" else None,
                )
                engines.append(asyncio.run(check_engine(settings)))
    finally:
        stop.set()
        sampling.join(timeout=12)
    result = {
        "checked_at": datetime.now(UTC).isoformat(),
        "playwright_version": version("playwright"),
        "engines": engines,
        "samples": len(samples),
        "baseline_frontmost": baseline.get("frontmost"),
        "focus_change_observations": [
            {
                "engine": engine,
                "frontmost": app,
                "count": sum(1 for sample in samples if sample["engine"] == engine and (sample.get("frontmost") or "unknown") == app),
            }
            for engine, app in sorted(
                {
                    (sample["engine"], sample.get("frontmost") or "unknown")
                    for sample in samples
                    if sample.get("frontmost") != baseline.get("frontmost")
                }
            )
        ],
        "observation_errors": errors,
        "focus_unchanged": bool(samples) and all(s.get("frontmost") == baseline.get("frontmost") for s in samples),
        "no_visible_browser_windows": baseline["windows"] == 0 and all(s["windows"] == 0 for s in samples),
        "scope": "real browser and adapter, intercepted fixture service responses",
        "not_verified": [
            "live Poe login/balance/update",
            "real OAuth/MFA/provider refusal",
            "Intel hardware",
            "typing target and Spaces",
        ],
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    assert not errors and result["focus_unchanged"] and result["no_visible_browser_windows"]
    return result


if __name__ == "__main__":
    fire.Fire(verify)
