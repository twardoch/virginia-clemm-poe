# this_file: src/virginia_clemm_poe/updater.py

"""Model updater for Virginia Clemm Poe."""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import Page
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .browser import BrowserManager
from .config import (
    DATA_FILE_PATH,
    LOAD_TIMEOUT_MS,
    PAUSE_SECONDS,
    POE_API_URL,
    POE_BASE_URL,
    TABLE_TIMEOUT_MS,
)
from .models import ModelCollection, Pricing, PricingDetails, PoeModel


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
    
    async def fetch_models_from_api(self) -> Dict[str, Any]:
        """Fetch models from Poe API."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(POE_API_URL, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"API request failed with status {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Failed to fetch models from API: {e}")
                raise
    
    def parse_pricing_table(self, html: str) -> Dict[str, Optional[Any]]:
        """Parse pricing table HTML into structured data."""
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            raise ValueError("No table found in the provided HTML.")

        data: Dict[str, Optional[Any]] = {}
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
    
    async def scrape_model_pricing(self, model_id: str, page: Page) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Scrape pricing data for a single model."""
        url = POE_BASE_URL.format(id=model_id)
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=LOAD_TIMEOUT_MS)
            await asyncio.sleep(PAUSE_SECONDS)
            
            # Look for the action bar containing the Rates button
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
                "table"
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
                    table_match = re.search(r'<table[^>]*>.*?</table>', dialog_html, re.DOTALL)
                    if table_match:
                        table_html = table_match.group(0)
                        logger.debug("Found table using regex extraction")
            
            if not table_html:
                logger.debug(f"No table found for {model_id}")
                return None, "No pricing table found in dialog"
            
            if not table_html.strip().startswith("<table"):
                table_html = f"<table>{table_html}</table>"
                
            pricing = self.parse_pricing_table(table_html)
            
            # Close the modal
            try:
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
            except Exception:
                pass
                
            return pricing, None
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping {model_id}")
            return None, "Timeout waiting for page elements"
        except Exception as e:
            logger.error(f"Error while scraping {model_id}: {e}")
            return None, f"Error: {str(e)}"
    
    async def sync_models(self, force: bool = False) -> ModelCollection:
        """Sync models with API and update pricing data."""
        # Load existing data
        existing_collection = None
        if DATA_FILE_PATH.exists() and not force:
            try:
                with open(DATA_FILE_PATH, "r") as f:
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
                # Preserve pricing data from existing model
                existing = existing_lookup[api_model.id]
                if existing.pricing:
                    api_model.pricing = existing.pricing
                if existing.pricing_error:
                    api_model.pricing_error = existing.pricing_error
            
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
        
        # Update pricing for models that need it
        models_to_update = [m for m in collection.data if m.needs_pricing_update() or force]
        
        if not models_to_update:
            logger.info("No models need pricing updates")
            return collection
        
        logger.info(f"Found {len(models_to_update)} models to update")
        
        # Connect browser and update pricing
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
                    
                    pricing_data, error = await self.scrape_model_pricing(model.id, page)
                    
                    if pricing_data:
                        model.pricing = Pricing(
                            checked_at=datetime.utcnow(),
                            details=PricingDetails(**pricing_data)
                        )
                        model.pricing_error = None
                        logger.info(f"✓ Updated pricing for {model.id}")
                    else:
                        model.pricing_error = error or "Unknown error"
                        model.pricing = None
                        logger.warning(f"✗ No pricing found for {model.id}: {error}")
                    
                    progress.advance(task)
            
            await page.close()
        finally:
            await self.browser_manager.close()
        
        return collection
    
    async def update_all(self, force: bool = False) -> None:
        """Update all model data and save to file."""
        collection = await self.sync_models(force=force)
        
        # Ensure data directory exists
        DATA_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(DATA_FILE_PATH, "w") as f:
            json.dump(collection.dict(), f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✓ Saved {len(collection.data)} models to {DATA_FILE_PATH}")