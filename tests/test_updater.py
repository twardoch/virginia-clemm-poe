# this_file: tests/test_updater.py

"""Tests for the bot updater integration with Poe API data."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from virginia_clemm_poe.bots import Architecture, BotCollection, PoeBot
from virginia_clemm_poe.updater import BotUpdater


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
