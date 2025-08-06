# this_file: tests/test_models.py
"""Tests for Pydantic data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from virginia_clemm_poe.models import Architecture, BotInfo, ModelCollection, PoeModel, Pricing, PricingDetails


class TestArchitecture:
    """Test Architecture model validation and functionality."""

    def test_valid_architecture_creation(self, sample_architecture: Architecture) -> None:
        """Test creating a valid Architecture instance."""
        assert sample_architecture.input_modalities == ["text"]
        assert sample_architecture.output_modalities == ["text"]
        assert sample_architecture.modality == "text->text"

    def test_multimodal_architecture(self) -> None:
        """Test creating a multimodal architecture."""
        arch = Architecture(input_modalities=["text", "image"], output_modalities=["text"], modality="multimodal->text")
        assert "text" in arch.input_modalities
        assert "image" in arch.input_modalities
        assert arch.output_modalities == ["text"]


class TestPricingDetails:
    """Test PricingDetails model validation and functionality."""

    def test_valid_pricing_details_creation(self, sample_pricing_details: PricingDetails) -> None:
        """Test creating valid pricing details."""
        assert sample_pricing_details.input_text == "10 points/1k tokens"
        assert sample_pricing_details.bot_message == "5 points/message"
        assert sample_pricing_details.initial_points_cost == "100 points"

    def test_pricing_details_with_aliases(self) -> None:
        """Test PricingDetails with field aliases from scraped data."""
        # Test using the alias names as they appear on Poe.com
        pricing = PricingDetails(
            **{
                "Input (text)": "15 points/1k tokens",
                "Bot message": "8 points/message",
                "Chat history": "2 points/message",
            }
        )
        assert pricing.input_text == "15 points/1k tokens"
        assert pricing.bot_message == "8 points/message"
        assert pricing.chat_history == "2 points/message"

    def test_pricing_details_partial_data(self) -> None:
        """Test PricingDetails with only some fields populated."""
        pricing = PricingDetails(total_cost="500 points")
        assert pricing.total_cost == "500 points"
        assert pricing.input_text is None
        assert pricing.bot_message is None

    def test_pricing_details_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed for future compatibility."""
        pricing = PricingDetails(
            **{
                "Input (text)": "10 points/1k tokens",
                "Custom Field": "custom value",  # Extra field should be allowed
            }
        )
        assert pricing.input_text == "10 points/1k tokens"


class TestBotInfo:
    """Test BotInfo model validation and functionality."""

    def test_valid_bot_info_creation(self, sample_bot_info: BotInfo) -> None:
        """Test creating valid bot info."""
        assert sample_bot_info.creator == "@testcreator"
        assert "test bot" in sample_bot_info.description.lower()
        assert "powered by" in sample_bot_info.description_extra.lower()

    def test_bot_info_optional_fields(self) -> None:
        """Test BotInfo with optional fields as None."""
        bot_info = BotInfo()
        assert bot_info.creator is None
        assert bot_info.description is None
        assert bot_info.description_extra is None

    def test_bot_info_partial_data(self) -> None:
        """Test BotInfo with only some fields populated."""
        bot_info = BotInfo(creator="@openai")
        assert bot_info.creator == "@openai"
        assert bot_info.description is None


class TestPoeModel:
    """Test PoeModel validation and functionality."""

    def test_valid_poe_model_creation(self, sample_poe_model: PoeModel) -> None:
        """Test creating a valid PoeModel instance."""
        assert sample_poe_model.id == "test-model-1"
        assert sample_poe_model.object == "model"
        assert sample_poe_model.owned_by == "testorg"
        assert sample_poe_model.root == "test-model-1"
        assert sample_poe_model.has_pricing()

    def test_poe_model_without_pricing(self, sample_architecture: Architecture) -> None:
        """Test PoeModel without pricing data."""
        model = PoeModel(
            id="no-pricing-model",
            created=1704369600,
            owned_by="testorg",
            root="no-pricing-model",
            architecture=sample_architecture,
        )
        assert not model.has_pricing()
        assert model.needs_pricing_update()
        assert model.get_primary_cost() is None

    def test_poe_model_needs_pricing_update(self, sample_poe_model: PoeModel) -> None:
        """Test pricing update logic."""
        # Model with pricing should not need update
        assert not sample_poe_model.needs_pricing_update()

        # Model with pricing error should need update
        sample_poe_model.pricing_error = "Failed to scrape"
        assert sample_poe_model.needs_pricing_update()

    def test_get_primary_cost_priority(self, sample_architecture: Architecture) -> None:
        """Test primary cost extraction priority order."""
        pricing_details = PricingDetails(
            input_text="10 points/1k tokens", total_cost="500 points", per_message="15 points/message"
        )
        pricing = Pricing(checked_at=datetime.now(), details=pricing_details)
        model = PoeModel(
            id="cost-test-model",
            created=1704369600,
            owned_by="testorg",
            root="cost-test-model",
            architecture=sample_architecture,
            pricing=pricing,
        )

        # Should prioritize input_text over other options
        assert model.get_primary_cost() == "10 points/1k tokens"

    def test_model_validation_errors(self, sample_architecture: Architecture) -> None:
        """Test model validation catches required field errors."""
        with pytest.raises(ValidationError):
            PoeModel(architecture=sample_architecture)  # Missing required fields


class TestModelCollection:
    """Test ModelCollection functionality."""

    def test_valid_model_collection_creation(self, sample_model_collection: ModelCollection) -> None:
        """Test creating a valid ModelCollection."""
        assert sample_model_collection.object == "list"
        assert len(sample_model_collection.data) == 1
        assert sample_model_collection.data[0].id == "test-model-1"

    def test_get_by_id_found(self, sample_model_collection: ModelCollection) -> None:
        """Test getting a model by ID when it exists."""
        model = sample_model_collection.get_by_id("test-model-1")
        assert model is not None
        assert model.id == "test-model-1"

    def test_get_by_id_not_found(self, sample_model_collection: ModelCollection) -> None:
        """Test getting a model by ID when it doesn't exist."""
        model = sample_model_collection.get_by_id("nonexistent-model")
        assert model is None

    def test_search_by_id(self, sample_model_collection: ModelCollection) -> None:
        """Test searching models by ID."""
        results = sample_model_collection.search("test-model")
        assert len(results) == 1
        assert results[0].id == "test-model-1"

    def test_search_case_insensitive(self, sample_model_collection: ModelCollection) -> None:
        """Test that search is case insensitive."""
        results = sample_model_collection.search("TEST-MODEL")
        assert len(results) == 1
        assert results[0].id == "test-model-1"

    def test_search_no_results(self, sample_model_collection: ModelCollection) -> None:
        """Test search with no matching results."""
        results = sample_model_collection.search("nonexistent")
        assert len(results) == 0

    def test_empty_collection(self) -> None:
        """Test operations on empty collection."""
        collection = ModelCollection(data=[])
        assert len(collection.data) == 0
        assert collection.get_by_id("any-id") is None
        assert len(collection.search("any-query")) == 0
