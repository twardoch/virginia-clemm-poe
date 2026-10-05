# this_file: tests/test_updater.py

"""Tests for the bot updater integration with Poe API data."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from virginia_clemm_poe.bots import ApiPricing, Architecture, BotCollection, PoeBot
from virginia_clemm_poe.updater import BotUpdater


@pytest.mark.asyncio
async def test_rate_card_response_recovers_a_dialog_without_tables():
    page = MagicMock()
    handlers = {}
    page.on.side_effect = lambda event, handler: handlers.update({event: handler})
    response = MagicMock(url="https://poe.com/api/gql_POST")
    response.json = AsyncMock(
        return_value={
            "data": {
                "botById": {
                    "botPricing": {
                        "rateMenuMarkdown": "Interpreter costs 1 point per message, plus the rates of any other bots it calls."
                    }
                }
            }
        }
    )
    button = MagicMock()

    async def click(**kwargs):
        handlers["response"](response)

    button.click = click
    page.get_by_role.return_value = button
    dialog = MagicMock()
    dialog.wait_for = AsyncMock()
    dialog.locator.return_value.first.wait_for = AsyncMock(side_effect=TimeoutError)
    dialog.inner_html = AsyncMock(return_value="<p>No table</p>")
    page.locator.return_value = dialog
    page.keyboard.press = AsyncMock()
    pricing, error = await BotUpdater("key")._extract_pricing_table(page, "interpreter")
    assert error is None and pricing["rates"][0]["amount"] == "1", "GraphQL rate prose should recover the price"
    assert pricing["rates"][0]["lower_bound"], "Called bot costs must remain additional"
    page.remove_listener.assert_called_once()


@pytest.mark.asyncio
async def test_failed_refresh_retains_the_previous_observed_rate(sample_poe_model):
    updater = BotUpdater("key")
    updater.scrape_model_info = AsyncMock(return_value=(None, None, "Timeout"))
    old = sample_poe_model.pricing.scraped.model_copy(deep=True)
    await updater._update_bot_data(sample_poe_model, MagicMock(), False, True)
    assert sample_poe_model.pricing.scraped == old, "A temporary failure must not erase known prices"
    assert sample_poe_model.pricing_error == "Timeout", "The failed refresh should remain visible"


@pytest.mark.asyncio
async def test_rates_button_when_action_bar_class_changes_then_extracts_table():
    page = MagicMock()
    button = MagicMock()
    button.click = AsyncMock()
    page.get_by_role.return_value = button
    dialog = MagicMock()
    dialog.wait_for = AsyncMock()
    dialog.locator.return_value.first.wait_for = AsyncMock()
    dialog.inner_html = AsyncMock(return_value="<table><tr><td>Bot message</td><td>10 points</td></tr></table>")
    page.locator.return_value = dialog
    page.keyboard.press = AsyncMock()
    updater = BotUpdater(api_key="test-key")
    pricing, error = await updater._extract_pricing_table(page, "test-bot")
    assert error is None, "Rates should work without a hardcoded action bar class"
    assert pricing["Bot message"] == "10 points", "The visible rates table should be parsed"
    assert pricing["rates"][0]["amount"] == "10", "The numeric rate should be preserved"


@pytest.mark.asyncio
async def test_fetch_and_parse_api_bots_records_last_updated(
    monkeypatch: pytest.MonkeyPatch, sample_api_response_data: dict[str, Any]
) -> None:
    """Fetcher should stamp each bot with the time it was last seen."""

    async def fake_fetch(self: BotUpdater) -> dict[str, Any]:
        return sample_api_response_data

    updater = BotUpdater(api_key="test-key")
    # Patch the network call to avoid hitting the real API
    monkeypatch.setattr(BotUpdater, "fetch_bots_from_api", fake_fetch, raising=False)

    _, bots = await updater._fetch_and_parse_api_bots()
    assert bots, "Expected at least one bot from fake API response"
    assert bots[0].api_last_updated is not None, "Bot should record last API update timestamp"
    assert isinstance(bots[0].api_last_updated, datetime)


def test_merge_bots_removes_missing_entries(sample_architecture: Architecture) -> None:
    """Merge should drop bots that no longer exist in the API dataset."""
    updater = BotUpdater(api_key="test-key")

    survivor_api = PoeBot(
        id="survivor-bot",
        created=1700001000,
        owned_by="poe",
        root="survivor-bot",
        architecture=sample_architecture,
        api_last_updated=datetime(2025, 1, 5, 12, 0, 0),
    )

    survivor_existing = survivor_api.model_copy()
    stale_existing = PoeBot(
        id="stale-bot",
        created=1690000000,
        owned_by="poe",
        root="stale-bot",
        architecture=sample_architecture,
        api_last_updated=datetime(2024, 12, 31, 12, 0, 0),
    )

    existing_collection = BotCollection(data=[survivor_existing, stale_existing])

    merged = updater._merge_bots([survivor_api], existing_collection)
    merged_ids = {bot.id for bot in merged}

    assert "survivor-bot" in merged_ids
    assert "stale-bot" not in merged_ids, "Bots absent from the API should be removed"


def test_api_refresh_without_rates_drops_stale_api_prices(sample_poe_model):
    existing = sample_poe_model.model_copy(deep=True)
    existing.pricing.api = ApiPricing(prompt="0.01")
    fresh = existing.model_copy(deep=True)
    fresh.pricing = None
    result = BotUpdater("key")._merge_bots([fresh], BotCollection(data=[existing]))
    assert result[0].pricing.api is None, "Missing current API prices must not retain old API rates"
    assert result[0].pricing.scraped is not None, "Website rates remain independent of API rates"
