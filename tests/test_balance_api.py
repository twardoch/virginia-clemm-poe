# this_file: tests/test_balance_api.py
"""Tests for balance API methods including GraphQL and fallback chain."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from playwright.async_api import Dialog

from virginia_clemm_poe.exceptions import APIError, AuthenticationError
from virginia_clemm_poe.poe_session import PoeSessionManager


@pytest.fixture
def session_manager(tmp_path):
    """Create a session manager with temporary directory."""
    return PoeSessionManager(cookies_dir=tmp_path)


@pytest.fixture
def mock_cookies():
    """Sample cookies for testing."""
    return {
        "m-b": "test_mb_cookie",
        "p-b": "test_pb_cookie", 
        "p-lat": "test_plat_cookie",
        "__cf_bm": "test_cf_bm",
        "cf_clearance": "test_cf_clearance"
    }


class TestCookieExtraction:
    """Test cookie extraction improvements."""
    
    @pytest.mark.asyncio
    async def test_extract_cookies_with_mb(self, session_manager):
        """Test that m-b cookie is properly extracted."""
        mock_context = MagicMock()
        mock_context.cookies = AsyncMock(return_value=[
            {"name": "m-b", "value": "test_mb", "domain": ".poe.com"},
            {"name": "p-b", "value": "test_pb", "domain": ".poe.com"},
            {"name": "p-lat", "value": "test_plat", "domain": ".poe.com"}
        ])
        
        cookies = await session_manager.extract_cookies_from_browser(mock_context)
        
        assert "m-b" in cookies
        assert cookies["m-b"] == "test_mb"
        assert "p-b" in cookies
        assert "p-lat" in cookies
    
    @pytest.mark.asyncio
    async def test_extract_cookies_validates_essential(self, session_manager):
        """Test that extraction validates essential cookies."""
        mock_context = MagicMock()
        mock_context.cookies = AsyncMock(return_value=[
            {"name": "unrelated", "value": "test", "domain": ".poe.com"}
        ])
        
        with pytest.raises(AuthenticationError, match="Missing essential Poe cookies"):
            await session_manager.extract_cookies_from_browser(mock_context)
    
    def test_has_valid_cookies_with_mb(self, session_manager, mock_cookies):
        """Test that m-b cookie is recognized as valid."""
        session_manager.cookies = {"m-b": "test_mb"}
        assert session_manager.has_valid_cookies() is True
        
        session_manager.cookies = {"p-b": "test_pb"}
        assert session_manager.has_valid_cookies() is True
        
        session_manager.cookies = {"p-lat": "test_plat"}
        assert session_manager.has_valid_cookies() is False


class TestGraphQLBalance:
    """Test GraphQL balance retrieval method."""
    
    @pytest.mark.asyncio
    async def test_graphql_success(self, session_manager, mock_cookies):
        """Test successful GraphQL balance query."""
        session_manager.cookies = mock_cookies
        
        mock_response = {
            "data": {
                "viewer": {
                    "messagePointInfo": {
                        "messagePointBalance": 1000,
                        "monthlyQuota": 5000
                    },
                    "subscription": {
                        "isActive": True,
                        "expiresAt": "2024-12-31"
                    }
                }
            }
        }
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = AsyncMock(
                raise_for_status=AsyncMock(),
                json=lambda: mock_response,
                status_code=200
            )
            
            result = await session_manager._get_balance_via_graphql()
            
            assert result["compute_points_available"] == 1000
            assert result["monthly_quota"] == 5000
            assert result["subscription"]["isActive"] is True
            
            # Verify GraphQL query was sent
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "SettingsPageQuery" in call_args[1]["json"]["query"]
    
    @pytest.mark.asyncio
    async def test_graphql_auth_error(self, session_manager, mock_cookies):
        """Test GraphQL authentication error handling."""
        session_manager.cookies = mock_cookies
        
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = AsyncMock(
                raise_for_status=AsyncMock(
                    side_effect=httpx.HTTPStatusError(
                        "401", request=MagicMock(), response=MagicMock(status_code=401)
                    )
                )
            )
            
            with pytest.raises(AuthenticationError, match="GraphQL: Cookies expired"):
                await session_manager._get_balance_via_graphql()


class TestFallbackChain:
    """Test the fallback chain for balance retrieval."""
    
    @pytest.mark.asyncio
    async def test_fallback_from_graphql_to_direct(self, session_manager, mock_cookies):
        """Test fallback from GraphQL to direct API."""
        session_manager.cookies = mock_cookies
        
        # GraphQL fails
        with patch.object(session_manager, "_get_balance_via_graphql") as mock_graphql:
            mock_graphql.side_effect = APIError("GraphQL failed")
            
            # Direct API succeeds
            with patch.object(session_manager, "_get_balance_via_direct_api") as mock_direct:
                mock_direct.return_value = {
                    "compute_points_available": 500,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                result = await session_manager._get_balance_via_cookies()
                
                assert result["compute_points_available"] == 500
                mock_graphql.assert_called_once()
                mock_direct.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fallback_to_browser_scraping(self, session_manager, mock_cookies):
        """Test fallback to browser scraping when API methods fail."""
        session_manager.cookies = mock_cookies
        
        # Mock page for browser scraping
        mock_page = MagicMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.evaluate = AsyncMock(return_value="1,234 points available")
        mock_page.url = "https://poe.com/settings"
        
        # API methods fail
        with patch.object(session_manager, "_get_balance_via_cookies") as mock_api:
            mock_api.side_effect = APIError("All API methods failed")
            
            # Browser scraping succeeds
            with patch("virginia_clemm_poe.poe_session.get_balance_with_browser") as mock_scraper:
                mock_scraper.return_value = {
                    "compute_points_available": 1234,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                result = await session_manager.get_account_balance(page=mock_page)
                
                assert result["compute_points_available"] == 1234
                mock_scraper.assert_called_once_with(mock_page)
    
    @pytest.mark.asyncio 
    async def test_cache_usage(self, session_manager):
        """Test that cache is used when available."""
        cached_data = {
            "compute_points_available": 999,
            "timestamp": datetime.utcnow().isoformat()
        }
        session_manager._balance_cache = cached_data
        
        result = await session_manager.get_account_balance(use_cache=True)
        assert result == cached_data
        
        # Force refresh should bypass cache
        with patch.object(session_manager, "_get_balance_via_cookies") as mock_api:
            mock_api.return_value = {"compute_points_available": 777}
            
            result = await session_manager.get_account_balance(force_refresh=True)
            assert result["compute_points_available"] == 777
            mock_api.assert_called_once()


class TestBrowserDialogSuppression:
    """Test browser dialog suppression during balance scraping."""
    
    @pytest.mark.asyncio
    async def test_dialog_handler_added(self):
        """Test that dialog handler is added during scraping."""
        from virginia_clemm_poe.balance_scraper import scrape_balance_from_page
        
        mock_page = MagicMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.evaluate = AsyncMock(return_value="No balance found")
        mock_page.url = "https://poe.com/settings"
        mock_page.on = MagicMock()
        mock_page.remove_listener = MagicMock()
        
        await scrape_balance_from_page(mock_page)
        
        # Verify dialog handler was added
        mock_page.on.assert_called()
        call_args = mock_page.on.call_args
        assert call_args[0][0] == "dialog"
        
        # Verify handler function dismisses dialogs
        handler_func = call_args[0][1]
        mock_dialog = MagicMock()
        mock_dialog.dismiss = AsyncMock()
        mock_dialog.message = "Test error"
        await handler_func(mock_dialog)
        mock_dialog.dismiss.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_graceful_wait_before_close(self):
        """Test that graceful wait is added before closing."""
        from virginia_clemm_poe.balance_scraper import get_balance_with_browser
        
        mock_page = MagicMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.evaluate = AsyncMock(return_value="1000 points")
        mock_page.url = "https://poe.com/settings"
        mock_page.on = MagicMock()
        mock_page.remove_listener = MagicMock()
        
        with patch("asyncio.sleep") as mock_sleep:
            result = await get_balance_with_browser(mock_page)
            
            # Verify wait_for_load_state was called
            assert mock_page.wait_for_load_state.call_count >= 2
            
            # Verify sleep was called for graceful shutdown
            mock_sleep.assert_called()


class TestRetryLogic:
    """Test retry logic with exponential backoff."""
    
    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self, session_manager, mock_cookies):
        """Test that transient failures are retried."""
        session_manager.cookies = mock_cookies
        
        call_count = 0
        
        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count < 3:
                # Fail first 2 attempts
                raise httpx.RequestError("Connection error")
            
            # Succeed on 3rd attempt
            return AsyncMock(
                raise_for_status=AsyncMock(),
                json=lambda: {
                    "data": {
                        "viewer": {
                            "messagePointInfo": {"messagePointBalance": 100},
                            "subscription": {"isActive": False}
                        }
                    }
                },
                status_code=200
            )
        
        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            with patch("asyncio.sleep"):  # Skip actual delays in test
                result = await session_manager._get_balance_via_graphql()
                
                assert result["compute_points_available"] == 100
                assert call_count == 3  # Verify it retried


if __name__ == "__main__":
    pytest.main([__file__, "-v"])