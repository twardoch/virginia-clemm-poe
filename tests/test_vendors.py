# this_file: tests/test_vendors.py
"""Vendor profile discovery and sync contracts."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

import virginia_clemm_poe.updater as module
from virginia_clemm_poe import vendors
from virginia_clemm_poe.bots import ApiPricing, Architecture, BotCollection, BotInfo, PoeBot
from virginia_clemm_poe.updater import BotUpdater
from virginia_clemm_poe.utils.validation import get_bot_schema
from virginia_clemm_poe.vendors import load_vendors, parse_profile, scrape_profile


def profile_html(nodes, count=None):
    user = {
        "handle": "anthropic",
        "createdBotCount": count if count is not None else len(nodes),
        "createdBotsConnection": {"edges": [{"node": n} for n in nodes]},
    }
    payload = {"props": {"pageProps": {"data": {"mainQuery": {"user": user}}}}}
    return f"<script id=__NEXT_DATA__ type=application/json>{json.dumps(payload)}</script>"


def test_vendor_file_contains_all_requested_handles():
    handles = load_vendors()
    assert len(handles) == 28, "Every requested vendor must be shipped"
    assert "xAI" in handles and "OpenSourceLab" in handles, "Handle casing must be retained"


def test_profile_extracts_created_bots_only_and_records_unknown_metadata():
    html = profile_html(
        [{"handle": "New-Bot", "description": "New description"}, {"handle": "Deleted", "deletionState": "deleted"}]
    )
    bots, count = parse_profile(html, "anthropic")
    assert [b.id for b in bots] == ["New-Bot"], "Deleted bots should not be discovered"
    assert count == 2, "Advertised profile count must be retained for pagination"
    assert bots[0].created is None and bots[0].api_last_updated is None, "Do not invent API metadata"
    assert bots[0].vendor_profile == "anthropic", "Discovery provenance must be persisted"


def test_profile_rejects_wrong_user_and_login_page():
    for html in ["<html>Sign in</html>", profile_html([]).replace("anthropic", "other")]:
        with pytest.raises(ValueError):
            parse_profile(html, "anthropic")


@pytest.mark.asyncio
async def test_profile_scrolls_until_all_bots_are_loaded():
    page = MagicMock()
    page.goto = AsyncMock()
    page.content = AsyncMock(
        side_effect=[
            profile_html([{"handle": "First"}], 2),
            profile_html([{"handle": "First"}, {"handle": "Second"}], 2),
        ]
    )
    page.evaluate = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    bots = await scrape_profile(page, "anthropic")
    assert len(bots) == 2, "Discovery must include bots beyond the first page"
    page.evaluate.assert_awaited()


@pytest.mark.asyncio
async def test_incomplete_profile_fails_instead_of_silently_truncating():
    page = MagicMock(
        goto=AsyncMock(),
        content=AsyncMock(return_value=profile_html([{"handle": "First"}], 2)),
        evaluate=AsyncMock(),
        wait_for_timeout=AsyncMock(),
    )
    with pytest.raises(ValueError, match="Incomplete"):
        await scrape_profile(page, "anthropic")


def test_vendor_merge_keeps_api_metadata_and_old_scraped_data():
    api = PoeBot(
        id="new-bot",
        created=123,
        owned_by="api",
        root="new-bot",
        architecture=Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text"),
    )
    discovered, _ = parse_profile(
        profile_html([{"handle": "New-Bot", "description": "Vendor description"}]), "anthropic"
    )
    updater = BotUpdater("key")
    merged = updater._merge_vendor_bots([api], discovered, None, set())
    assert len(merged) == 1 and merged[0].created == 123, "Case variants must not duplicate API bots"
    assert merged[0].vendor_profile == "anthropic", "API bots should retain vendor provenance"
    assert merged[0].bot_info.creator == "@anthropic", "Profile creators should enrich API metadata"
    assert merged[0].bot_info.description == "Vendor description", "Profile metadata should seed scraping"


def test_failed_vendor_retains_previously_discovered_bots():
    bots, _ = parse_profile(profile_html([{"handle": "Old"}]), "anthropic")
    updater = BotUpdater("key")
    merged = updater._merge_vendor_bots([], [], BotCollection(data=bots), {"anthropic"})
    assert [b.id for b in merged] == ["Old"], "A failed profile scrape must not delete its bots"
    assert updater._merge_vendor_bots([], [], BotCollection(data=bots), set()) == [], (
        "Successful empty profiles remove stale bots"
    )


@pytest.mark.asyncio
async def test_sync_includes_vendor_bots_and_persists_their_pricing(monkeypatch, tmp_path):
    updater = BotUpdater("key")
    discovered, _ = parse_profile(profile_html([{"handle": "Only-Web"}]), "anthropic")
    updater._fetch_and_parse_api_bots = AsyncMock(return_value=({"object": "list"}, []))
    updater._discover_vendor_bots = AsyncMock(return_value=(discovered, set()))
    updater.scrape_model_info = AsyncMock(
        return_value=({"Total cost": ["$0.00/message", "0 points/message"]}, BotInfo(creator="@anthropic"), None)
    )
    page = MagicMock()
    pool = MagicMock()
    pool.acquire_page.return_value.__aenter__ = AsyncMock(return_value=page)
    pool.acquire_page.return_value.__aexit__ = AsyncMock(return_value=False)
    monkeypatch.setattr(module, "get_global_pool", AsyncMock(return_value=pool))
    monkeypatch.setattr(module, "DATA_FILE_PATH", tmp_path / "bots.json")
    collection = await updater.sync_bots()
    bot = collection.data[0]
    assert bot.id == "Only-Web" and bot.pricing.scraped.details.total_cost == "0 points/message", (
        "Vendor bots must go through normal pricing updates"
    )
    saved = BotCollection.model_validate_json((tmp_path / "bots.json").read_text())
    assert saved.data[0].vendor_profile == "anthropic", "Vendor provenance must survive serialization"
    assert bot.has_api_pricing() is False, "Web pricing must not be represented as API pricing"


@pytest.mark.asyncio
async def test_discovery_continues_after_one_vendor_fails(monkeypatch):
    updater = BotUpdater("key")
    bots, _ = parse_profile(profile_html([{"handle": "Works"}]), "anthropic")
    monkeypatch.setattr(module, "load_vendors", lambda: ["broken", "anthropic"])
    monkeypatch.setattr(module, "scrape_profile", AsyncMock(side_effect=[ValueError("Unavailable"), bots]))
    pool = MagicMock()
    pool.acquire_page.return_value.__aenter__ = AsyncMock(return_value=MagicMock())
    pool.acquire_page.return_value.__aexit__ = AsyncMock(return_value=False)
    discovered, failed = await updater._discover_vendor_bots(pool)
    assert failed == {"broken"} and discovered == bots, "One failed vendor must not cancel other profiles"


def test_vendor_bot_losing_api_access_clears_api_pricing(sample_poe_model):
    sample_poe_model.pricing.api = ApiPricing(prompt="0.01")
    sample_poe_model.vendor_profile = "anthropic"
    discovered, _ = parse_profile(profile_html([{"handle": sample_poe_model.id}]), "anthropic")
    merged = BotUpdater("key")._merge_vendor_bots([], discovered, BotCollection(data=[sample_poe_model]), set())
    assert merged[0].pricing.api is None and merged[0].pricing.scraped is not None, (
        "Lost API membership must clear API prices and retain web pricing"
    )


def test_vendor_file_rejects_urls(monkeypatch, tmp_path):
    path = tmp_path / "vendors.txt"
    path.write_text("https://poe.com/anthropic\n")
    monkeypatch.setattr(vendors, "VENDOR_FILE", path)
    with pytest.raises(ValueError, match="handles"):
        load_vendors()


@pytest.mark.asyncio
async def test_profile_http_failure_is_reported():
    page = MagicMock(goto=AsyncMock(return_value=MagicMock(status=404)))
    with pytest.raises(ValueError, match="HTTP 404"):
        await scrape_profile(page, "anthropic")


def test_vendor_records_match_persisted_data_schema():
    schema = get_bot_schema()["properties"]["data"]["items"]["properties"]
    assert "null" in schema["created"]["type"], "Unknown creation timestamps must be accepted"
    assert schema["object"]["enum"] == ["model", "bot"], "Persisted API and web bots both need schema support"
    assert schema["architecture"]["properties"]["input_modalities"]["minItems"] == 0, (
        "Unknown modalities must be accepted"
    )


def test_rendered_created_panel_adds_paginated_bots():
    html = profile_html([{"handle": "First"}], 2)
    html += (
        '<div id="profile-created-bots"><div data-bot-list-item><div class="botName">Second</div>'
        '<div class="botDescription">Page two</div></div></div>'
    )
    bots, count = parse_profile(html, "anthropic")
    assert len(bots) == count == 2 and bots[1].bot_info.description == "Page two", (
        "Rendered cards must extend hydration data"
    )
