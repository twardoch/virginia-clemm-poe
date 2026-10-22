# this_file: tests/test_browser_cli.py
"""Command settings reach the session API; unattended auth failures are structured."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from virginia_clemm_poe.__main__ import Cli


@pytest.fixture
def close_pools(monkeypatch):
    close = AsyncMock()
    monkeypatch.setattr("virginia_clemm_poe.browser_pool.close_global_pool", close)
    return close


def test_login_forwards_identity_and_uses_explicit_interactive_api(monkeypatch, close_pools):
    login = AsyncMock(return_value={"p-b": "fixture"})
    monkeypatch.setattr("virginia_clemm_poe.api.login_to_poe", login)
    Cli().login(browser_engine="firefox", browser_profile="secondary")
    selected = login.call_args.kwargs["settings"]
    assert selected.engine == "firefox" and selected.profile == "secondary"
    close_pools.assert_awaited_once()


def test_balance_forwards_headless_settings_and_does_not_login(monkeypatch, close_pools):
    balance = AsyncMock(return_value={"compute_points_available": 0})
    login = AsyncMock()
    monkeypatch.setattr("virginia_clemm_poe.api.get_account_balance", balance)
    monkeypatch.setattr("virginia_clemm_poe.api.login_to_poe", login)
    Cli().balance(browser_engine="chromium", browser_profile="other", browser_mode="headless")
    selected = balance.call_args.kwargs["settings"]
    assert selected.mode == "headless" and selected.profile == "other"
    login.assert_not_awaited()
    close_pools.assert_awaited_once()


def test_auth_failure_returns_code_and_nonzero_exit(monkeypatch, close_pools, capsys):
    from playwrightauthor.session_errors import AuthenticationRequired

    monkeypatch.setattr(
        "virginia_clemm_poe.api.get_account_balance",
        AsyncMock(side_effect=AuthenticationRequired("Sign in explicitly")),
    )
    with pytest.raises(SystemExit) as error:
        Cli().balance()
    assert error.value.code == 3
    assert "AUTH_REQUIRED" in capsys.readouterr().err
    close_pools.assert_awaited_once()


def test_update_passes_browser_settings_and_closes_pool(monkeypatch, close_pools):
    updater = MagicMock(update_all=AsyncMock())
    factory = MagicMock(return_value=updater)
    monkeypatch.setattr("virginia_clemm_poe.__main__.BotUpdater", factory)
    Cli().update(api_key="fixture", browser_engine="firefox", browser_profile="other")
    assert factory.call_args.kwargs["settings"].profile == "other"
    updater.update_all.assert_awaited_once()
    close_pools.assert_awaited_once()


def test_logout_clears_only_selected_http_identity(monkeypatch):
    manager = MagicMock()
    factory = MagicMock(return_value=manager)
    monkeypatch.setattr("virginia_clemm_poe.api.get_session_manager", factory)
    Cli().logout(browser_engine="firefox", browser_profile="secondary")
    selected = factory.call_args.args[0]
    assert selected.engine == "firefox" and selected.profile == "secondary"
    manager.clear_cookies.assert_called_once()


def test_login_timeout_has_actionable_nonempty_message(monkeypatch, close_pools, capsys):
    monkeypatch.setattr("virginia_clemm_poe.api.login_to_poe", AsyncMock(side_effect=TimeoutError()))
    with pytest.raises(SystemExit) as error:
        Cli().login()
    assert error.value.code == 1
    assert "timed out" in capsys.readouterr().err
    close_pools.assert_awaited_once()
