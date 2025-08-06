# this_file: tests/test_api.py
"""Tests for public API functions."""

import json
from pathlib import Path
from unittest.mock import patch

from virginia_clemm_poe import api
from virginia_clemm_poe.models import ModelCollection


class TestLoadModels:
    """Test load_models function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_load_models_success(self, mock_data_file: Path, sample_model_collection: ModelCollection) -> None:
        """Test successfully loading models from file."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            models = api.load_models()

        assert isinstance(models, ModelCollection)
        assert len(models.data) == 1
        assert models.data[0].id == "test-model-1"

    def test_load_models_file_not_found(self, tmp_path: Path) -> None:
        """Test loading models when file doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.json"

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", nonexistent_file):
            models = api.load_models()

        # Should return empty collection, not raise exception
        assert isinstance(models, ModelCollection)
        assert len(models.data) == 0

    def test_load_models_invalid_json(self, tmp_path: Path) -> None:
        """Test loading models with invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", invalid_file):
            models = api.load_models()

        # Should return empty collection on JSON parse error
        assert isinstance(models, ModelCollection)
        assert len(models.data) == 0

    def test_load_models_invalid_data_structure(self, tmp_path: Path) -> None:
        """Test loading models with invalid data structure."""
        invalid_file = tmp_path / "invalid_structure.json"
        invalid_file.write_text('{"wrong": "structure"}')

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", invalid_file):
            models = api.load_models()

        # Should return empty collection on validation error
        assert isinstance(models, ModelCollection)
        assert len(models.data) == 0


class TestGetModelById:
    """Test get_model_by_id function."""

    def test_get_model_by_id_found(self, mock_data_file: Path) -> None:
        """Test getting an existing model by ID."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            model = api.get_model_by_id("test-model-1")

        assert model is not None
        assert model.id == "test-model-1"
        assert model.owned_by == "testorg"

    def test_get_model_by_id_not_found(self, mock_data_file: Path) -> None:
        """Test getting a non-existent model by ID."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            model = api.get_model_by_id("nonexistent-model")

        assert model is None

    def test_get_model_by_id_empty_string(self, mock_data_file: Path) -> None:
        """Test getting model with empty string ID."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            model = api.get_model_by_id("")

        assert model is None


class TestSearchModels:
    """Test search_models function."""

    def test_search_models_found(self, mock_data_file: Path) -> None:
        """Test searching for models with matching results."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_models("test-model")

        assert len(results) == 1
        assert results[0].id == "test-model-1"

    def test_search_models_case_insensitive(self, mock_data_file: Path) -> None:
        """Test that search is case insensitive."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_models("TEST-MODEL")

        assert len(results) == 1
        assert results[0].id == "test-model-1"

    def test_search_models_no_results(self, mock_data_file: Path) -> None:
        """Test searching with no matching results."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_models("nonexistent")

        assert len(results) == 0

    def test_search_models_empty_query(self, mock_data_file: Path) -> None:
        """Test searching with empty query string."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            results = api.search_models("")

        # Empty query matches all models (since empty string is "in" every string)
        assert len(results) == 1


class TestGetModelsWithPricing:
    """Test get_models_with_pricing function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_get_models_with_pricing(self, mock_data_file: Path) -> None:
        """Test getting models that have pricing information."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            models = api.get_models_with_pricing()

        assert len(models) == 1
        assert models[0].has_pricing()
        assert models[0].pricing is not None

    def test_get_models_with_pricing_empty_result(self, tmp_path: Path) -> None:
        """Test getting models with pricing when none have pricing."""
        # Create a model collection without pricing
        no_pricing_data = {
            "object": "list",
            "data": [
                {
                    "id": "no-pricing-model",
                    "object": "model",
                    "created": 1704369600,
                    "owned_by": "testorg",
                    "permission": [],
                    "root": "no-pricing-model",
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
            models = api.get_models_with_pricing()

        assert len(models) == 0


class TestGetAllModels:
    """Test get_all_models function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_get_all_models(self, mock_data_file: Path) -> None:
        """Test getting all models."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            models = api.get_all_models()

        assert len(models) == 1
        assert models[0].id == "test-model-1"

    def test_get_all_models_empty_collection(self, tmp_path: Path) -> None:
        """Test getting all models from empty collection."""
        empty_data = {"object": "list", "data": []}
        empty_file = tmp_path / "empty.json"
        with open(empty_file, "w") as f:
            json.dump(empty_data, f)

        # Clear cache to ensure fresh load
        api._collection = None

        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", empty_file):
            models = api.get_all_models()

        assert len(models) == 0


class TestGetModelsNeedingUpdate:
    """Test get_models_needing_update function."""

    def setup_method(self) -> None:
        """Clear global cache before each test."""
        api._collection = None

    def test_get_models_needing_update_no_pricing(self, tmp_path: Path) -> None:
        """Test getting models that need pricing updates."""
        # Create model without pricing
        no_pricing_data = {
            "object": "list",
            "data": [
                {
                    "id": "needs-update-model",
                    "object": "model",
                    "created": 1704369600,
                    "owned_by": "testorg",
                    "permission": [],
                    "root": "needs-update-model",
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
            models = api.get_models_needing_update()

        assert len(models) == 1
        assert models[0].needs_pricing_update()

    def test_get_models_needing_update_with_errors(self, tmp_path: Path) -> None:
        """Test getting models with pricing errors."""
        error_data = {
            "object": "list",
            "data": [
                {
                    "id": "error-model",
                    "object": "model",
                    "created": 1704369600,
                    "owned_by": "testorg",
                    "permission": [],
                    "root": "error-model",
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
            models = api.get_models_needing_update()

        assert len(models) == 1
        assert models[0].needs_pricing_update()
        assert models[0].pricing_error == "Failed to scrape pricing"


class TestReloadModels:
    """Test reload_models function."""

    def test_reload_models_cache_invalidation(self, mock_data_file: Path) -> None:
        """Test that reload_models invalidates cache."""
        with patch("virginia_clemm_poe.api.DATA_FILE_PATH", mock_data_file):
            # Load models to populate cache
            models1 = api.load_models()
            assert len(models1.data) == 1

            # Reload should work (testing that it doesn't raise errors)
            api.reload_models()

            # Load again to verify it still works
            models2 = api.load_models()
            assert len(models2.data) == 1

    @patch("virginia_clemm_poe.api._collection", None)
    def test_reload_models_no_cache(self) -> None:
        """Test reload_models when no cache exists."""
        # Should not raise any errors even when cache is None
        api.reload_models()
