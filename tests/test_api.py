# this_file: tests/test_api.py
"""Tests for public API functions."""

import json
from pathlib import Path
from unittest.mock import patch

from virginia_clemm_poe import api
from virginia_clemm_poe.bots import BotCollection


class TestLoadModels:
    """Test load_bots function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_load_bots_success(self, mock_data_file: Path, sample_bot_collection: BotCollection) -> None:
        """Test successfully loading bots from file."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            bots = api.load_bots()

        assert isinstance(bots, BotCollection)
        assert len(bots.data) == 1
        assert bots.data[0].id == "test-bot-1"

    def test_load_bots_file_not_found(self, tmp_path: Path) -> None:
        """Test loading bots when file doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.json"

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", nonexistent_file):
            bots = api.load_bots()

        # Should return empty collection, not raise exception
        assert isinstance(bots, BotCollection)
        assert len(bots.data) == 0

    def test_load_bots_invalid_json(self, tmp_path: Path) -> None:
        """Test loading bots with invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", invalid_file):
            bots = api.load_bots()

        # Should return empty collection on JSON parse error
        assert isinstance(bots, BotCollection)
        assert len(bots.data) == 0

    def test_load_bots_invalid_data_structure(self, tmp_path: Path) -> None:
        """Test loading bots with invalid data structure."""
        invalid_file = tmp_path / "invalid_structure.json"
        invalid_file.write_text('{"wrong": "structure"}')

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", invalid_file):
            bots = api.load_bots()

        # Should return empty collection on validation error
        assert isinstance(bots, BotCollection)
        assert len(bots.data) == 0


