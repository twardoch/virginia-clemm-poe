# this_file: src/virginia_clemm_poe/balance_scraper.py

"""Scrape balance information directly from Poe web interface."""

import asyncio
from typing import Any, Optional

from loguru import logger
from playwright.async_api import Dialog, Page


async def scrape_balance_from_page(page: Page) -> dict[str, Any]:
    """Scrape balance information from an authenticated Poe page.
    
    Args:
        page: Playwright page that's already logged into Poe
        
    Returns:
        Dictionary with balance information
    """
    # Set up dialog handler to auto-dismiss error dialogs
    async def handle_dialog(dialog: Dialog) -> None:
        """Auto-dismiss any dialogs that appear during scraping."""
        logger.debug(f"Dialog appeared: {dialog.message}")
        await dialog.dismiss()
    
    # Add dialog handler
    page.on("dialog", handle_dialog)
    
    try:
        # Navigate to settings page where balance is shown
        logger.info("Navigating to Poe settings to get balance...")
        await page.goto("https://poe.com/settings", wait_until="networkidle")
        await asyncio.sleep(2)  # Let page fully load
        
        # Check if we're on the settings page
        current_url = page.url
        if "/login" in current_url:
            logger.warning("Redirected to login - session might be expired")
            return {"error": "Not authenticated"}
        
        balance_info = {}
        
        # Try to find compute points
        # Based on the actual HTML structure from Poe
        try:
            # Look for the specific element that contains the points value
            selectors = [
                # The exact class from the HTML you provided
                ".SettingsComputePointsSection_value__LY8w1",
                # Fallback selectors
                "[class*='SettingsComputePointsSection_value']",
                "[class*='value']:has-text(/[0-9,]+/)",
                # Look near "Available points" header
                "header:has-text('Available points') + div span",
                "span:has-text('Available points') ~ div span",
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            # Extract number from text (e.g., "999,933")
                            import re
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                points_str = numbers[0].replace(',', '')
                                try:
                                    points_val = int(points_str)
                                    # Sanity check
                                    if 0 <= points_val <= 10000000:
                                        balance_info['compute_points_available'] = points_val
                                        logger.info(f"Found compute points: {numbers[0]}")
                                        break
                                except:
                                    continue
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
        except Exception as e:
            logger.debug(f"Error finding compute points: {e}")
        
        # Try to find subscription status
        try:
            # Look for subscription indicators
            sub_selectors = [
                "text=/subscription.*active/i",
                "text=/premium/i",
                "text=/pro subscription/i",
                "*:has-text('Cancel subscription')",
                "*:has-text('Manage subscription')",
            ]
            
            for selector in sub_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        balance_info['subscription'] = {"isActive": True}
                        logger.info("Found active subscription")
                        break
                except:
                    continue
                    
            # If we didn't find subscription, mark as inactive
            if 'subscription' not in balance_info:
                balance_info['subscription'] = {"isActive": False}
                
        except Exception as e:
            logger.debug(f"Error finding subscription status: {e}")
        
        # Try alternative method - check page content via JavaScript
        if 'compute_points_available' not in balance_info:
            try:
                # Execute JavaScript to get page text and search for patterns
                page_text = await page.evaluate("() => document.body.innerText")
                
                # Log a sample of the page text for debugging
                logger.debug(f"Page text sample (first 500 chars): {page_text[:500]}")
                
                # Look for various patterns that might indicate compute points
                import re
                patterns = [
                    r'([\d,]+)\s*(?:compute\s*)?points?\s*(?:available|remaining)?',
                    r'(?:compute\s*points|points)[\s:]+([0-9,]+)',
                    r'([0-9,]+)(?:\s*/\s*[0-9,]+)?\s*points',
                    r'balance[\s:]+([0-9,]+)',
                    r'([0-9,]+)\s*(?:remaining|left)',
                ]
                
                for pattern in patterns:
                    points_match = re.search(pattern, page_text, re.IGNORECASE)
                    if points_match:
                        points_str = points_match.group(1).replace(',', '')
                        try:
                            points_val = int(points_str)
                            # Sanity check - points should be reasonable
                            if 0 <= points_val <= 10000000:
                                balance_info['compute_points_available'] = points_val
                                logger.info(f"Found compute points via pattern '{pattern}': {points_match.group(1)}")
                                break
                        except:
                            continue
                    
                # Check for subscription keywords
                if 'premium' in page_text.lower() or 'subscription' in page_text.lower():
                    if 'cancel' in page_text.lower() or 'manage subscription' in page_text.lower():
                        balance_info['subscription'] = {"isActive": True}
                        logger.info("Detected active subscription from page text")
                        
            except Exception as e:
                logger.debug(f"Error evaluating page text: {e}")
        
        # Add timestamp
        from datetime import datetime
        balance_info['timestamp'] = datetime.utcnow().isoformat()
        
        return balance_info
        
    except Exception as e:
        logger.error(f"Error scraping balance: {e}")
        return {"error": str(e)}
    finally:
        # Remove dialog handler
        try:
            page.remove_listener("dialog", handle_dialog)
        except:
            pass


async def get_balance_with_browser(page: Page) -> dict[str, Any]:
    """Get balance using an authenticated browser page.
    
    This is more reliable than the API method as it works with the actual
    web interface that the user sees.
    
    Args:
        page: Authenticated Playwright page
        
    Returns:
        Balance information dictionary
    """
    try:
        result = await scrape_balance_from_page(page)
        
        # Add graceful wait before returning to allow JS cleanup
        logger.debug("Waiting for page JavaScript to settle...")
        await page.wait_for_load_state("networkidle", timeout=5000)
        await asyncio.sleep(0.5)  # Small delay for async operations to complete
        
        return result
    except Exception as e:
        logger.error(f"Browser balance scraping failed: {e}")
        return {"error": str(e)}