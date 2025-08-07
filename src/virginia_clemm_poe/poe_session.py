# this_file: src/virginia_clemm_poe/poe_session.py

"""Poe session management with cookie extraction and balance checking."""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import httpx
from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page

from .config import POE_BASE_URL
from .exceptions import APIError, AuthenticationError
from .utils.paths import get_data_dir
from .utils.timeout import with_retries


class PoeSessionManager:
    """Manages Poe session cookies and account balance checking."""

    COOKIES_FILE = "poe_cookies.json"
    BALANCE_CACHE_FILE = "balance_cache.json"
    POE_SETTINGS_URL = "https://www.quora.com/poe_api/settings"
    POE_LOGIN_URL = "https://poe.com/login"
    BALANCE_CACHE_DURATION_MINUTES = 5  # Cache balance for 5 minutes
    
    def __init__(self, cookies_dir: Optional[Path] = None):
        """Initialize session manager with optional custom cookies directory."""
        self.cookies_dir = cookies_dir or get_data_dir() / "cookies"
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_path = self.cookies_dir / self.COOKIES_FILE
        self.balance_cache_path = self.cookies_dir / self.BALANCE_CACHE_FILE
        self.cookies: dict[str, Any] = {}
        self._load_cookies()
        self._balance_cache: Optional[dict[str, Any]] = None
        self._load_balance_cache()
    
    def _load_cookies(self) -> None:
        """Load cookies from disk if available."""
        if self.cookies_path.exists():
            try:
                with open(self.cookies_path) as f:
                    data = json.load(f)
                    self.cookies = data.get("cookies", {})
                    saved_at = data.get("saved_at")
                    if saved_at:
                        logger.debug(f"Loaded Poe cookies saved at {saved_at}")
            except Exception as e:
                logger.warning(f"Failed to load cookies: {e}")
                self.cookies = {}
    
    def _save_cookies(self) -> None:
        """Save cookies to disk."""
        try:
            data = {
                "cookies": self.cookies,
                "saved_at": datetime.utcnow().isoformat()
            }
            with open(self.cookies_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved Poe cookies to {self.cookies_path}")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
    
    def _load_balance_cache(self) -> None:
        """Load cached balance data from disk if available and not expired."""
        if self.balance_cache_path.exists():
            try:
                with open(self.balance_cache_path) as f:
                    cache_data = json.load(f)
                    
                # Check if cache is expired
                cached_at = cache_data.get("cached_at")
                if cached_at:
                    cache_time = datetime.fromisoformat(cached_at)
                    if datetime.utcnow() - cache_time < timedelta(minutes=self.BALANCE_CACHE_DURATION_MINUTES):
                        self._balance_cache = cache_data.get("balance")
                        logger.debug(f"Loaded cached balance from {cached_at}")
                    else:
                        logger.debug("Balance cache expired")
                        self._balance_cache = None
            except Exception as e:
                logger.warning(f"Failed to load balance cache: {e}")
                self._balance_cache = None
    
    def _save_balance_cache(self, balance_data: dict[str, Any]) -> None:
        """Save balance data to cache."""
        try:
            cache_data = {
                "balance": balance_data,
                "cached_at": datetime.utcnow().isoformat()
            }
            with open(self.balance_cache_path, "w") as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Saved balance cache to {self.balance_cache_path}")
        except Exception as e:
            logger.error(f"Failed to save balance cache: {e}")
    
    async def extract_cookies_from_browser(self, context: BrowserContext) -> dict[str, str]:
        """Extract Poe session cookies from browser context.
        
        Args:
            context: Playwright browser context with active Poe session
            
        Returns:
            Dictionary with essential Poe cookies (p-b, p-lat, m-b, etc.)
        """
        try:
            # Get cookies from all relevant URLs
            # Poe uses both poe.com and quora.com domains
            all_cookies = []
            
            # Get cookies from multiple URLs to ensure we get all domains
            for url in ["https://poe.com", "https://www.poe.com", "https://quora.com", "https://www.quora.com"]:
                try:
                    url_cookies = await context.cookies(url)
                    all_cookies.extend(url_cookies)
                    logger.debug(f"Got {len(url_cookies)} cookies from {url}")
                except Exception as e:
                    logger.debug(f"Could not get cookies from {url}: {e}")
            
            # Filter for Poe-related cookies
            poe_cookies = {}
            # m-b is the main cookie for internal API, p-b for external
            essential_cookies = ["m-b", "p-b", "p-lat", "__cf_bm", "cf_clearance"]
            optional_cookies = ["poe-formkey", "__stripe_mid", "__stripe_sid", "m-lat", "m-uid"]
            all_wanted = essential_cookies + optional_cookies
            
            # Look for cookies by name, regardless of domain
            for cookie in all_cookies:
                name = cookie.get("name", "")
                if name in all_wanted:
                    # Don't duplicate cookies
                    if name not in poe_cookies:
                        poe_cookies[name] = cookie["value"]
                        logger.debug(f"Extracted cookie: {name} from domain {cookie.get('domain', 'unknown')}")
            
            # Also check for any cookie that starts with 'p-' or 'm-'
            for cookie in all_cookies:
                name = cookie.get("name", "")
                if (name.startswith("p-") or name.startswith("m-")) and name not in poe_cookies:
                    poe_cookies[name] = cookie["value"]
                    logger.debug(f"Extracted additional cookie: {name}")
            
            # Validate we have minimum required cookies
            # We need either m-b (for internal API) or p-b (for external API)
            if "m-b" in poe_cookies or "p-b" in poe_cookies:
                logger.info(f"Successfully extracted {len(poe_cookies)} Poe cookies")
                if "m-b" in poe_cookies:
                    logger.debug("Found m-b cookie for internal API access")
                if "p-b" in poe_cookies:
                    logger.debug("Found p-b cookie for external API access")
                self.cookies = poe_cookies
                self._save_cookies()
                return poe_cookies
            else:
                # Log what we did find for debugging
                logger.warning(f"Missing essential cookies. Found: {list(poe_cookies.keys())}")
                logger.debug(f"All cookie names seen: {[c.get('name') for c in all_cookies]}")
                raise AuthenticationError("Missing essential Poe cookies (m-b or p-b)")
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Failed to extract cookies: {e}")
            raise
    
    async def login_with_browser(self, browser: Browser) -> dict[str, str]:
        """Open Poe login page and wait for user to log in.
        
        Args:
            browser: Playwright browser instance (preferably from PlaywrightAuthor)
            
        Returns:
            Extracted cookies after successful login
        """
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            logger.info("Opening Poe login page...")
            await page.goto(self.POE_LOGIN_URL)
            
            # Wait for user to log in (detect by looking for logged-in indicators)
            logger.info("Please log in to Poe.com in the browser window...")
            
            # Wait for successful login (check for specific elements that appear when logged in)
            await page.wait_for_selector(
                "button[aria-label='User menu']",  # User menu button appears when logged in
                timeout=300000  # 5 minute timeout for login
            )
            
            logger.info("Login detected, extracting cookies...")
            cookies = await self.extract_cookies_from_browser(context)
            
            return cookies
            
        finally:
            await context.close()
    
    async def extract_from_existing_playwright_session(self, page: Page) -> dict[str, str]:
        """Extract cookies from an existing PlaywrightAuthor browser session.
        
        Args:
            page: Active Playwright page from PlaywrightAuthor session
            
        Returns:
            Extracted Poe cookies
        """
        # Navigate to Poe if not already there
        current_url = page.url
        if "poe.com" not in current_url:
            logger.info("Navigating to Poe.com to extract cookies...")
            await page.goto("https://poe.com")
            await page.wait_for_load_state("networkidle")
        
        # Extract cookies from the browser context
        context = page.context
        return await self.extract_cookies_from_browser(context)
    
    async def get_account_balance(self, use_api_key: bool = False, api_key: Optional[str] = None, page: Optional[Page] = None, use_cache: bool = True, force_refresh: bool = False) -> dict[str, Any]:
        """Get account balance and settings using multiple methods with fallback.
        
        Tries methods in this order:
        1. Cached data (if not expired and not force_refresh)
        2. API key method (if provided)
        3. GraphQL query with cookies (most reliable)
        4. Direct API endpoint with cookies
        5. Browser scraping (most robust but slowest)
        
        Args:
            use_api_key: If True, try to use API key first (faster but limited info)
            api_key: Optional API key for basic balance check
            page: Optional authenticated Playwright page for scraping
            use_cache: If True, return cached balance if available and not expired
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            Dictionary with account settings including compute points balance
        """
        # Check cache first if allowed
        if use_cache and not force_refresh and self._balance_cache:
            logger.info("Using cached balance data")
            return self._balance_cache
        
        errors = []  # Collect errors for debugging
        
        # Try API key method first if requested
        if use_api_key and api_key:
            try:
                result = await self._get_balance_via_api(api_key)
                if result.get("compute_points_available") is not None:
                    self._save_balance_cache(result)
                    return result
            except Exception as e:
                errors.append(f"API key: {e}")
                logger.debug(f"API key method failed: {e}")
        
        # Try cookie-based methods if we have cookies
        if self.cookies:
            try:
                result = await self._get_balance_via_cookies()
                # If we got real data, save to cache and return it
                if result.get("compute_points_available") is not None:
                    self._save_balance_cache(result)
                    logger.info("Successfully got balance via API")
                    return result
            except AuthenticationError:
                # Re-raise auth errors immediately
                raise
            except Exception as e:
                errors.append(f"Cookie API: {e}")
                logger.debug(f"Cookie-based API methods failed: {e}")
        
        # If we have a page, try scraping as last resort
        if page:
            logger.info("Falling back to browser scraping for balance...")
            try:
                from .balance_scraper import get_balance_with_browser
                result = await get_balance_with_browser(page)
                if result.get("compute_points_available") is not None:
                    self._save_balance_cache(result)
                    logger.info("Successfully got balance via browser scraping")
                return result
            except Exception as e:
                errors.append(f"Browser scraping: {e}")
                logger.error(f"Browser scraping failed: {e}")
        
        # If all methods failed, provide helpful error
        if not self.cookies and not api_key:
            raise AuthenticationError("No authentication available. Please login first with --login flag.")
        
        # Return empty result with error info
        logger.warning(f"All balance retrieval methods failed. Errors: {errors}")
        return {
            "compute_points_available": None,
            "error": "Failed to retrieve balance",
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_balance_via_cookies(self) -> dict[str, Any]:
        """Get balance using session cookies (internal API)."""
        if not self.cookies:
            raise AuthenticationError("No cookies available")
        
        # Try GraphQL method first if we have m-b cookie
        if "m-b" in self.cookies:
            try:
                return await self._get_balance_via_graphql()
            except Exception as e:
                logger.debug(f"GraphQL method failed, falling back to direct API: {e}")
        
        # Fall back to direct API method
        return await self._get_balance_via_direct_api()
    
    async def _get_balance_via_graphql(self) -> dict[str, Any]:
        """Get balance using GraphQL query (most reliable method)."""
        if not self.cookies:
            raise AuthenticationError("No cookies available")
        
        # GraphQL query for settings
        SETTINGS_QUERY = """
        query SettingsPageQuery {
            viewer {
                messagePointInfo {
                    messagePointBalance
                    monthlyQuota
                }
                subscription {
                    isActive
                    expiresAt
                }
            }
        }
        """
        
        # Build cookie header
        cookie_header = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
        
        headers = {
            "Cookie": cookie_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Origin": "https://poe.com",
            "Referer": "https://poe.com/settings",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        # GraphQL endpoint
        graphql_url = "https://poe.com/api/gql_POST"
        
        payload = {
            "query": SETTINGS_QUERY,
            "variables": {}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Use retry logic for transient failures
                async def make_request():
                    response = await client.post(graphql_url, json=payload, headers=headers, timeout=15)
                    response.raise_for_status()
                    return response
                
                response = await with_retries(
                    make_request,
                    max_retries=3,
                    base_delay=1.0,
                    operation_name="graphql_balance_query"
                )
                
                data = response.json()
                
                # Extract data from GraphQL response
                viewer_data = data.get("data", {}).get("viewer", {})
                message_info = viewer_data.get("messagePointInfo", {})
                subscription = viewer_data.get("subscription", {})
                
                result = {
                    "compute_points_available": message_info.get("messagePointBalance"),
                    "monthly_quota": message_info.get("monthlyQuota"),
                    "subscription": subscription,
                    "message_point_info": message_info,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Log balance info
                points = result.get("compute_points_available")
                if points is not None:
                    logger.info(f"Account balance (via GraphQL): {points:,} compute points")
                
                return result
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError("GraphQL: Cookies expired or invalid")
                raise APIError(f"GraphQL request failed: {e}")
            except Exception as e:
                raise APIError(f"GraphQL error: {e}")
    
    async def _get_balance_via_direct_api(self) -> dict[str, Any]:
        """Get balance using direct API endpoint (fallback method)."""
        if not self.cookies:
            raise AuthenticationError("No cookies available")
        
        # Build cookie header
        cookie_header = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
        
        headers = {
            "Cookie": cookie_header,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Origin": "https://poe.com",
            "Referer": "https://poe.com/settings",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Use retry logic for transient failures
                async def make_request():
                    response = await client.get(self.POE_SETTINGS_URL, headers=headers, timeout=15)
                    response.raise_for_status()
                    return response
                
                response = await with_retries(
                    make_request,
                    max_retries=3,
                    base_delay=1.0,
                    operation_name="direct_api_balance"
                )
                
                data = response.json()
                
                # Extract relevant information
                result = {
                    "compute_points_available": data.get("computePointsAvailable"),
                    "daily_compute_points_available": data.get("dailyComputePointsAvailable"),
                    "subscription": data.get("subscription", {}),
                    "message_point_info": data.get("messagePointInfo", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Log balance info
                points = result.get("compute_points_available", 0)
                daily = result.get("daily_compute_points_available")
                sub_active = result.get("subscription", {}).get("isActive", False)
                
                # Handle None values in formatting
                if points is not None:
                    logger.info(f"Account balance: {points:,} compute points")
                else:
                    logger.info("Account balance: Unknown")
                    
                if daily is not None:
                    logger.info(f"Daily points: {daily:,}")
                    
                logger.info(f"Subscription active: {sub_active}")
                
                return result
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError("Cookies expired or invalid. Please login again.")
                raise APIError(f"Failed to get account settings: {e}")
            except Exception as e:
                raise APIError(f"Error fetching account balance: {e}")
    
    async def _get_balance_via_api(self, api_key: str) -> dict[str, Any]:
        """Get basic balance info using API key (limited information)."""
        # This would use the official Poe API if it had a balance endpoint
        # For now, this is a placeholder that would need the actual implementation
        raise NotImplementedError("API key balance check not yet implemented by Poe")
    
    def has_valid_cookies(self) -> bool:
        """Check if we have the minimum required cookies."""
        # We need either m-b (internal API) or p-b (external API)
        return "m-b" in self.cookies or "p-b" in self.cookies
    
    def clear_cookies(self) -> None:
        """Clear stored cookies and delete cookies file."""
        self.cookies = {}
        if self.cookies_path.exists():
            self.cookies_path.unlink()
            logger.info("Cleared stored Poe cookies")
    
    async def use_with_poe_api_wrapper(self) -> Optional["AsyncPoeApi"]:
        """Create a poe-api-wrapper client using stored cookies.
        
        Returns:
            AsyncPoeApi client if poe-api-wrapper is available, None otherwise
        """
        if not self.has_valid_cookies():
            raise AuthenticationError("No valid cookies available")
        
        try:
            # Try to import poe-api-wrapper if available
            from poe_api_wrapper import AsyncPoeApi
            
            # Create client with our cookies
            client = await AsyncPoeApi(tokens=self.cookies).create()
            
            # Get settings to verify connection
            settings = await client.get_settings()
            
            logger.info("Successfully connected to Poe via poe-api-wrapper")
            logger.info(f"Points balance: {settings['messagePointInfo']['messagePointBalance']}")
            
            return client
            
        except ImportError:
            logger.warning("poe-api-wrapper not installed. Install it for enhanced functionality.")
            return None
        except Exception as e:
            logger.error(f"Failed to create poe-api-wrapper client: {e}")
            raise