class TestGetModelById:
    """Test get_bot_by_id function."""

    def test_get_bot_by_id_found(self, mock_data_file: Path) -> None:
        """Test getting an existing bot by ID."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            bot = api.get_bot_by_id("test-bot-1")

        assert bot is not None
        assert bot.id == "test-bot-1"
        assert bot.owned_by == "testorg"

    def test_get_bot_by_id_not_found(self, mock_data_file: Path) -> None:
        """Test getting a non-existent bot by ID."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            bot = api.get_bot_by_id("nonexistent-bot")

        assert bot is None

    def test_get_bot_by_id_empty_string(self, mock_data_file: Path) -> None:
        """Test getting bot with empty string ID."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            bot = api.get_bot_by_id("")

        assert bot is None


class TestSearchModels:
    """Test search_bots function."""

    def test_search_bots_found(self, mock_data_file: Path) -> None:
        """Test searching for bots with matching results."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_bots("test-bot")

        assert len(results) == 1
        assert results[0].id == "test-bot-1"

    def test_search_bots_case_insensitive(self, mock_data_file: Path) -> None:
        """Test that search is case insensitive."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_bots("TEST-MODEL")

        assert len(results) == 1
        assert results[0].id == "test-bot-1"

    def test_search_bots_no_results(self, mock_data_file: Path) -> None:
        """Test searching with no matching results."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_bots("nonexistent")

        assert len(results) == 0

    def test_search_bots_empty_query(self, mock_data_file: Path) -> None:
        """Test searching with empty query string."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_bots("")

        # Empty query matches all bots (since empty string is "in" every string)
        assert len(results) == 1


class TestGetModelsWithPricing:
    """Test get_bots_with_pricing function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_get_bots_with_pricing(self, mock_data_file: Path) -> None:
        """Test getting bots that have pricing information."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            bots = api.get_bots_with_pricing()

        assert len(bots) == 1
        assert bots[0].has_pricing()
        assert bots[0].pricing is not None

    def test_get_bots_with_pricing_empty_result(self, tmp_path: Path) -> None:
        """Test getting bots with pricing when none have pricing."""
        # Create a bot collection without pricing
        no_pricing_data = {
            "object": "list",
            "data": [
                {
                    "id": "no-pricing-bot",
                    "object": "bot",
                    "created": 1704369600,
                    "owned_by": "testorg",
                    "permission": [],
                    "root": "no-pricing-bot",
                    "architecture": {
                        "input_modalities": ["text"],
                        "output_modalities": ["text"],
                        "modality": "text->text",
                    },
                    # No pricing field
                }
            ],
        }

        no_pricing_file = tmp_path / "no_pricing.json"
        with open(no_pricing_file, "w") as f:
            json.dump(no_pricing_data, f)

        # Clear cache to ensure fresh load
        api._collection = None

        # Force reload to bypass cache
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", no_pricing_file):
            bots = api.get_bots_with_pricing()

        assert len(bots) == 0


class TestGetAllModels:
    """Test get_all_bots function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_get_all_bots(self, mock_data_file: Path) -> None:
        """Test getting all bots."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            bots = api.get_all_bots()

        assert len(bots) == 1
        assert bots[0].id == "test-bot-1"

    def test_get_all_bots_empty_collection(self, tmp_path: Path) -> None:
        """Test getting all bots from empty collection."""
        empty_data = {"object": "list", "data": []}
        empty_file = tmp_path / "empty.json"
        with open(empty_file, "w") as f:
            json.dump(empty_data, f)

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", empty_file):
            bots = api.get_all_bots()

        assert len(bots) == 0


class TestGetModelsNeedingUpdate:
    """Test get_bots_needing_update function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_get_bots_needing_update_no_pricing(self, tmp_path: Path) -> None:
        """Test getting bots that need pricing updates."""
        # Create bot without pricing
        no_pricing_data = {
            "object": "list",
            "data": [
                {
                    "id": "needs-update-bot",
                    "object": "bot",
                    "created": 1704369600,
                    "owned_by": "testorg",
                    "permission": [],
                    "root": "needs-update-bot",
                    "architecture": {
                        "input_modalities": ["text"],
                        "output_modalities": ["text"],
                        "modality": "text->text",
                    },
                }
            ],
        }

        no_pricing_file = tmp_path / "needs_update.json"
        with open(no_pricing_file, "w") as f:
            json.dump(no_pricing_data, f)

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", no_pricing_file):
            bots = api.get_bots_needing_update()

        assert len(bots) == 1
        assert bots[0].needs_pricing_update()

    def test_get_bots_needing_update_with_errors(self, tmp_path: Path) -> None:
        """Test getting bots with pricing errors."""
        error_data = {
            "object": "list",
            "data": [
                {
                    "id": "error-bot",
                    "object": "bot",
                    "created": 1704369600,
                    "owned_by": "testorg",
                    "permission": [],
                    "root": "error-bot",
                    "architecture": {
                        "input_modalities": ["text"],
                        "output_modalities": ["text"],
                        "modality": "text->text",
                    },
                    "pricing_error": "Failed to scrape pricing",
                }
            ],
        }

        error_file = tmp_path / "error_models.json"
        with open(error_file, "w") as f:
            json.dump(error_data, f)

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", error_file):
            bots = api.get_bots_needing_update()

        assert len(bots) == 1
        assert bots[0].needs_pricing_update()
        assert bots[0].pricing_error == "Failed to scrape pricing"


class TestReloadModels:
    """Test reload_bots function."""

    def test_reload_bots_cache_invalidation(self, mock_data_file: Path) -> None:
        """Test that reload_bots invalidates cache."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            # Load bots to populate cache
            models1 = api.load_bots()
            assert len(models1.data) == 1

            # Reload should work (testing that it doesn't raise errors)
            api.reload_bots()

            # Load again to verify it still works
            models2 = api.load_bots()
            assert len(models2.data) == 1

    @patch("virginia_clemm_poe.api._collection", None)
    def test_reload_bots_no_cache(self) -> None:
        """Test reload_bots when no cache exists."""
        # Should not raise any errors even when cache is None
        api.reload_bots()
