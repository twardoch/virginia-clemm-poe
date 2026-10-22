# this_file: tests/test_docs.py
"""Generated catalog pages preserve unknown metadata and literal descriptions."""

from pathlib import Path

from src_docs.update_docs import add_reference_prices, add_saved_modalities, generate_model_page, normalize_saved_rates


def test_vendor_description_does_not_create_unresolved_cross_references():
    page = generate_model_page({"id": "test-bot", "bot_info": {"description": "Use [verse] and [bridge]"}})
    assert r"Use \[verse\] and \[bridge\]" in page, "Bot instructions must not become documentation cross references"


def test_vendor_unknown_metadata_and_zero_rates_are_visible():
    page = generate_model_page(
        {
            "id": "test-bot",
            "created": None,
            "api_last_updated": None,
            "pricing": {"scraped": {"checked_at": "2026-10-05", "details": {"total_cost": "0 points/message"}}},
        }
    )
    assert "0 points/message" in page, "Zero prices must remain visible"
    assert "**Created:** Unknown" in page and "**API Last Updated:** Not listed in API" in page, (
        "Unknown API metadata must be explicit"
    )


def test_saved_rate_normalization_repairs_point_amounts_and_video_duration():
    model = {
        "id": "video",
        "pricing": {
            "scraped": {
                "details": {
                    "rate_card": "| Resolution | Duration | Points |\n|---|---|---|\n| 720p | 5s | 100 ($0.003) |"
                }
            }
        },
    }
    normalize_saved_rates(model)
    rates = model["pricing"]["scraped"]["details"]["rates"]
    assert len(rates) == 2 and all(r["quantity"] == "5" for r in rates), (
        "Offline card normalization retains points and duration"
    )


def test_reference_prices_assign_every_model_and_render_zero_api_rates():
    models = [
        {
            "id": "free",
            "pricing": {
                "api": {"prompt": 0, "completion": 0},
                "scraped": {"details": {"total_cost": "0 points/message"}},
            },
        },
        {"id": "unknown"},
    ]
    script = Path(__file__).resolve().parents[1] / "src_docs/md/price_compare.js"
    add_reference_prices(models, script)
    assert [model["pricing_tier"] for model in models] == [0, 9], "Every bot gets a tier, including unknown prices"
    page = generate_model_page(models[0])
    assert "**Tier 0:**" in page and "| Prompt | $0/token |" in page, (
        "Reference and literal zero dollar prices must render"
    )
    assert "**Tier 9:**" in generate_model_page(models[1]), "Unknown prices must also have a tier on their page"


def test_explicit_saved_output_media_extends_filter_metadata():
    model = {
        "architecture": {"output_modalities": ["text"]},
        "pricing": {"scraped": {"details": {"rates": [{"label": "Video Output", "unit": "second"}]}}},
    }
    add_saved_modalities(model)
    assert model["architecture"]["output_modalities"] == ["text", "video"], (
        "Saved output media must be discoverable in modality filters"
    )
    assert model["comparison_modalities_source"] == "saved_rate_card", "Derived metadata retains provenance"


def test_database_status_uses_latest_saved_observation_in_utc():
    from src_docs.update_docs import render_database_status

    status = render_database_status({"data": [
        {"api_last_updated": "2026-10-22T16:10:00+02:00"},
        {"pricing": {"scraped": {"checked_at": "2026-10-22 14:07:50.806556"}}},
    ]})
    assert 'datetime="2026-10-22T14:10:00Z"' in status, "Compare actual instants across timestamp formats"
    assert "22 October 2026, 14:10 UTC" in status, "Display an explicit date and timezone"
    assert "2 bots" in status and "1 with website prices" in status, "Display saved catalogue coverage"


def test_database_status_without_observations_does_not_invent_a_date():
    from src_docs.update_docs import render_database_status

    status = render_database_status({"data": [{"api_last_updated": None, "pricing": None}]})
    assert "Not recorded" in status and "<time" not in status, "Never use a rebuild time as data freshness"


def test_homepage_database_status_rebuild_replaces_one_block(tmp_path):
    from src_docs.update_docs import update_homepage_status

    home = tmp_path / "index.md"
    home.write_text("# Virginia Clemm Poe \n\nExisting content.\n")
    update_homepage_status(home, '<p class="database-status">Old date</p>')
    update_homepage_status(home, '<p class="database-status">New date</p>')
    first = home.read_text()
    update_homepage_status(home, '<p class="database-status">New date</p>')
    assert home.read_text() == first, "Rebuild must be idempotent"
    assert first.count('class="database-status"') == 1 and "Old date" not in first, "Replace stale status"
    assert first.startswith("# Virginia Clemm Poe") and "Existing content." in first, "Preserve the authored homepage"
