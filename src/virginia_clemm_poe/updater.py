# this_file: src/virginia_clemm_poe/updater.py

"""Bot updater for Virginia Clemm Poe."""

import asyncio
import json
import re
from datetime import UTC, datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag
from loguru import logger
from playwright.async_api import Page
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .bots import (
    ApiPricing,
    BotCollection,
    BotInfo,
    PoeBot,
    ScrapedPricing,
    ScrapedPricingDetails,
    UnifiedPricing,
)
from .browser_pool import BrowserPool, get_global_pool
from .config import (
    DATA_FILE_PATH,
    DEFAULT_DEBUG_PORT,
    DIALOG_WAIT_SECONDS,
    EXPANSION_WAIT_SECONDS,
    HTTP_REQUEST_TIMEOUT_SECONDS,
    MODAL_CLOSE_WAIT_SECONDS,
    PAGE_NAVIGATION_TIMEOUT_MS,
    PAUSE_SECONDS,
    POE_API_URL,
    POE_BASE_URL,
    TABLE_TIMEOUT_MS,
)
from .poe_session import PoeSessionManager
from .type_guards import validate_poe_api_response
from .types import PoeApiResponse
from .utils.cache import cached, get_api_cache, get_scraping_cache
from .utils.logger import log_api_request, log_browser_operation, log_performance_metric
from .utils.memory import MemoryManagedOperation


