# this_file: tests/test_cookie_store.py
"""HTTP exports retain expiry/provenance and cannot silently overwrite account scope."""

import json
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from virginia_clemm_poe.poe_session import PoeSessionManager


@pytest.mark.asyncio
async def test_cookie_export_is_private_atomic_and_expired_values_are_excluded(tmp_path):
    manager = PoeSessionManager(cookies_dir=tmp_path)
    context = MagicMock(
        cookies=AsyncMock(
            return_value=[
                {"name": "p-b", "value": "fixture", "domain": ".poe.com", "expires": time.time() + 1000},
                {"name": "m-b", "value": "expired", "domain": ".poe.com", "expires": time.time() - 1},
                {"name": "m-uid", "value": "provider", "domain": ".google.com", "expires": -1},
            ]
        )
    )
    cookies = await manager.extract_cookies_from_browser(context)
    assert cookies == {"p-b": "fixture"}
    assert tmp_path.stat().st_mode & 0o777 == 0o700
    assert manager.cookies_path.stat().st_mode & 0o777 == 0o600
    data = json.loads(manager.cookies_path.read_text())
    assert data["cookie_metadata"]["p-b"]["domain"] == ".poe.com"
    assert data["provenance"]["source"] == "browser-context"
    reloaded = PoeSessionManager(cookies_dir=tmp_path)
    assert reloaded.cookies == cookies
    data["cookie_metadata"]["p-b"]["expires"] = time.time() - 1
    manager.cookies_path.write_text(json.dumps(data))
    assert not PoeSessionManager(cookies_dir=tmp_path).has_valid_cookies()


def test_cookie_save_failure_is_reported_without_destroying_previous_export(tmp_path, monkeypatch):
    manager = PoeSessionManager(cookies_dir=tmp_path)
    manager.cookies = {"p-b": "first"}
    manager._save_cookies()
    before = manager.cookies_path.read_bytes()
    monkeypatch.setattr("virginia_clemm_poe.private_store.os.replace", MagicMock(side_effect=PermissionError("denied")))
    manager.cookies = {"p-b": "second"}
    with pytest.raises(PermissionError):
        manager._save_cookies()
    assert manager.cookies_path.read_bytes() == before


def test_scoped_exports_and_cache_do_not_cross_account_identities(tmp_path):
    from virginia_clemm_poe.browser_settings import BrowserSettings

    first = PoeSessionManager(cookies_dir=tmp_path, settings=BrowserSettings(profile="first"))
    first.cookies = {"p-b": "first"}
    first._save_cookies()
    first._save_balance_cache({"compute_points_available": 123})
    second = PoeSessionManager(cookies_dir=tmp_path, settings=BrowserSettings(profile="second"))
    assert not second.cookies
    assert second._balance_cache is None


@pytest.mark.asyncio
async def test_cookie_extraction_never_redirects_an_oauth_page(tmp_path):
    from virginia_clemm_poe.exceptions import AuthenticationError

    manager = PoeSessionManager(cookies_dir=tmp_path)
    page = MagicMock(url="https://accounts.google.com/signin", goto=AsyncMock())
    with pytest.raises(AuthenticationError):
        await manager.extract_from_existing_playwright_session(page)
    page.goto.assert_not_awaited()


def test_new_export_invalidates_balance_from_previous_cookie_material(tmp_path):
    manager = PoeSessionManager(cookies_dir=tmp_path)
    manager._save_balance_cache({"compute_points_available": 321})
    manager.cookies = {"p-b": "new-login"}
    manager._save_cookies()
    assert manager._balance_cache is None
    assert not manager.balance_cache_path.exists()
