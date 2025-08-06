# this_file: tests/conftest.py
"""Shared test fixtures and configuration for Virginia Clemm Poe tests."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from virginia_clemm_poe.models import Architecture, BotInfo, ModelCollection, PoeModel, Pricing, PricingDetails


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
def sample_poe_model(sample_architecture: Architecture, sample_pricing: Pricing, sample_bot_info: BotInfo) -> PoeModel:
    """Sample PoeModel for testing."""
    return PoeModel(
        id="test-model-1",
        object="model",
        created=1704369600,  # 2024-01-04 12:00:00 UTC
        owned_by="testorg",
        permission=[],
        root="test-model-1",
        architecture=sample_architecture,
        pricing=sample_pricing,
        bot_info=sample_bot_info,
    )


@pytest.fixture
def sample_model_collection(sample_poe_model: PoeModel) -> ModelCollection:
    """Sample ModelCollection for testing."""
    return ModelCollection(object="list", data=[sample_poe_model])


@pytest.fixture
def sample_api_response_data() -> dict[str, Any]:
    """Sample API response data matching Poe API format."""
    return {
        "object": "list",
        "data": [
            {
                "id": "test-model-1",
                "object": "model",
                "created": 1704369600,
                "owned_by": "testorg",
                "permission": [],
                "root": "test-model-1",
                "parent": None,
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"], "modality": "text->text"},
            }
        ],
    }


@pytest.fixture
def mock_data_file(tmp_path: Path, sample_model_collection: ModelCollection) -> Path:
    """Create a temporary data file for testing."""
    data_file = tmp_path / "test_models.json"
    with open(data_file, "w") as f:
        json.dump(sample_model_collection.model_dump(), f, indent=2, default=str)
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