class BotUpdater:
    """Updates Poe bot data with pricing information."""

    def __init__(
        self,
        api_key: str,
        debug_port: int = DEFAULT_DEBUG_PORT,
        verbose: bool = False,
        session_manager: PoeSessionManager | None = None,
    ):
        self.api_key = api_key
        self.debug_port = debug_port
        self.verbose = verbose
        self.session_manager = session_manager or PoeSessionManager()
        # Browser manager is no longer needed - using pool instead

        if verbose:
            logger.remove()
            logger.add(lambda msg: print(msg), level="DEBUG")

    @cached(cache=get_api_cache(), ttl=600, key_prefix="poe_api_bots")
    async def fetch_bots_from_api(self) -> PoeApiResponse:
        """Fetch bots from Poe API with structured logging and performance tracking.

        Returns:
            Validated PoeApiResponse containing bot data

        Raises:
            APIError: If the API response is invalid or doesn't match expected structure
            httpx.HTTPStatusError: If the API request fails
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=HTTP_REQUEST_TIMEOUT_SECONDS) as client:
            with log_api_request("GET", POE_API_URL, headers) as ctx:
                try:
                    response = await client.get(POE_API_URL, headers=headers)
                    response.raise_for_status()

                    # Add response context
                    ctx["status_code"] = response.status_code
                    ctx["response_size"] = len(response.content)

                    # Parse and validate the response
                    raw_data = response.json()
                    validated_data = validate_poe_api_response(raw_data)

                    bot_count = len(validated_data["data"])
                    ctx["bots_fetched"] = bot_count

                    # Log performance metric
                    log_performance_metric(
                        "api_bots_fetched", bot_count, "count", {"endpoint": "bots", "api_version": "v1"}
                    )

                    logger.info(f"Successfully fetched and validated {bot_count} bots from Poe API")
                    return validated_data

                except httpx.HTTPStatusError as e:
                    ctx["status_code"] = e.response.status_code
                    ctx["error_detail"] = e.response.text if e.response else "No response"
                    logger.error(f"API request failed with status {e.response.status_code}: {e.response.text[:200]}")
                    raise
                except Exception as e:
                    ctx["error_type"] = type(e).__name__
                    logger.error(f"Failed to fetch bots from API: {e}")
                    raise

    def parse_pricing_table(self, html: str) -> dict[str, Any | None]:
        """Parse pricing table HTML into structured data for bot cost analysis.

        This function extracts pricing information from HTML tables found on Poe.com
        bot pages. It handles various table formats and structures commonly used
        for displaying bot pricing information.

        The parsing logic:
        1. Locates the first table element in the HTML
        2. Iterates through table rows, extracting key-value pairs
        3. Skips header rows (all th elements)
        4. Uses the first cell as the key and remaining cells as values
        5. Handles single values and multi-value arrays appropriately

        Args:
            html: Raw HTML string containing a pricing table element

        Returns:
            Dictionary mapping pricing categories to their values:
            - Keys are pricing category names (e.g., "Input (text)", "Bot message")
            - Values can be strings, None, or lists depending on table structure

        Raises:
            ValueError: If no table element is found in the HTML

        Example:
            >>> html = '<table><tr><td>Input (text)</td><td>$0.50</td></tr></table>'
            >>> parser.parse_pricing_table(html)
            {'Input (text)': '$0.50'}

        Note:
            This parser is specifically designed for Poe.com pricing tables and
            may not work correctly with arbitrary HTML table structures.
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            raise ValueError("No table found in the provided HTML.")

        # Type check: table should be a Tag when found
        assert isinstance(table, Tag), "Table element should be a Tag"

        data: dict[str, Any | None] = {}
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if not cells or all(cell.name == "th" for cell in cells):
                continue
            texts = [cell.get_text(strip=True) for cell in cells]
            if not texts:
                continue
            key = texts[0]
            values = texts[1:]
            if not values:
                data[key] = None
            elif len(values) == 1:
                data[key] = values[0]
            else:
                data[key] = values
        return data

    async def scrape_model_info(
        self, model_id: str, page: Page
    ) -> tuple[dict[str, Any] | None, BotInfo | None, str | None]:
        """Scrape bot information with caching support."""
        # Check cache first
        cache = get_scraping_cache()
        cache_key = f"scrape_{model_id}"

        cached_result = await cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Using cached scraping result for {model_id}")
            return cached_result

        # If not cached, scrape and cache the result
        result = await self._scrape_model_info_uncached(model_id, page)

        # Only cache successful results (non-error cases)
        if result[2] is None:  # No error
            await cache.set(cache_key, result, ttl=3600)  # Cache for 1 hour
            logger.debug(f"Cached scraping result for {model_id}")

        return result

    async def _extract_with_fallback_selectors(
        self, page: Page, selectors: list[str], validate_fn=None, debug_name: str = "element"
    ) -> str | None:
        """Extract text content using a list of fallback selectors.

        Args:
            page: Playwright page object
            selectors: List of CSS selectors to try in order
            validate_fn: Optional function to validate extracted text
            debug_name: Name for debug logging

        Returns:
            Extracted text or None if not found
        """
        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.text_content()
                    if text and text.strip() and (validate_fn is None or validate_fn(text)):
                        logger.debug(f"Found {debug_name} with selector '{selector}': {text.strip()[:50]}...")
                        return text.strip()
            except Exception as e:
                logger.debug(f"{debug_name} selector '{selector}' failed: {e}")
                continue
        return None

    async def _extract_initial_points_cost(self, page: Page) -> str | None:
        """Extract initial points cost from the page."""
        selectors = [
            ".BotInfoCardHeader_initialPointsCost__oIIcI span",
            "[class*='initialPointsCost'] span",
            "[class*='BotInfoCardHeader_initialPointsCost'] span",
            ".BotInfoCardHeader_initialPointsCost__oIIcI",
            "[class*='initialPointsCost']",
        ]

        def validate_points(text: str) -> bool:
            return "point" in text.lower() or "+" in text

        return await self._extract_with_fallback_selectors(page, selectors, validate_points, "initial points cost")

    async def _extract_bot_creator(self, page: Page) -> str | None:
        """Extract bot creator handle from the page."""
        selectors = [
            ".UserHandle_creatorHandle__aNMAK",
            "[class*='creatorHandle']",
            "[class*='UserHandle_creatorHandle']",
            ".BotInfoCardHeader_operatedBy__G5WAP a[href^='/']",
            "a[href^='/@']",
        ]
        return await self._extract_with_fallback_selectors(page, selectors, debug_name="creator")

    async def _expand_description(self, page: Page) -> None:
        """Click 'View more' button to expand description if present."""
        selectors = [
            ".BotDescriptionDisclaimerSection_expander__DkmQX",
            "[class*='expander']",
            "button:has-text('View more')",
            "[aria-expanded='false']",
        ]

        for selector in selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    logger.debug(f"Found 'View more' button with selector '{selector}', clicking...")
                    await elem.click()
                    await asyncio.sleep(EXPANSION_WAIT_SECONDS)
                    break
            except Exception as e:
                logger.debug(f"View more selector '{selector}' failed: {e}")

    async def _extract_bot_description(self, page: Page) -> str | None:
        """Extract bot description from the page."""
        selectors = [
            ".BotDescriptionDisclaimerSection_text__sIeXQ span",
            "[class*='BotDescriptionDisclaimerSection_text'] span",
            ".BotDescriptionDisclaimerSection_text__sIeXQ",
            "[class*='BotDescriptionDisclaimerSection_text']",
            "[aria-expanded='true'] span",
        ]

        def validate_description(text: str) -> bool:
            return len(text.strip()) > 10

        return await self._extract_with_fallback_selectors(page, selectors, validate_description, "description")

    async def _extract_bot_disclaimer(self, page: Page) -> str | None:
        """Extract bot disclaimer text from the page."""
        selectors = [
            ".BotDescriptionDisclaimerSection_disclaimerText__yEe8h",
            "[class*='disclaimerText']",
            "[class*='BotDescriptionDisclaimerSection_disclaimerText']",
            "p:has-text('Powered by')",
            "p:has(a[href*='privacy_center'])",
        ]

        def validate_disclaimer(text: str) -> bool:
            return "Powered by" in text or "Learn more" in text

        return await self._extract_with_fallback_selectors(page, selectors, validate_disclaimer, "disclaimer")

    async def _extract_bot_info(self, page: Page) -> BotInfo:
        """Extract all bot information from the page."""
        bot_info = BotInfo()

        # Extract creator
        bot_info.creator = await self._extract_bot_creator(page)

        # Expand description if needed
        await self._expand_description(page)

        # Extract description and disclaimer
        bot_info.description = await self._extract_bot_description(page)
        bot_info.description_extra = await self._extract_bot_disclaimer(page)

        return bot_info

    async def _extract_pricing_table(self, page: Page, model_id: str) -> tuple[dict[str, Any] | None, str | None]:
        """Extract pricing information from the rates dialog.

        Returns:
            Tuple of (pricing_dict, error_message)
        """
        # Look for the action bar
        action_bar = await page.query_selector(".BotInfoCardActionBar_actionBar__5_Gnq")
        if not action_bar:
            logger.debug(f"No action bar found for {model_id}")
            return None, "No action bar found on page"

        # Find the Rates button
        rates_button = await action_bar.query_selector("button:has-text('Rates')")
        if not rates_button:
            rates_button = await action_bar.query_selector("button:has(span:has-text('Rates'))")

        if not rates_button:
            logger.debug(f"No 'Rates' button found for {model_id}")
            return None, "No Rates button found"

        # Click Rates button
        logger.debug(f"Found Rates button for {model_id}, clicking...")
        await rates_button.click()

        # Wait for dialog
        await page.wait_for_selector("div[role='dialog']", timeout=TABLE_TIMEOUT_MS)
        await asyncio.sleep(DIALOG_WAIT_SECONDS)

        # Extract table HTML
        table_html = await self._find_pricing_table_html(page)
        if not table_html:
            logger.debug(f"No table found for {model_id}")
            return None, "No pricing table found in dialog"

        # Parse pricing
        pricing = self.parse_pricing_table(table_html)

        # Close modal
        try:
            await page.keyboard.press("Escape")
            await asyncio.sleep(MODAL_CLOSE_WAIT_SECONDS)
        except Exception:
            pass

        return pricing, None

    async def _find_pricing_table_html(self, page: Page) -> str | None:
        """Find and extract pricing table HTML from the dialog."""
        selectors = [
            "div[role='dialog'] table",
            "[role='dialog'] table",
            "div.Modal_modalContent__YYC8E table",
            ".Modal_modalContent__YYC8E table",
            "table",
        ]

        # Try CSS selectors first
        for selector in selectors:
            try:
                dialog = await page.query_selector("div[role='dialog']")
                if dialog:
                    table_element = await dialog.query_selector(selector)
                    if table_element:
                        table_html = await table_element.inner_html()
                        logger.debug(f"Found table with selector: {selector}")
                        return (
                            f"<table>{table_html}</table>"
                            if not table_html.strip().startswith("<table")
                            else table_html
                        )
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")

        # Fallback to regex extraction
        try:
            dialog_html = await page.inner_html("div[role='dialog']")
            if "<table" in dialog_html:
                table_match = re.search(r"<table[^>]*>.*?</table>", dialog_html, re.DOTALL)
                if table_match:
                    logger.debug("Found table using regex extraction")
                    return table_match.group(0)
        except Exception as e:
            logger.debug(f"Regex extraction failed: {e}")

        return None

    async def _scrape_model_info_uncached(
        self, model_id: str, page: Page
    ) -> tuple[dict[str, Any] | None, BotInfo | None, str | None]:
        """Scrape pricing and bot info data for a single bot with comprehensive error handling.

        This function orchestrates a multi-stage scraping process to extract all available
        information from a Poe.com bot page. It coordinates several independent extraction
        operations and implements robust error handling with partial success recovery.

        Scraping workflow:
        1. Navigate to the bot's Poe.com page with networkidle wait
        2. Extract initial points cost from bot info card header
        3. Extract bot metadata (creator, description, disclaimer text)
        4. Extract detailed pricing from the rates dialog modal
        5. Merge all collected data and handle partial failures gracefully

        Error handling strategy:
        - Timeouts: Return partial data with timeout error message
        - Navigation failures: Return empty data with navigation error
        - Partial failures: Return available data (bot_info without pricing, etc.)
        - Complete failures: Return error message but preserve any bot_info found

        Args:
            model_id: The bot identifier to scrape (e.g., "Claude-3-Opus")
            page: Playwright page object to use for browser automation

        Returns:
            Tuple of (pricing_dict, bot_info, error_message):
            - pricing_dict: Dictionary of pricing data or None if unavailable
            - bot_info: BotInfo object with creator/description or empty if unavailable
            - error_message: String describing any errors encountered or None on success

        Example successful result:
            >>> pricing, bot_info, error = await scraper._scrape_model_info_uncached("Claude-3-Opus", page)
            >>> pricing  # {"Input (text)": "10 points/1k tokens", "Bot message": "5 points"}
            >>> bot_info  # BotInfo(creator="@anthropic", description="Claude is...")
            >>> error  # None

        Example partial failure:
            >>> pricing, bot_info, error = await scraper._scrape_model_info_uncached("bot-with-no-pricing", page)
            >>> pricing  # None
            >>> bot_info  # BotInfo(creator="@creator", description="Some description")
            >>> error  # "No Rates button found"

        Note:
            This function implements a "best effort" strategy - it attempts to collect
            as much information as possible even if some extraction steps fail.
        """
        url = POE_BASE_URL.format(id=model_id)

        with log_browser_operation("scrape_model", model_id, self.debug_port) as ctx:
            ctx["url"] = url

            try:
                # Navigate to page
                logger.debug(f"Navigating to {url}")
                await page.goto(url, wait_until="networkidle", timeout=PAGE_NAVIGATION_TIMEOUT_MS)
                await asyncio.sleep(PAUSE_SECONDS)
                ctx["page_loaded"] = True

                # Extract initial points cost
                initial_points_cost = await self._extract_initial_points_cost(page)

                # Extract bot info
                bot_info = await self._extract_bot_info(page)

                # Extract pricing from rates dialog
                pricing, error_msg = await self._extract_pricing_table(page, model_id)

                if error_msg and not bot_info.creator and not bot_info.description:
                    # If we couldn't get pricing and have no bot info, return error
                    return None, bot_info, error_msg

                # Add initial points cost to pricing if found
                if pricing and initial_points_cost:
                    pricing["initial_points_cost"] = initial_points_cost

                # Log successful scraping results
                scraped_fields = []
                if pricing:
                    scraped_fields.append("pricing")
                if bot_info and (bot_info.creator or bot_info.description):
                    scraped_fields.append("bot_info")
                if initial_points_cost:
                    scraped_fields.append("initial_points")

                ctx["scraped_fields"] = scraped_fields
                ctx["success"] = True

                logger.debug(f"Successfully scraped {model_id}: {', '.join(scraped_fields)}")
                return pricing, bot_info, error_msg

            except TimeoutError as e:
                ctx["error_type"] = "timeout"
                ctx["timeout_ms"] = PAGE_NAVIGATION_TIMEOUT_MS
                logger.error(f"Timeout while scraping {model_id} after {PAGE_NAVIGATION_TIMEOUT_MS / 1000:.1f}s: {e}")
                return None, BotInfo(), f"Operation timed out after {PAGE_NAVIGATION_TIMEOUT_MS / 1000:.1f}s"
            except Exception as e:
                ctx["error_type"] = type(e).__name__
                ctx["error_message"] = str(e)
                logger.error(f"Error while scraping {model_id}: {e}")
                return None, BotInfo(), f"Error: {str(e)}"

    def _migrate_old_pricing_format(self, model_data: dict[str, Any]) -> dict[str, Any]:
        """Migrate old pricing format to new UnifiedPricing structure.

        Args:
            model_data: Bot data dictionary potentially with old pricing format

        Returns:
            Updated bot data with migrated pricing
        """
        if "pricing" in model_data and isinstance(model_data["pricing"], dict):
            pricing_data = model_data["pricing"]

            # Check if it's the old format with checked_at and details
            if "checked_at" in pricing_data and "details" in pricing_data:
                # Convert old ScrapedPricing format to UnifiedPricing
                old_pricing = pricing_data
                model_data["pricing"] = {"api": None, "scraped": old_pricing}
                logger.debug(f"Migrated old pricing format for bot {model_data.get('id', 'unknown')}")

        return model_data

    def _extract_api_update_timestamp(self, model_data: dict[str, Any]) -> datetime | None:
        """Extract update timestamp from API bot payload if present."""
        possible_keys = (
            "updated_at",
            "updatedAt",
            "last_updated",
            "lastUpdated",
            "last_seen_at",
            "lastSeenAt",
        )

        for key in possible_keys:
            if key in model_data:
                raw_value = model_data.pop(key)
                timestamp = self._coerce_datetime(raw_value)
                if timestamp:
                    return timestamp
        return None

    @staticmethod
    def _coerce_datetime(value: Any) -> datetime | None:
        """Convert various timestamp representations to naive UTC datetimes."""
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value

        if isinstance(value, (int, float)):
            epoch_value = value / 1000 if value > 1_000_000_000_000 else value
            try:
                return datetime.utcfromtimestamp(epoch_value)
            except (OSError, OverflowError):
                return None

        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            normalized = normalized.replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError:
                return None
            if parsed.tzinfo:
                return parsed.astimezone(UTC).replace(tzinfo=None)
            return parsed

        return None

    def _load_existing_collection(self, force: bool) -> BotCollection | None:
        """Load existing bot collection from disk if available.

        Args:
            force: If True, skip loading existing data

        Returns:
            Existing BotCollection or None if not available/force=True
        """
        if not DATA_FILE_PATH.exists() or force:
            return None

        try:
            with open(DATA_FILE_PATH) as f:
                collection_data = json.load(f)

            # Check version and migrate if needed
            version = collection_data.get("version", 1)
            if version < 2:
                logger.info("Migrating data from version 1 to version 2 (dual pricing support)")
                # Migrate each bot's pricing
                if "data" in collection_data:
                    for i, model_data in enumerate(collection_data["data"]):
                        collection_data["data"][i] = self._migrate_old_pricing_format(model_data)
                collection_data["version"] = 2

            collection = BotCollection(**collection_data)
            logger.info(f"Loaded {len(collection.data)} existing bots (version {version})")
            return collection
        except Exception as e:
            logger.warning(f"Failed to load existing data: {e}")
            return None

    async def _fetch_and_parse_api_bots(self) -> tuple[dict[str, Any], list[PoeBot]]:
        """Fetch bots from API and parse them into PoeBot instances.

        Returns:
            Tuple of (raw_api_data, parsed_models)
        """
        logger.info("Fetching bots from API...")
        api_data = await self.fetch_bots_from_api()
        api_bots = []

        for model_dict in api_data["data"]:
            # Ensure architecture is properly typed
            model_data: dict[str, Any] = dict(model_dict)
            if "architecture" in model_data and isinstance(model_data["architecture"], dict):
                from .bots import Architecture

                model_data["architecture"] = Architecture(**model_data["architecture"])

            # Handle pricing field from API
            api_pricing_data = None
            if "pricing" in model_data and isinstance(model_data["pricing"], dict):
                pricing_data = model_data["pricing"]

                # Check if it's the new API format with prompt/completion fields
                if any(key in pricing_data for key in ["prompt", "completion", "image", "request"]):
                    # Store API pricing data for later processing
                    api_pricing_data = pricing_data
                    logger.debug(f"Found API pricing for {model_dict.get('id', 'unknown')}")

                # Remove pricing from model_data as we'll handle it separately
                model_data.pop("pricing", None)

            api_updated_at = self._extract_api_update_timestamp(model_data)

            # Create the bot without pricing first
            api_model = PoeBot(**model_data)
            api_model.api_last_updated = api_updated_at or datetime.utcnow()

            # Add API pricing if available
            if api_pricing_data:
                api_model.pricing = UnifiedPricing(api=ApiPricing(**api_pricing_data))

            api_bots.append(api_model)

        logger.info(f"Fetched {len(api_bots)} bots from API")
        return api_data, api_bots

    def _merge_bots(self, api_bots: list[PoeBot], existing_collection: BotCollection | None) -> list[PoeBot]:
        """Merge API bots with existing data, combining API and scraped pricing.

        Args:
            api_bots: Fresh bots from API (may have API pricing)
            existing_collection: Existing collection with scraped data

        Returns:
            Merged list of bots sorted by ID
        """
        if not existing_collection:
            return sorted(api_bots, key=lambda x: x.id)

        # Create lookup for existing bots
        existing_lookup = {bot.id: bot for bot in existing_collection.data}
        api_model_ids = set()
        merged_bots = []

        # Merge API bots with existing data
        for api_model in api_bots:
            api_model_ids.add(api_model.id)

            if api_model.id in existing_lookup:
                existing = existing_lookup[api_model.id]

                # Merge pricing information
                if api_model.pricing and api_model.pricing.api:
                    # API bot has new API pricing
                    if existing.pricing and existing.pricing.scraped:
                        # Combine API pricing with existing scraped pricing
                        api_model.pricing = UnifiedPricing(api=api_model.pricing.api, scraped=existing.pricing.scraped)
                    # else: keep API pricing only
                elif existing.pricing:
                    # No API pricing, preserve existing pricing
                    api_model.pricing = existing.pricing

                # Preserve error and bot info
                if existing.pricing_error:
                    api_model.pricing_error = existing.pricing_error
                if existing.bot_info:
                    api_model.bot_info = existing.bot_info

            merged_bots.append(api_model)

        # Log removed bots
        removed_ids = set(existing_lookup.keys()) - api_model_ids
        for removed_id in removed_ids:
            logger.info(f"Removed bot no longer in API: {removed_id}")

        return sorted(merged_bots, key=lambda x: x.id)

    def _save_collection(self, collection: BotCollection) -> None:
        """Persist the current bot collection to disk sorted by API age."""
        collection.sort_by_api_last_updated()
        DATA_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE_PATH, "w") as f:
            json.dump(collection.model_dump(), f, indent=2, ensure_ascii=False, default=str)
        logger.debug(f"Persisted {len(collection.data)} bots to {DATA_FILE_PATH}")

    def _get_bots_to_update(
        self, collection: BotCollection, force: bool, update_info: bool, update_pricing: bool
    ) -> list[PoeBot]:
        """Determine which bots need updates based on criteria.

        Args:
            collection: Bot collection to check
            force: Force update all bots
            update_info: Check if bot info needs update
            update_pricing: Check if scraped pricing needs update

        Returns:
            List of bots that need updates
        """
        if not update_info and not update_pricing:
            return []

        bots_to_update = []

        for bot in collection.data:
            needs_update = False

            # Check if scraped pricing needs update
            if update_pricing and (force or bot.needs_scraping_update()):
                needs_update = True

            # Check if bot info needs update
            if update_info and (force or not bot.bot_info):
                needs_update = True

            if needs_update:
                bots_to_update.append(bot)

        return bots_to_update

    async def _update_bot_data(self, bot: PoeBot, page: Page, update_info: bool, update_pricing: bool) -> None:
        """Update a single bot's scraped pricing and/or bot info.

        Args:
            bot: Bot to update (modified in place)
            page: Browser page to use for scraping
            update_info: Whether to update bot info
            update_pricing: Whether to update scraped pricing
        """
        pricing_data, bot_info, error = await self.scrape_model_info(bot.id, page)

        # Update scraped pricing if requested
        if update_pricing:
            if pricing_data:
                # Create or update UnifiedPricing with scraped data
                if not bot.pricing:
                    bot.pricing = UnifiedPricing()

                bot.pricing.scraped = ScrapedPricing(
                    checked_at=datetime.utcnow(), details=ScrapedPricingDetails(**pricing_data)
                )
                bot.pricing_error = None
                logger.info(f"✓ Updated scraped pricing for {bot.id}")
            else:
                bot.pricing_error = error or "Unknown error"
                # Don't clear pricing entirely - keep API pricing if it exists
                if bot.pricing:
                    bot.pricing.scraped = None
                logger.warning(f"✗ No scraped pricing found for {bot.id}: {error}")

        # Update bot info if requested
        if update_info:
            if bot_info and (bot_info.creator or bot_info.description or bot_info.description_extra):
                bot.bot_info = bot_info
                logger.info(f"✓ Updated bot info for {bot.id}")
            else:
                logger.warning(f"✗ No bot info found for {bot.id}")

    async def _update_bots_with_progress(
        self,
        collection: BotCollection,
        bots_to_update: list[PoeBot],
        update_info: bool,
        update_pricing: bool,
        memory_monitor: MemoryManagedOperation,
        pool: BrowserPool,
    ) -> None:
        """Update bots with progress tracking, persistence, and memory management.

        Args:
            collection: Full bot collection being updated
            bots_to_update: List of bots to update
            update_info: Whether to update bot info
            update_pricing: Whether to update pricing
            memory_monitor: Memory management context
            pool: Browser connection pool
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Updating bots...", total=len(bots_to_update))
            bots_processed = 0

            for bot in bots_to_update:
                progress.update(task, description=f"Updating {bot.id}...")

                # Use browser pool for each bot
                async with pool.acquire_page() as page:
                    await self._update_bot_data(bot, page, update_info, update_pricing)

                # Persist progress after each bot update
                self._save_collection(collection)

                # Track progress and memory usage
                bots_processed += 1
                memory_monitor.increment_operation_count()

                # Periodic memory monitoring (every 10 bots)
                if bots_processed % 10 == 0:
                    memory_monitor.log_memory_status(f"processed_{bots_processed}_bots")

                    # Force cleanup if memory is getting high
                    if memory_monitor.should_run_cleanup():
                        logger.info(f"Running memory cleanup after processing {bots_processed} bots")
                        await memory_monitor.cleanup_memory()

                progress.advance(task)

    async def sync_bots(
        self, force: bool = False, update_info: bool = True, update_pricing: bool = True
    ) -> BotCollection:
        """Sync bots with API and update pricing/info data.

        This method coordinates the entire bot synchronization process:
        1. Loads existing data if available
        2. Fetches fresh bots from API
        3. Merges API data with existing scraped data
        4. Updates bots that need new pricing/bot info

        Args:
            force: Force update even if data exists
            update_info: Update bot info (creator, description)
            update_pricing: Update pricing information

        Returns:
            Updated BotCollection with all bots
        """
        # Load existing data
        existing_collection = self._load_existing_collection(force)

        # Fetch fresh bots from API
        api_data, api_bots = await self._fetch_and_parse_api_bots()

        # Merge with existing data and persist immediately (captures removals)
        merged_bots = self._merge_bots(api_bots, existing_collection)
        collection = BotCollection(object=api_data["object"], data=merged_bots)
        self._save_collection(collection)

        # Determine which bots need updates (oldest API timestamp first)
        bots_to_update = self._get_bots_to_update(collection, force, update_info, update_pricing)

        if not bots_to_update:
            logger.info("No bots need updates")
            return collection

        logger.info(f"Found {len(bots_to_update)} bots to update")

        # Use memory management for the entire update operation
        async with MemoryManagedOperation(f"sync_{len(bots_to_update)}_bots") as memory_monitor:
            # Get the browser pool for better performance
            pool = await get_global_pool(
                max_size=3,  # Allow up to 3 concurrent browser connections
                debug_port=self.debug_port,
                verbose=self.verbose,
            )

            # Log performance metric for pool usage
            log_performance_metric("browser_pool_enabled", 1, "count", {"bots_to_update": len(bots_to_update)})

            # Update bots with progress tracking and persistence
            await self._update_bots_with_progress(
                collection, bots_to_update, update_info, update_pricing, memory_monitor, pool
            )

        # Pool stats for debugging
        if self.verbose:
            stats = await pool.get_stats()
            logger.debug(f"Browser pool stats: {stats}")

        # Final persistence to capture any remaining updates
        self._save_collection(collection)
        return collection

    async def update_all(self, force: bool = False, update_info: bool = True, update_pricing: bool = True) -> None:
        """Update bot data and save to file.

        Args:
            force: Force update even if data exists
            update_info: Update bot info (creator, description)
            update_pricing: Update pricing information
        """
        collection = await self.sync_bots(force=force, update_info=update_info, update_pricing=update_pricing)

        # Final persistence handled by helper to ensure consistent ordering
        self._save_collection(collection)
        logger.info(f"✓ Saved {len(collection.data)} bots to {DATA_FILE_PATH}")

    async def get_account_balance(self) -> dict[str, Any]:
        """Get Poe account balance using stored session cookies.

        Returns:
            Dictionary with balance information including compute points

        Raises:
            AuthenticationError: If no valid cookies are available
        """
        return await self.session_manager.get_account_balance(
            use_api_key=False,  # Prefer cookies for more detailed info
            api_key=self.api_key,
        )

    async def extract_cookies_from_browser(self, page: Page) -> dict[str, str]:
        """Extract Poe cookies from an active browser session.

        This is designed to work with PlaywrightAuthor's browser session.

        Args:
            page: Active Playwright page from PlaywrightAuthor

        Returns:
            Dictionary of extracted cookies
        """
        return await self.session_manager.extract_from_existing_playwright_session(page)

    async def login_and_extract_cookies(self) -> dict[str, str]:
        """Open browser for manual Poe login and extract cookies.

        Returns:
            Dictionary of extracted cookies after successful login
        """
        # Get a browser from the pool for login
        pool = await get_global_pool(max_size=1, debug_port=self.debug_port, verbose=self.verbose)

        async with pool.acquire_page() as page:
            # Navigate to Poe login
            await page.goto("https://poe.com/login")
            logger.info("Please log in to Poe.com in the browser window...")

            # Wait for login (detect by user menu button)
            await page.wait_for_selector(
                "button[aria-label='User menu']",
                timeout=300000,  # 5 minutes
            )

            logger.info("Login successful, extracting cookies...")
            return await self.extract_cookies_from_browser(page)

    async def get_enhanced_model_data(self) -> BotCollection | None:
        """Get bot data with enhanced information using poe-api-wrapper.

        This uses the faster poe-api-wrapper library if available and cookies are set.

        Returns:
            Enhanced bot collection or None if not available
        """
        if not self.session_manager.has_valid_cookies():
            logger.warning("No valid cookies for enhanced bot data")
            return None

        try:
            # Try to use poe-api-wrapper for faster access
            client = await self.session_manager.use_with_poe_api_wrapper()
            if client:
                # Get available bots with enhanced info
                bots = await client.get_available_bots(get_all=True)
                logger.info(f"Retrieved {len(bots)} bots via poe-api-wrapper")

                # Could enhance our bot data with this information
                # This is where we'd merge the bot data with our bots

            return None

        except Exception as e:
            logger.error(f"Failed to get enhanced bot data: {e}")
            return None
