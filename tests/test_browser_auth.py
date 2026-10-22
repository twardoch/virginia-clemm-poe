# this_file: tests/test_browser_auth.py
"""Authorization never depends on a cookie name or navigates an active login tab."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from virginia_clemm_poe.browser_auth import page_is_signed_in, probe_poe_context, wait_for_poe_login


def page_at(url="https://poe.com/settings", signed_in=True):
    page = MagicMock(url=url, close=AsyncMock())
    marker = MagicMock(
        is_visible=AsyncMock(return_value=signed_in), wait_for=AsyncMock(), text_content=AsyncMock(return_value="1,234")
    )
    marker.first = marker
    page.locator.return_value = marker
    refusal = MagicMock(is_visible=AsyncMock(return_value=False))
    refusal.first = refusal
    page.get_by_text.return_value = refusal
    page.goto = AsyncMock(return_value=MagicMock(status=200))
    page.is_closed.return_value = False
    return page


@pytest.mark.asyncio
async def test_probe_requires_settings_response_and_account_marker():
    page = page_at()
    context = MagicMock(new_page=AsyncMock(return_value=page))
    assert await probe_poe_context(context) is True
    page.close.assert_awaited_once()
    page.goto.assert_awaited_once()
    page.url = "https://poe.com/login"
    assert await probe_poe_context(context) is False
    assert await page_is_signed_in(page) is False
    page.url = "https://poe.com.attacker.test/settings"
    assert await page_is_signed_in(page) is False


@pytest.mark.asyncio
async def test_login_wait_does_not_navigate_an_oauth_popup(monkeypatch):
    login = page_at("https://poe.com/login", False)
    oauth = page_at("https://accounts.google.com/signin", False)
    authenticated = page_at("https://poe.com/", True)
    login.context.pages = [login, oauth, authenticated]
    monkeypatch.setattr("virginia_clemm_poe.browser_auth.probe_poe_context", AsyncMock(return_value=True))
    await wait_for_poe_login(login, timeout_seconds=1)
    login.goto.assert_not_awaited()
    oauth.goto.assert_not_awaited()
    authenticated.goto.assert_not_awaited()


@pytest.mark.asyncio
async def test_login_timeout_is_bounded_and_does_not_navigate():
    page = page_at("https://poe.com/login", False)
    page.context.pages = [page]
    with pytest.raises(TimeoutError):
        await wait_for_poe_login(page, timeout_seconds=0.01)
    page.goto.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_login_never_exports_or_repeatedly_navigates(monkeypatch):
    from virginia_clemm_poe.api import login_to_poe

    page = page_at("https://poe.com/login", False)
    manager = MagicMock(extract_cookies_from_browser=AsyncMock())
    monkeypatch.setattr("virginia_clemm_poe.api.get_session_manager", lambda settings: manager)
    monkeypatch.setattr("virginia_clemm_poe.browser_auth.probe_poe_context", AsyncMock(return_value=False))
    monkeypatch.setattr(
        "virginia_clemm_poe.browser_auth.wait_for_poe_login", AsyncMock(side_effect=TimeoutError("expired"))
    )
    with pytest.raises(TimeoutError):
        await login_to_poe(page=page)
    page.goto.assert_awaited_once()
    manager.extract_cookies_from_browser.assert_not_awaited()


@pytest.mark.asyncio
async def test_provider_refusal_is_distinct_and_does_not_navigate():
    from virginia_clemm_poe.browser_auth import ProviderRejected

    page = page_at("https://poe.com/login", False)
    provider = page_at("https://accounts.google.com/signin", False)
    provider.get_by_text.return_value.is_visible.return_value = True
    page.context.pages = [page, provider]
    with pytest.raises(ProviderRejected) as error:
        await wait_for_poe_login(page, timeout_seconds=1)
    assert error.value.code == "AUTH_REJECTED_BY_PROVIDER"
    provider.goto.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text,expected",
    [("", False), (",", False), ("unknown", False), ("points", False), (" ", False), ("0", True), ("12,345", True)],
)
async def test_probe_requires_a_numeric_points_value(text, expected):
    page = page_at()
    page.locator.return_value.text_content.return_value = text
    context = MagicMock(new_page=AsyncMock(return_value=page))
    assert await probe_poe_context(context) is expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("1,234,567available", 1234567),
        ("0 available", 0),
        ("12,345", 12345),
        ("$150.41 value", None),
        (",available", None),
    ],
)
def test_parse_points_supports_current_and_legacy_account_rows(text, expected):
    from virginia_clemm_poe.browser_auth import parse_points_value

    assert parse_points_value(text) == expected


@pytest.mark.asyncio
async def test_probe_uses_subscription_tab_url_and_current_points_row():
    page = page_at()
    page.locator.return_value.text_content.return_value = "1,234,567available"
    context = MagicMock(new_page=AsyncMock(return_value=page))
    assert await probe_poe_context(context) is True
    assert page.goto.call_args.args[0] == "https://poe.com/settings?tab=subscription"
    assert "SettingsComputePointsSection_inlinePointsRow" in page.locator.call_args.args[0]


@pytest.mark.asyncio
async def test_login_recognizes_current_settings_tab_before_fresh_probe(monkeypatch):
    page = page_at("https://poe.com/settings", False)
    tab = MagicMock(is_visible=AsyncMock(return_value=True))
    page.get_by_role.return_value = tab
    page.context.pages = [page]
    probe = AsyncMock(return_value=True)
    monkeypatch.setattr("virginia_clemm_poe.browser_auth.probe_poe_context", probe)
    await wait_for_poe_login(page, timeout_seconds=1)
    probe.assert_awaited_once_with(page.context)
    page.get_by_role.assert_called_with("tab", name="Subscription and points", exact=True)
    page.goto.assert_not_awaited()
