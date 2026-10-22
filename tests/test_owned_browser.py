# this_file: tests/test_owned_browser.py
"""Poe unattended identity and session/tab ownership regressions."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from virginia_clemm_poe.browser_settings import BrowserSettings, browser_settings


def test_browser_settings_defaults_and_explicit_overrides(monkeypatch):
    for name in ("ENGINE", "PROFILE", "MODE", "EXECUTABLE_PATH"):
        monkeypatch.delenv(f"VCP_BROWSER_{name}", raising=False)
    assert browser_settings() == BrowserSettings()
    assert browser_settings().profile == "poe-primary"
    assert browser_settings().mode == "auto"
    monkeypatch.setenv("VCP_BROWSER_ENGINE", "firefox")
    assert browser_settings().engine == "firefox"
    assert browser_settings(engine="chromium").engine == "chromium"
    for options in ({"profile": "../other"}, {"mode": "hidden"}, {"engine": "safari"}):
        with pytest.raises(ValueError):
            browser_settings(**options)


@pytest.mark.asyncio
async def test_manager_serializes_start_and_returns_context_pages(monkeypatch):
    from virginia_clemm_poe.browser_manager import BrowserManager

    context = MagicMock(new_page=AsyncMock(side_effect=[MagicMock(), MagicMock()]))
    session = MagicMock(context=context, browser=MagicMock(), close=AsyncMock(), new_page=context.new_page)
    session.__aenter__ = AsyncMock(return_value=session)
    factory = MagicMock(return_value=session)
    monkeypatch.setattr("virginia_clemm_poe.browser_manager.AsyncBrowserSession", factory)
    manager = BrowserManager(settings=BrowserSettings(engine="chromium"))
    one, two = await asyncio.gather(manager.get_page(), manager.get_page())
    assert one is not two
    session.__aenter__.assert_awaited_once()
    assert factory.call_args.kwargs["profile"] == "poe-primary"
    assert factory.call_args.kwargs["mode"] == "auto"
    assert callable(factory.call_args.kwargs["auth_probe"])
    await manager.close()
    session.close.assert_awaited_once()
    context.close.assert_not_called()


@pytest.mark.asyncio
async def test_pool_tasks_share_session_and_failure_closes_only_its_tab(monkeypatch):
    from virginia_clemm_poe.browser_pool import BrowserPool

    pages = [MagicMock(close=AsyncMock(), wait_for_load_state=AsyncMock()) for _ in range(2)]
    session = MagicMock(context=MagicMock(new_page=AsyncMock(side_effect=pages)), browser=MagicMock())
    manager = MagicMock(get_session=AsyncMock(return_value=session), close=AsyncMock())
    monkeypatch.setattr("virginia_clemm_poe.browser_pool.BrowserManager", lambda **kwargs: manager)
    pool = BrowserPool(max_size=2)
    await pool.start()
    async with pool.acquire_page() as first:
        with pytest.raises(ValueError):
            async with pool.acquire_page() as second:
                assert first is not second
                raise ValueError("one task failed")
        first.close.assert_not_awaited()
        manager.close.assert_not_awaited()
    for page in pages:
        page.close.assert_awaited_once()
    await pool.stop()
    manager.close.assert_awaited_once()
    session.context.close.assert_not_called()


@pytest.mark.asyncio
async def test_pool_stop_cancellation_still_closes_its_session(monkeypatch):
    from virginia_clemm_poe.browser_pool import BrowserPool

    manager = MagicMock(close=AsyncMock())
    monkeypatch.setattr("virginia_clemm_poe.browser_pool.BrowserManager", lambda **kwargs: manager)
    pool = BrowserPool()
    started = asyncio.Event()

    async def wait_forever():
        started.set()
        await asyncio.Event().wait()

    pool._pool.append(MagicMock(close=AsyncMock(side_effect=wait_forever)))
    task = asyncio.create_task(pool.stop())
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    manager.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_global_pools_are_scoped_by_identity_and_close(monkeypatch):
    from virginia_clemm_poe.browser_pool import close_global_pool, get_global_pool

    monkeypatch.setattr("virginia_clemm_poe.browser_pool.BrowserManager", lambda **kwargs: MagicMock(close=AsyncMock()))
    first = BrowserSettings(profile="first")
    one = await get_global_pool(settings=first)
    try:
        assert await get_global_pool(settings=first) is one
        two = await get_global_pool(settings=BrowserSettings(profile="second"))
        assert two is not one
    finally:
        await close_global_pool()
    assert one._closed and two._closed


@pytest.mark.asyncio
async def test_missing_session_api_fails_explicitly_without_starting_ui(monkeypatch):
    from virginia_clemm_poe.browser_manager import BrowserManager
    from virginia_clemm_poe.exceptions import BrowserEngineUnavailable

    monkeypatch.setattr("virginia_clemm_poe.browser_manager.AsyncBrowserSession", None)
    with pytest.raises(BrowserEngineUnavailable) as error:
        await BrowserManager().get_session()
    assert error.value.code == "ENGINE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_auth_required_identifies_the_matching_login_command(monkeypatch):
    from playwrightauthor.session_errors import AuthenticationRequired

    from virginia_clemm_poe.browser_manager import BrowserManager
    from virginia_clemm_poe.exceptions import AuthenticationError

    session = MagicMock()
    session.__aenter__ = AsyncMock(side_effect=AuthenticationRequired("login required"))
    monkeypatch.setattr("virginia_clemm_poe.browser_manager.AsyncBrowserSession", lambda **kwargs: session)
    with pytest.raises(AuthenticationError) as error:
        await BrowserManager(settings=BrowserSettings(engine="firefox", profile="secondary")).get_session()
    assert error.value.code == "AUTH_REQUIRED"
    assert "--browser-profile=secondary" in error.value.command
    assert "--browser-engine=firefox" in error.value.command


@pytest.mark.asyncio
async def test_setup_checks_and_installs_chrome_without_opening_a_browser(monkeypatch, tmp_path):
    from virginia_clemm_poe.browser_manager import BrowserManager

    find = MagicMock(side_effect=[None, tmp_path / "chrome-testing"])
    install = MagicMock()
    monkeypatch.setattr("playwrightauthor.browser.finder.find_chrome_executable", find)
    monkeypatch.setattr("playwrightauthor.browser.installer.install_from_lkgv", install)
    assert await BrowserManager.setup_chrome() is True
    install.assert_called_once()
