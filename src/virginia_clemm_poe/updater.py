# this_file: src/virginia_clemm_poe/updater.py

"""Model updater for Virginia Clemm Poe."""

import asyncio
import json
import re
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import Page
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .browser_manager import BrowserManager
from .config import (
    DATA_FILE_PATH,
    LOAD_TIMEOUT_MS,
    PAUSE_SECONDS,
    POE_API_URL,
    POE_BASE_URL,
    TABLE_TIMEOUT_MS,
)
from .models import BotInfo, ModelCollection, PoeModel, Pricing, PricingDetails
from .utils.logger import log_api_request, log_browser_operation, log_operation, log_performance_metric


class ModelUpdater:
    """Updates Poe model data with pricing information."""

    def __init__(self, api_key: str, debug_port: int = 9222, verbose: bool = False):
        self.api_key = api_key
        self.debug_port = debug_port
        self.verbose = verbose
        self.browser_manager = BrowserManager(debug_port)

        if verbose:
            logger.remove()
            logger.add(lambda msg: print(msg), level="DEBUG")

    async def fetch_models_from_api(self) -> dict[str, Any]:
        """Fetch models from Poe API with structured logging and performance tracking."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient() as client:
            with log_api_request("GET", POE_API_URL, headers) as ctx:
                try:
                    response = await client.get(POE_API_URL, headers=headers)
                    response.raise_for_status()
                    
                    # Add response context
                    ctx["status_code"] = response.status_code
                    ctx["response_size"] = len(response.content)
                    
                    data = response.json()
                    model_count = len(data.get("data", []))
                    ctx["models_fetched"] = model_count
                    
                    # Log performance metric
                    log_performance_metric(
                        "api_models_fetched", 
                        model_count, 
                        "count",
                        {"endpoint": "models", "api_version": "v1"}
                    )
                    
                    logger.info(f"Successfully fetched {model_count} models from Poe API")
                    return data
                    
                except httpx.HTTPStatusError as e:
                    ctx["status_code"] = e.response.status_code
                    ctx["error_detail"] = e.response.text if e.response else "No response"
                    logger.error(f"API request failed with status {e.response.status_code}: {e.response.text[:200]}")
                    raise
                except Exception as e:
                    ctx["error_type"] = type(e).__name__
                    logger.error(f"Failed to fetch models from API: {e}")
                    raise

    def parse_pricing_table(self, html: str) -> dict[str, Any | None]:
        """Parse pricing table HTML into structured data."""
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            raise ValueError("No table found in the provided HTML.")

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
        """Scrape pricing and bot info data for a single model with detailed logging."""
        url = POE_BASE_URL.format(id=model_id)

        with log_browser_operation("scrape_model", model_id, self.debug_port) as ctx:
            ctx["url"] = url
            
            try:
                logger.debug(f"Navigating to {url}")
                await page.goto(url, wait_until="networkidle", timeout=LOAD_TIMEOUT_MS)
                await asyncio.sleep(PAUSE_SECONDS)
                
                ctx["page_loaded"] = True

                # Initialize bot info
                bot_info = BotInfo()

                # Extract initial points cost with fallback selectors
                initial_points_cost = None
                initial_points_selectors = [
                    ".BotInfoCardHeader_initialPointsCost__oIIcI span",
                    "[class*='initialPointsCost'] span",
                    "[class*='BotInfoCardHeader_initialPointsCost'] span",
                    ".BotInfoCardHeader_initialPointsCost__oIIcI",
                "[class*='initialPointsCost']",
                ]

                for selector in initial_points_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.text_content()
                            if text and ("point" in text.lower() or "+" in text):
                                initial_points_cost = text.strip()
                                logger.debug(f"Found initial points cost with selector '{selector}': {initial_points_cost}")
                                break
                    except Exception as e:
                        logger.debug(f"Selector '{selector}' failed: {e}")
                        continue

                # Extract creator handle with fallback selectors
                creator_selectors = [
                    ".UserHandle_creatorHandle__aNMAK",
                    "[class*='creatorHandle']",
                    "[class*='UserHandle_creatorHandle']",
                    ".BotInfoCardHeader_operatedBy__G5WAP a[href^='/']",
                    "a[href^='/@']",
                ]

                for selector in creator_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.text_content()
                            if text and text.strip():
                                bot_info.creator = text.strip()
                                logger.debug(f"Found creator with selector '{selector}': {bot_info.creator}")
                                break
                    except Exception as e:
                        logger.debug(f"Creator selector '{selector}' failed: {e}")
                        continue

                # Click "View more" button if present to expand description with fallback selectors
                view_more_selectors = [
                    ".BotDescriptionDisclaimerSection_expander__DkmQX",
                    "[class*='expander']",
                    "button:has-text('View more')",
                    "[aria-expanded='false']",
                ]

                for selector in view_more_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            logger.debug(f"Found 'View more' button with selector '{selector}', clicking...")
                            await elem.click()
                            await asyncio.sleep(0.5)  # Wait for expansion
                            break
                    except Exception as e:
                        logger.debug(f"View more selector '{selector}' failed: {e}")
                        continue

                # Extract description with fallback selectors
                description_selectors = [
                    ".BotDescriptionDisclaimerSection_text__sIeXQ span",
                    "[class*='BotDescriptionDisclaimerSection_text'] span",
                    ".BotDescriptionDisclaimerSection_text__sIeXQ",
                    "[class*='BotDescriptionDisclaimerSection_text']",
                    "[aria-expanded='true'] span",
                ]

                for selector in description_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.text_content()
                            if text and text.strip() and len(text.strip()) > 10:
                                bot_info.description = text.strip()
                                logger.debug(
                                    f"Found description with selector '{selector}': {bot_info.description[:50]}..."
                                )
                                break
                    except Exception as e:
                        logger.debug(f"Description selector '{selector}' failed: {e}")
                        continue

                # Extract description_extra (disclaimer text) with fallback selectors
                disclaimer_selectors = [
                    ".BotDescriptionDisclaimerSection_disclaimerText__yEe8h",
                    "[class*='disclaimerText']",
                    "[class*='BotDescriptionDisclaimerSection_disclaimerText']",
                    "p:has-text('Powered by')",
                    "p:has(a[href*='privacy_center'])",
                ]

                for selector in disclaimer_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.text_content()
                            if text and text.strip() and ("Powered by" in text or "Learn more" in text):
                                bot_info.description_extra = text.strip()
                                logger.debug(
                                    f"Found description_extra with selector '{selector}': {bot_info.description_extra[:50]}..."
                                )
                                break
                    except Exception as e:
                        logger.debug(f"Disclaimer selector '{selector}' failed: {e}")
                        continue

                # Look for the action bar containing the Rates button
                action_bar = await page.query_selector(".BotInfoCardActionBar_actionBar__5_Gnq")

                if not action_bar:
                    logger.debug(f"No action bar found for {model_id}")
                    return None, bot_info, "No action bar found on page"

                # Find the Rates button
                rates_button = await action_bar.query_selector("button:has-text('Rates')")

                if not rates_button:
                    rates_button = await action_bar.query_selector("button:has(span:has-text('Rates'))")

                if not rates_button:
                    logger.debug(f"No 'Rates' button found for {model_id}")
                    return None, bot_info, "No Rates button found"

                logger.debug(f"Found Rates button for {model_id}, clicking...")
                await rates_button.click()

                # Wait for the rates dialog
                await page.wait_for_selector("div[role='dialog']", timeout=TABLE_TIMEOUT_MS)
                await asyncio.sleep(1)

                # Extract pricing table
                table_html = None
                selectors = [
                    "div[role='dialog'] table",
                    "[role='dialog'] table",
                    "div.Modal_modalContent__YYC8E table",
                    ".Modal_modalContent__YYC8E table",
                    "table",
                ]

                for selector in selectors:
                    try:
                        dialog = await page.query_selector("div[role='dialog']")
                        if dialog:
                            table_element = await dialog.query_selector(selector)
                            if table_element:
                                table_html = await table_element.inner_html()
                                logger.debug(f"Found table with selector: {selector}")
                                break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue

                if not table_html:
                    dialog_html = await page.inner_html("div[role='dialog']")
                    if "<table" in dialog_html:
                        table_match = re.search(r"<table[^>]*>.*?</table>", dialog_html, re.DOTALL)
                        if table_match:
                            table_html = table_match.group(0)
                            logger.debug("Found table using regex extraction")

                if not table_html:
                    logger.debug(f"No table found for {model_id}")
                    return None, bot_info, "No pricing table found in dialog"

                if not table_html.strip().startswith("<table"):
                    table_html = f"<table>{table_html}</table>"

                pricing = self.parse_pricing_table(table_html)

                # Add initial points cost to pricing if we found it
                if initial_points_cost:
                    pricing["initial_points_cost"] = initial_points_cost

                # Close the modal
                try:
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

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
                return pricing, bot_info, None

            except TimeoutError as e:
                ctx["error_type"] = "timeout"
                ctx["timeout_ms"] = LOAD_TIMEOUT_MS
                logger.error(f"Timeout while scraping {model_id} after {LOAD_TIMEOUT_MS}ms")
                return None, bot_info, "Timeout waiting for page elements"
            except Exception as e:
                ctx["error_type"] = type(e).__name__
                ctx["error_message"] = str(e)
                logger.error(f"Error while scraping {model_id}: {e}")
                return None, bot_info, f"Error: {str(e)}"

    async def sync_models(
        self, force: bool = False, update_info: bool = True, update_pricing: bool = True
    ) -> ModelCollection:
        """Sync models with API and update pricing/info data.

        Args:
            force: Force update even if data exists
            update_info: Update bot info (creator, description)
            update_pricing: Update pricing information
        """
        # Load existing data
        existing_collection = None
        if DATA_FILE_PATH.exists() and not force:
            try:
                with open(DATA_FILE_PATH) as f:
                    data = json.load(f)
                existing_collection = ModelCollection(**data)
                logger.info(f"Loaded {len(existing_collection.data)} existing models")
            except Exception as e:
                logger.warning(f"Failed to load existing data: {e}")

        # Fetch fresh models from API
        logger.info("Fetching models from API...")
        api_data = await self.fetch_models_from_api()
        api_models = [PoeModel(**m) for m in api_data["data"]]
        logger.info(f"Fetched {len(api_models)} models from API")

        # Merge with existing data
        merged_models = []
        existing_lookup = {}
        if existing_collection:
            existing_lookup = {m.id: m for m in existing_collection.data}

        api_model_ids = set()
        for api_model in api_models:
            api_model_ids.add(api_model.id)

            if api_model.id in existing_lookup:
                # Preserve pricing and bot info data from existing model
                existing = existing_lookup[api_model.id]
                if existing.pricing:
                    api_model.pricing = existing.pricing
                if existing.pricing_error:
                    api_model.pricing_error = existing.pricing_error
                if existing.bot_info:
                    api_model.bot_info = existing.bot_info

            merged_models.append(api_model)

        # Log removed models
        if existing_lookup:
            removed_ids = set(existing_lookup.keys()) - api_model_ids
            for removed_id in removed_ids:
                logger.info(f"Removed model no longer in API: {removed_id}")

        # Sort by ID
        merged_models.sort(key=lambda x: x.id)

        # Create collection
        collection = ModelCollection(object=api_data["object"], data=merged_models)

        # Check if we need to do any web scraping
        if not update_info and not update_pricing:
            logger.info("No updates requested")
            return collection

        # Determine which models to update
        models_to_update = []

        for model in collection.data:
            needs_update = False

            if update_pricing and (model.needs_pricing_update() or force):
                needs_update = True

            if update_info and (not model.bot_info or force):
                needs_update = True

            if needs_update:
                models_to_update.append(model)

        if not models_to_update:
            logger.info("No models need updates")
            return collection

        logger.info(f"Found {len(models_to_update)} models to update")

        # Connect browser and update data
        await self.browser_manager.connect()
        page = await self.browser_manager.new_page()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Updating models...", total=len(models_to_update))

                for model in models_to_update:
                    progress.update(task, description=f"Updating {model.id}...")

                    pricing_data, bot_info, error = await self.scrape_model_info(model.id, page)

                    # Update pricing if requested
                    if update_pricing:
                        if pricing_data:
                            model.pricing = Pricing(
                                checked_at=datetime.utcnow(), details=PricingDetails(**pricing_data)
                            )
                            model.pricing_error = None
                            logger.info(f"✓ Updated pricing for {model.id}")
                        else:
                            model.pricing_error = error or "Unknown error"
                            model.pricing = None
                            logger.warning(f"✗ No pricing found for {model.id}: {error}")

                    # Update bot info if requested
                    if update_info:
                        if bot_info and (bot_info.creator or bot_info.description or bot_info.description_extra):
                            model.bot_info = bot_info
                            logger.info(f"✓ Updated bot info for {model.id}")
                        else:
                            logger.warning(f"✗ No bot info found for {model.id}")

                    progress.advance(task)

            await page.close()
        finally:
            await self.browser_manager.close()

        return collection

    async def update_all(self, force: bool = False, update_info: bool = True, update_pricing: bool = True) -> None:
        """Update model data and save to file.

        Args:
            force: Force update even if data exists
            update_info: Update bot info (creator, description)
            update_pricing: Update pricing information
        """
        collection = await self.sync_models(force=force, update_info=update_info, update_pricing=update_pricing)

        # Ensure data directory exists
        DATA_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(DATA_FILE_PATH, "w") as f:
            json.dump(collection.dict(), f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✓ Saved {len(collection.data)} models to {DATA_FILE_PATH}")
