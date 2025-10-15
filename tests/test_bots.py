# this_file: tests/test_bots.py
"""Tests for Pydantic bot data structures."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from virginia_clemm_poe.bots import (
    Architecture,
    BotCollection,
    BotInfo,
    PoeBot,
    Pricing,
    PricingDetails,
    UnifiedPricing,
)


class TestArchitecture:
    """Test Architecture bot validation and functionality."""

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
    """Test PricingDetails bot validation and functionality."""

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
    """Test BotInfo bot validation and functionality."""

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


class TestPoeBot:
    """Test PoeBot validation and functionality."""

    def test_valid_poe_model_creation(self, sample_poe_model: PoeBot) -> None:
        """Test creating a valid PoeBot instance."""
        assert sample_poe_model.id == "test-bot-1"
        assert sample_poe_model.object == "bot"
        assert sample_poe_model.owned_by == "testorg"
        assert sample_poe_model.root == "test-bot-1"
        assert sample_poe_model.has_pricing()

    def test_poe_model_without_pricing(self, sample_architecture: Architecture) -> None:
        """Test PoeBot without pricing data."""
        bot = PoeBot(
            id="no-pricing-bot",
            created=1704369600,
            owned_by="testorg",
            root="no-pricing-bot",
            architecture=sample_architecture,
        )
        assert not bot.has_pricing()
        assert bot.needs_pricing_update()
        assert bot.get_primary_cost() is None

    def test_poe_model_needs_pricing_update(self, sample_poe_model: PoeBot) -> None:
        """Test pricing update logic."""
        # Bot with pricing should not need update
        assert not sample_poe_model.needs_pricing_update()

        # Bot with pricing error should need update
        sample_poe_model.pricing_error = "Failed to scrape"
        assert sample_poe_model.needs_pricing_update()

    def test_get_primary_cost_priority(self, sample_architecture: Architecture) -> None:
        """Test primary cost extraction priority order."""
        pricing_details = PricingDetails(
            input_text="10 points/1k tokens", total_cost="500 points", per_message="15 points/message"
        )
        pricing = Pricing(checked_at=datetime.now(), details=pricing_details)
        bot = PoeBot(
            id="cost-test-bot",
            created=1704369600,
            owned_by="testorg",
            root="cost-test-bot",
            architecture=sample_architecture,
            pricing=UnifiedPricing(scraped=pricing),
        )

        # Should prioritize input_text over other options
        assert bot.get_primary_cost() == "10 points/1k tokens"

    def test_model_validation_errors(self, sample_architecture: Architecture) -> None:
        """Test bot validation catches required field errors."""
        with pytest.raises(ValidationError):
            PoeBot(architecture=sample_architecture)  # Missing required fields


class TestBotCollection:
    """Test BotCollection functionality."""

    def test_valid_model_collection_creation(self, sample_bot_collection: BotCollection) -> None:
        """Test creating a valid BotCollection."""
        assert sample_bot_collection.object == "list"
        assert len(sample_bot_collection.data) == 1
        assert sample_bot_collection.data[0].id == "test-bot-1"

    def test_get_by_id_found(self, sample_bot_collection: BotCollection) -> None:
        """Test getting a bot by ID when it exists."""
        bot = sample_bot_collection.get_by_id("test-bot-1")
        assert bot is not None
        assert bot.id == "test-bot-1"

    def test_get_by_id_not_found(self, sample_bot_collection: BotCollection) -> None:
        """Test getting a bot by ID when it doesn't exist."""
        bot = sample_bot_collection.get_by_id("nonexistent-bot")
        assert bot is None

    def test_search_by_id(self, sample_bot_collection: BotCollection) -> None:
        """Test searching bots by ID."""
        results = sample_bot_collection.search("test-bot")
        assert len(results) == 1
        assert results[0].id == "test-bot-1"

    def test_search_case_insensitive(self, sample_bot_collection: BotCollection) -> None:
        """Test that search is case insensitive."""
        results = sample_bot_collection.search("TEST-MODEL")
        assert len(results) == 1
        assert results[0].id == "test-bot-1"

    def test_search_no_results(self, sample_bot_collection: BotCollection) -> None:
        """Test search with no matching results."""
        results = sample_bot_collection.search("nonexistent")
        assert len(results) == 0

    def test_empty_collection(self) -> None:
        """Test operations on empty collection."""
        collection = BotCollection(data=[])
        assert len(collection.data) == 0
        assert collection.get_by_id("any-id") is None
        assert len(collection.search("any-query")) == 0

    def test_sort_by_api_last_updated_orders_oldest_first(self, sample_architecture: Architecture) -> None:
        """Bots should sort by oldest API update timestamp first."""
        now = datetime(2025, 1, 1, 12, 0, 0)
        older = PoeBot(
            id="older-bot",
            created=1700000000,
            owned_by="org",
            root="older-bot",
            architecture=sample_architecture,
            api_last_updated=now - timedelta(days=2),
        )
        newest = PoeBot(
            id="newer-bot",
            created=1700000100,
            owned_by="org",
            root="newer-bot",
            architecture=sample_architecture,
            api_last_updated=now,
        )
        missing = PoeBot(
            id="missing-timestamp",
            created=1700000200,
            owned_by="org",
            root="missing-timestamp",
            architecture=sample_architecture,
        )

        collection = BotCollection(data=[newest, missing, older])
        collection.sort_by_api_last_updated()

        ordered_ids = [bot.id for bot in collection.data]
        assert ordered_ids == ["missing-timestamp", "older-bot", "newer-bot"], "Expected oldest timestamps first"
