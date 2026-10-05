# this_file: tests/test_docs.py
"""Generated catalog pages preserve unknown metadata and literal descriptions."""

from src_docs.update_docs import generate_model_page


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
