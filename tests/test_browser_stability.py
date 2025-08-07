# this_file: tests/test_browser_stability.py
"""Integration tests for browser stability improvements."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import Dialog

from virginia_clemm_poe.browser_pool import BrowserConnection, BrowserPool


class TestBrowserPoolStability:
    """Test browser pool stability improvements."""
    
    @pytest.mark.asyncio
    async def test_graceful_page_close(self):
        """Test that pages are closed gracefully with network wait."""
        pool = BrowserPool(max_size=1)
        
        mock_page = MagicMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.on = MagicMock()
        
        with patch("asyncio.sleep") as mock_sleep:
            await pool._close_page_safely(mock_page)
            
            # Verify graceful shutdown sequence
            mock_page.on.assert_called_once()
            assert mock_page.on.call_args[0][0] == "dialog"
            mock_page.wait_for_load_state.assert_called_with("networkidle", timeout=3000)
            mock_sleep.assert_called_with(0.3)
            mock_page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connection_close_with_context_cleanup(self):
        """Test that browser connections close contexts properly."""
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_manager = MagicMock()
        mock_manager.close = AsyncMock()
        
        # Create mock pages
        mock_page1 = MagicMock()
        mock_page1.wait_for_load_state = AsyncMock()
        mock_page1.on = MagicMock()
        
        mock_page2 = MagicMock()
        mock_page2.wait_for_load_state = AsyncMock()
        mock_page2.on = MagicMock()
        
        mock_context.pages = [mock_page1, mock_page2]
        mock_context.close = AsyncMock()
        
        connection = BrowserConnection(mock_browser, mock_context, mock_manager)
        
        with patch("asyncio.sleep") as mock_sleep:
            await connection.close()
            
            # Verify all pages got dialog handlers
            mock_page1.on.assert_called()
            mock_page2.on.assert_called()
            
            # Verify wait for network settle on all pages
            mock_page1.wait_for_load_state.assert_called_with("networkidle", timeout=2000)
            mock_page2.wait_for_load_state.assert_called_with("networkidle", timeout=2000)
            
            # Verify delay before context close
            mock_sleep.assert_called_with(0.5)
            
            # Verify context and manager closed
            mock_context.close.assert_called_once()
            mock_manager.close.assert_called_once()
            
            # Verify connection marked unhealthy
            assert connection.is_healthy is False
    
    @pytest.mark.asyncio
    async def test_dialog_auto_dismiss(self):
        """Test that dialogs are automatically dismissed."""
        pool = BrowserPool(max_size=1)
        
        mock_page = MagicMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.on = MagicMock()
        
        await pool._close_page_safely(mock_page)
        
        # Get the dialog handler that was registered
        dialog_handler = mock_page.on.call_args[0][1]
        
        # Test that it dismisses dialogs
        mock_dialog = MagicMock()
        mock_dialog.dismiss = AsyncMock()
        mock_dialog.message = "Something went wrong"
        
        await dialog_handler(mock_dialog)
        mock_dialog.dismiss.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_with_error_resilience(self):
        """Test that cleanup continues even if some operations fail."""
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_manager = MagicMock()
        mock_manager.close = AsyncMock()
        
        # Create mock page that fails on wait_for_load_state
        mock_page = MagicMock()
        mock_page.wait_for_load_state = AsyncMock(side_effect=Exception("Network error"))
        mock_page.on = MagicMock()
        
        mock_context.pages = [mock_page]
        mock_context.close = AsyncMock()
        
        connection = BrowserConnection(mock_browser, mock_context, mock_manager)
        
        # Should not raise exception despite page error
        await connection.close()
        
        # Verify cleanup continued despite error
        mock_context.close.assert_called_once()
        mock_manager.close.assert_called_once()
        assert connection.is_healthy is False


class TestBrowserStabilityIntegration:
    """Integration tests for overall browser stability."""
    
    @pytest.mark.asyncio
    async def test_multiple_balance_checks_no_dialogs(self):
        """Test that multiple consecutive balance checks don't produce error dialogs."""
        from virginia_clemm_poe.balance_scraper import scrape_balance_from_page
        
        # Simulate multiple balance checks
        for i in range(5):
            mock_page = MagicMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.query_selector = AsyncMock(return_value=None)
            mock_page.evaluate = AsyncMock(return_value=f"{1000 + i} points")
            mock_page.url = "https://poe.com/settings"
            mock_page.on = MagicMock()
            mock_page.remove_listener = MagicMock()
            
            dialog_count = 0
            
            async def count_dialogs(dialog):
                nonlocal dialog_count
                dialog_count += 1
                await dialog.dismiss()
            
            # Replace dialog handler to count calls
            def mock_on(event, handler):
                if event == "dialog":
                    mock_page._dialog_handler = handler
            
            mock_page.on = mock_on
            
            result = await scrape_balance_from_page(mock_page)
            
            # Verify balance was scraped
            assert result.get("compute_points_available") == 1000 + i
            
            # Verify dialog handler was installed
            assert hasattr(mock_page, "_dialog_handler")
            
            # Simulate a dialog appearing (should be auto-dismissed)
            mock_dialog = MagicMock()
            mock_dialog.dismiss = AsyncMock()
            mock_dialog.message = "Error dialog"
            await mock_page._dialog_handler(mock_dialog)
            mock_dialog.dismiss.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pool_cleanup_sequence(self):
        """Test that browser pool cleanup follows proper sequence."""
        pool = BrowserPool(max_size=2)
        
        # Mock connections
        conn1 = MagicMock()
        conn1.close = AsyncMock()
        conn1.is_healthy = True
        conn1.age_seconds = lambda: 10
        
        conn2 = MagicMock()
        conn2.close = AsyncMock()
        conn2.is_healthy = False
        conn2.age_seconds = lambda: 20
        
        pool._pool.append(conn1)
        pool._pool.append(conn2)
        
        await pool.stop()
        
        # Verify both connections were closed
        conn1.close.assert_called_once()
        conn2.close.assert_called_once()
        
        # Verify pool is marked closed
        assert pool._closed is True


class TestErrorRecovery:
    """Test error recovery mechanisms."""
    
    @pytest.mark.asyncio
    async def test_page_close_timeout_recovery(self):
        """Test recovery when page close times out."""
        pool = BrowserPool(max_size=1)
        
        mock_page = MagicMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.close = AsyncMock(side_effect=asyncio.TimeoutError("Close timeout"))
        mock_page.on = MagicMock()
        
        # Should handle timeout gracefully
        await pool._close_page_safely(mock_page)
        
        # Verify close was attempted
        mock_page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_close_error_recovery(self):
        """Test recovery when context close fails."""
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_manager = MagicMock()
        mock_manager.close = AsyncMock()
        
        mock_context.pages = []
        mock_context.close = AsyncMock(side_effect=Exception("Context close error"))
        
        connection = BrowserConnection(mock_browser, mock_context, mock_manager)
        
        # Should not raise exception
        await connection.close()
        
        # Verify manager close was still called
        mock_manager.close.assert_called_once()
        assert connection.is_healthy is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])