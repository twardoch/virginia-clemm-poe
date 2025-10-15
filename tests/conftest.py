# this_file: tests/conftest.py
"""Shared test fixtures and configuration for Virginia Clemm Poe tests."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from virginia_clemm_poe.bots import (
    Architecture,
    BotCollection,
    BotInfo,
    PoeBot,
    ScrapedPricing,
    ScrapedPricingDetails,
    UnifiedPricing,
)

# Aliases for backward compatibility in tests
Pricing = ScrapedPricing
PricingDetails = ScrapedPricingDetails


@pytest.fixture
def sample_architecture() -> Architecture:
    """Sample architecture data for testing."""
    return Architecture(input_modalities=["text"], output_modalities=["text"], modality="text->text")


@pytest.fixture
def sample_pricing_details() -> PricingDetails:
    """Sample pricing details for testing."""
    return PricingDetails(
        input_text="10 points/1k tokens", bot_message="5 points/message", initial_points_cost="100 points"
    )


@pytest.fixture
def sample_pricing(sample_pricing_details: PricingDetails) -> Pricing:
    """Sample pricing with timestamp for testing."""
    return Pricing(checked_at=datetime.fromisoformat("2025-08-04T12:00:00"), details=sample_pricing_details)


@pytest.fixture
def sample_bot_info() -> BotInfo:
    """Sample bot info for testing."""
    return BotInfo(
        creator="@testcreator",
        description="A test bot for demonstration purposes",
        description_extra="Powered by Test Framework",
    )


@pytest.fixture
def sample_unified_pricing(sample_pricing: Pricing) -> UnifiedPricing:
    """Sample unified pricing for testing."""
    return UnifiedPricing(scraped=sample_pricing)


@pytest.fixture
def sample_poe_model(
    sample_architecture: Architecture, sample_unified_pricing: UnifiedPricing, sample_bot_info: BotInfo
) -> PoeBot:
    """Sample PoeBot for testing."""
    return PoeBot(
        id="test-bot-1",
        object="bot",
        created=1704369600,  # 2024-01-04 12:00:00 UTC
        owned_by="testorg",
        permission=[],
        root="test-bot-1",
        architecture=sample_architecture,
        pricing=sample_unified_pricing,
        bot_info=sample_bot_info,
    )


@pytest.fixture
def sample_bot_collection(sample_poe_model: PoeBot) -> BotCollection:
    """Sample BotCollection for testing."""
    return BotCollection(object="list", data=[sample_poe_model])


@pytest.fixture
def sample_api_response_data() -> dict[str, Any]:
    """Sample API response data matching Poe API format."""
    return {
        "object": "list",
        "data": [
            {
                "id": "test-bot-1",
                "object": "bot",
                "created": 1704369600,
                "owned_by": "testorg",
                "permission": [],
                "root": "test-bot-1",
                "parent": None,
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"], "modality": "text->text"},
            }
        ],
    }


@pytest.fixture
def mock_data_file(tmp_path: Path, sample_bot_collection: BotCollection) -> Path:
    """Create a temporary data file for testing."""
    data_file = tmp_path / "test_models.json"
    with open(data_file, "w") as f:
        json.dump(sample_bot_collection.model_dump(), f, indent=2, default=str)
    return data_file


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("POE_API_KEY", "test-api-key-12345")


# Test markers configuration
pytest_markers = [
    "unit: marks tests as unit tests (default)",
    "integration: marks tests as integration tests (require network/browser)",
    "slow: marks tests as slow (may take >5 seconds)",
]
