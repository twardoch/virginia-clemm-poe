# this_file: src/virginia_clemm_poe/models.py

"""Pydantic models for Virginia Clemm Poe."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Architecture(BaseModel):
    """Model architecture information describing input/output capabilities.

    This model defines what types of data a Poe model can accept as input
    and produce as output (e.g., text, images, video).

    Attributes:
        input_modalities: List of supported input types (e.g., ["text", "image"])
        output_modalities: List of supported output types (e.g., ["text"])
        modality: Primary modality description (e.g., "text->text", "text->image")

    Example:
        ```python
        arch = Architecture(
            input_modalities=["text", "image"],
            output_modalities=["text"],
            modality="multimodal->text"
        )
        ```
    """

    input_modalities: list[str]
    output_modalities: list[str]
    modality: str


class PricingDetails(BaseModel):
    """Detailed pricing information scraped from Poe.com model pages.

    This model captures all possible pricing structures found on Poe.com,
    as different models use different pricing formats. The fields use aliases
    to match the exact text found on the website.

    Standard pricing fields are the most common, while alternative fields
    accommodate different model types and pricing structures.

    Attributes:
        input_text: Cost per input text tokens (e.g., "10 points/1k tokens")
        input_image: Cost per input image (e.g., "50 points/image")
        bot_message: Cost per bot response (e.g., "5 points/message")
        chat_history: Cost for accessing chat history
        chat_history_cache_discount: Discount rate for cached history
        total_cost: Flat rate cost (e.g., "100 points")
        image_output: Cost per generated image
        video_output: Cost per generated video
        text_input: Alternative text input pricing format
        per_message: Cost per message interaction
        finetuning: Cost for model fine-tuning
        initial_points_cost: Upfront cost from bot info card

    Note:
        Uses Field aliases to match exact website text.
        Extra fields are allowed for future pricing format compatibility.

    Example:
        ```python
        pricing = PricingDetails(
            input_text="10 points/1k tokens",
            bot_message="5 points/message",
            initial_points_cost="100 points"
        )
        ```
    """

    # Standard pricing fields
    input_text: str | None = Field(None, alias="Input (text)")
    input_image: str | None = Field(None, alias="Input (image)")
    bot_message: str | None = Field(None, alias="Bot message")
    chat_history: str | None = Field(None, alias="Chat history")
    chat_history_cache_discount: str | None = Field(None, alias="Chat history cache discount")

    # Alternative pricing fields
    total_cost: str | None = Field(None, alias="Total cost")
    image_output: str | None = Field(None, alias="Image Output")
    video_output: str | None = Field(None, alias="Video Output")
    text_input: str | None = Field(None, alias="Text input")
    per_message: str | None = Field(None, alias="Per Message")
    finetuning: str | None = Field(None, alias="Finetuning")

    # Initial points cost from bot info card
    initial_points_cost: str | None = None

    # Allow extra fields for future compatibility
    class Config:
        populate_by_name = True
        extra = "allow"


class Pricing(BaseModel):
    """Pricing information with timestamp for tracking data freshness.

    Combines detailed pricing information with a timestamp to know
    when the data was last scraped from Poe.com.

    Attributes:
        checked_at: UTC datetime when pricing was last scraped
        details: Detailed pricing information structure

    Example:
        ```python
        pricing = Pricing(
            checked_at=datetime.now(timezone.utc),
            details=PricingDetails(input_text="10 points/1k tokens")
        )
        ```
    """

    checked_at: datetime
    details: PricingDetails


class BotInfo(BaseModel):
    """Bot information scraped from Poe.com bot info cards.

    This model captures metadata about the bot/model that isn't available
    through the API, including creator information and descriptions.

    Attributes:
        creator: Bot creator handle (e.g., "@openai", "@anthropic")
        description: Main bot description text from the info card
        description_extra: Additional disclaimer or detail text

    Note:
        All fields are optional as not all bots have complete information.
        Creator handles include the "@" prefix as shown on Poe.com.

    Example:
        ```python
        bot_info = BotInfo(
            creator="@anthropic",
            description="Claude is an AI assistant created by Anthropic",
            description_extra="Powered by Claude-3 Sonnet"
        )
        ```
    """

    creator: str | None = None  # e.g., "@openai"
    description: str | None = None  # Main bot description
    description_extra: str | None = None  # Additional disclaimer text


class PoeModel(BaseModel):
    """Complete Poe model representation combining API data with scraped information.

    This is the main model class that represents a complete Poe.com model,
    including data from the API (id, architecture, etc.) and additional
    information scraped from the website (pricing, bot info).

    Attributes:
        id: Unique model identifier (e.g., "Claude-3-Opus")
        object: Always "model" for API compatibility
        created: Unix timestamp of model creation
        owned_by: Organization that owns the model (e.g., "anthropic")
        permission: List of permissions (typically empty)
        root: Root model name (often same as id)
        parent: Parent model if this is a variant (optional)
        architecture: Model capabilities and modalities
        pricing: Scraped pricing information with timestamp (optional)
        pricing_error: Error message if pricing scraping failed (optional)
        bot_info: Scraped bot metadata from info card (optional)

    Note:
        Used by api.py for model querying and by updater.py for data management.
        See ModelCollection for working with multiple models.

    Example:
        ```python
        model = PoeModel(
            id="Claude-3-Opus",
            created=1709574492024,
            owned_by="anthropic",
            root="Claude-3-Opus",
            architecture=Architecture(...),
            pricing=Pricing(...)
        )
        ```
    """

    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: list[Any] = Field(default_factory=list)
    root: str
    parent: str | None = None
    architecture: Architecture
    pricing: Pricing | None = None
    pricing_error: str | None = None
    bot_info: BotInfo | None = None

    def has_pricing(self) -> bool:
        """Check if model has valid pricing information.

        Returns:
            True if model has pricing data, False otherwise.

        Note:
            Used by CLI commands to filter models with pricing.
        """
        return self.pricing is not None

    def needs_pricing_update(self) -> bool:
        """Check if model needs pricing information updated.

        Returns:
            True if pricing is missing or has errors, False otherwise.

        Note:
            Used by updater.py to determine which models to scrape.
        """
        return self.pricing is None or self.pricing_error is not None

    def get_primary_cost(self) -> str | None:
        """Get the most relevant cost information for display.

        Tries different pricing fields in order of preference to find
        the most useful cost information for CLI display.

        Returns:
            Primary cost string (e.g., "10 points/1k tokens") or None.

        Note:
            Used by CLI search and list commands for consistent display.
            Preference order: input_text -> total_cost -> per_message -> others.
        """
        if not self.pricing:
            return None

        details = self.pricing.details
        # Try different cost fields in order of preference
        if details.input_text:
            return details.input_text
        if details.total_cost:
            return details.total_cost
        if details.per_message:
            return details.per_message
        if details.image_output:
            return details.image_output
        if details.video_output:
            return details.video_output
        if details.text_input:
            return details.text_input
        if details.finetuning:
            return details.finetuning
        # If none of the known fields, try to get first available field
        for value in details.model_dump(exclude_none=True).values():
            if value and isinstance(value, str):
                return str(value)  # Explicit cast to satisfy mypy
        return None


class ModelCollection(BaseModel):
    """Collection of Poe models with query and search capabilities.

    This class represents the complete dataset of Poe models loaded from
    the JSON data file. It provides methods for querying and searching
    models efficiently.

    Attributes:
        object: Always "list" for API compatibility
        data: List of all PoeModel instances

    Note:
        Used by api.py as the main data structure for model operations.
        Loaded from poe_models.json by the get_models() function.

    Example:
        ```python
        collection = ModelCollection(data=[model1, model2, model3])
        claude_models = collection.search("claude")
        specific_model = collection.get_by_id("Claude-3-Opus")
        ```
    """

    object: str = "list"
    data: list[PoeModel]

    def get_by_id(self, model_id: str) -> PoeModel | None:
        """Get a specific model by its unique identifier.

        Args:
            model_id: The model ID to search for (case-sensitive)

        Returns:
            The matching PoeModel or None if not found

        Note:
            Used by api.get_model_by_id() for direct model access.
        """
        return next((model for model in self.data if model.id == model_id), None)

    def search(self, query: str) -> list[PoeModel]:
        """Search models by ID or name using case-insensitive matching.

        Searches both the model ID and root name fields for matches.

        Args:
            query: Search term to match against model names

        Returns:
            List of matching PoeModel instances (may be empty)

        Note:
            Used by api.search_models() and CLI search command.
            Searches both 'id' and 'root' fields for maximum coverage.
        """
        query_lower = query.lower()
        return [model for model in self.data if query_lower in model.id.lower() or query_lower in model.root.lower()]
