# this_file: src/virginia_clemm_poe/bots.py

"""Pydantic bot representations for Virginia Clemm Poe with dual pricing support."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Architecture(BaseModel):
    """Bot architecture information describing input/output capabilities.

    This structure defines what types of data a Poe bot can accept as input
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


class ApiPricing(BaseModel):
    """Dollar-based pricing from official Poe API.

    Represents the authoritative pricing information provided directly by the API.
    All prices are in USD per unit (token/image/request).

    Attributes:
        prompt: Cost per input token in USD (e.g., 0.0000011 = $0.0000011/token)
        completion: Cost per output token in USD
        image: Cost per image in USD (for image bots)
        request: Cost per request in USD (for request-based pricing)

    Example:
        ```python
        api_pricing = ApiPricing(
            prompt=Decimal("0.0000011"),
            completion=Decimal("0.0000090"),
            image=None,
            request=None
        )
        ```
    """

    prompt: Decimal | None = None
    completion: Decimal | None = None
    image: Decimal | None = None
    request: Decimal | None = None

    @field_validator("prompt", "completion", "image", "request", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert string prices to Decimal for precision."""
        if v is None:
            return None
        if isinstance(v, str):
            return Decimal(v)
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v

    def cost_per_1k_tokens(self, input_tokens: int = 500, output_tokens: int = 500) -> Decimal | None:
        """Calculate cost for 1k tokens with given input/output ratio.

        Args:
            input_tokens: Number of input tokens (default 500)
            output_tokens: Number of output tokens (default 500)

        Returns:
            Total cost in USD for the specified token counts, or None if pricing unavailable
        """
        if not self.prompt or not self.completion:
            return None

        input_cost = self.prompt * Decimal(input_tokens)
        output_cost = self.completion * Decimal(output_tokens)
        return input_cost + output_cost

    def format_price(self, price: Decimal | None, unit: str = "token") -> str:
        """Format a price value for display.

        Args:
            price: Price to format
            unit: Unit label (e.g., "token", "image", "request")

        Returns:
            Formatted price string
        """
        if price is None:
            return ""

        # Use scientific notation for very small numbers
        if price < Decimal("0.0001"):
            return f"${price:.2e}/{unit}"
        return f"${price:.6f}/{unit}"

    def display_summary(self) -> str:
        """Get a concise summary of API pricing for CLI display."""
        parts = []
        if self.prompt is not None:
            parts.append(self.format_price(self.prompt, "in"))
        if self.completion is not None:
            parts.append(self.format_price(self.completion, "out"))
        if self.image is not None:
            parts.append(self.format_price(self.image, "img"))
        if self.request is not None:
            parts.append(self.format_price(self.request, "req"))

        return " | ".join(parts) if parts else "No API pricing"


class ScrapedPricingDetails(BaseModel):
    """Point-based pricing details from web scraping.

    This bot captures all possible pricing structures found on Poe.com,
    as different bots use different pricing formats. The fields use aliases
    to match the exact text found on the website.

    Standard pricing fields are the most common, while alternative fields
    accommodate different bot types and pricing structures.

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
        finetuning: Cost for bot fine-tuning
        initial_points_cost: Upfront cost from bot info card

    Note:
        Uses Field aliases to match exact website text.
        Extra fields are allowed for future pricing format compatibility.

    Example:
        ```python
        pricing = ScrapedPricingDetails(
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

    @field_validator(
        "total_cost",
        "input_text",
        "input_image",
        "bot_message",
        "chat_history",
        "image_output",
        "video_output",
        "text_input",
        "per_message",
        mode="before",
    )
    @classmethod
    def handle_list_values(cls, v):
        """Handle case where pricing fields are lists (e.g., ['$0.0057/message', '190 points/message']).

        When Poe returns both dollar and point values, prefer the point value for scraped pricing.
        """
        if isinstance(v, list):
            # If it's a list, look for the points value
            for item in v:
                if isinstance(item, str) and "points" in item.lower():
                    return item
            # If no points value, return the first item
            return v[0] if v else None
        return v


class ScrapedPricing(BaseModel):
    """Container for scraped pricing information with timestamp.

    Combines detailed pricing information scraped from Poe.com with
    metadata about when the data was collected.

    Attributes:
        checked_at: UTC datetime when pricing was last scraped
        details: Detailed pricing information structure

    Example:
        ```python
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(timezone.utc),
            details=ScrapedPricingDetails(input_text="10 points/1k tokens")
        )
        ```
    """

    checked_at: datetime
    details: ScrapedPricingDetails

    def get_primary_cost(self) -> str | None:
        """Get the most relevant scraped cost for display.

        Returns the most useful cost information from scraped data,
        preferring input_text -> total_cost -> per_message -> others.
        """
        if not self.details:
            return None

        # Try different cost fields in order of preference
        if self.details.input_text:
            return self.details.input_text
        if self.details.total_cost:
            return self.details.total_cost
        if self.details.per_message:
            return self.details.per_message
        if self.details.image_output:
            return self.details.image_output
        if self.details.video_output:
            return self.details.video_output
        if self.details.text_input:
            return self.details.text_input
        if self.details.finetuning:
            return self.details.finetuning

        # If none of the known fields, try to get first available field
        for value in self.details.model_dump(exclude_none=True).values():
            if value and isinstance(value, str):
                return value
        return None


class UnifiedPricing(BaseModel):
    """Unified container for both API and scraped pricing information.

    This bot combines authoritative API pricing (in dollars) with contextual
    scraped pricing (in points), providing a complete view of bot costs.

    The API pricing is considered the primary/authoritative source when available,
    while scraped pricing provides additional context and point-based information.

    Attributes:
        api: Dollar-based pricing from the official API (authoritative)
        scraped: Point-based pricing from web scraping (contextual)

    Example:
        ```python
        unified = UnifiedPricing(
            api=ApiPricing(prompt=Decimal("0.0000011")),
            scraped=ScrapedPricing(
                checked_at=datetime.now(),
                details=ScrapedPricingDetails(total_cost="170 points/message")
            )
        )
        ```
    """

    api: ApiPricing | None = None
    scraped: ScrapedPricing | None = None

    @property
    def has_api_pricing(self) -> bool:
        """Check if API pricing is available."""
        return self.api is not None

    @property
    def has_scraped_pricing(self) -> bool:
        """Check if scraped pricing is available."""
        return self.scraped is not None

    @property
    def has_any_pricing(self) -> bool:
        """Check if any pricing information is available."""
        return self.has_api_pricing or self.has_scraped_pricing

    def display_primary(self) -> str:
        """Get primary pricing display (API preferred over scraped).

        Returns a single-line summary of the most relevant pricing information,
        preferring API pricing when available.
        """
        if self.api:
            return self.api.display_summary()
        if self.scraped:
            cost = self.scraped.get_primary_cost()
            return cost if cost else "No pricing available"
        return "No pricing available"

    def display_full(self) -> str:
        """Get full pricing display showing both API and scraped pricing.

        Returns a detailed view with both pricing types when available.
        """
        parts = []

        if self.api:
            api_summary = self.api.display_summary()
            if api_summary and api_summary != "No API pricing":
                parts.append(f"API: {api_summary}")

        if self.scraped:
            scraped_cost = self.scraped.get_primary_cost()
            if scraped_cost:
                parts.append(f"Points: {scraped_cost}")

        return " | ".join(parts) if parts else "No pricing available"

    def display_for_cli(self, format_type: str = "primary") -> str:
        """Get pricing display formatted for CLI output.

        Args:
            format_type: Display format - "primary", "api", "scraped", or "both"

        Returns:
            Formatted pricing string based on the requested format
        """
        if format_type == "api" and self.api:
            return self.api.display_summary()
        if format_type == "scraped" and self.scraped:
            cost = self.scraped.get_primary_cost()
            return cost if cost else "No scraped pricing"
        if format_type == "both":
            return self.display_full()
        # primary (default)
        return self.display_primary()


# Backward compatibility aliases (will be deprecated)
Pricing = ScrapedPricing  # Temporary alias for backward compatibility
PricingDetails = ScrapedPricingDetails  # Temporary alias


class BotInfo(BaseModel):
    """Bot information scraped from Poe.com bot info cards.

    This bot captures metadata about the bot/bot that isn't available
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


class PoeBot(BaseModel):
    """Complete Poe bot representation with dual pricing support.

    This is the main bot class that represents a complete Poe.com bot,
    including data from the API (id, architecture, etc.) and additional
    information scraped from the website (pricing, bot info).

    Now supports both API pricing (dollars) and scraped pricing (points)
    through the UnifiedPricing bot.

    Attributes:
        id: Unique bot identifier (e.g., "Claude-3-Opus")
        object: Always "bot" for API compatibility
        created: Unix timestamp of bot creation
        owned_by: Organization that owns the bot (e.g., "anthropic")
        permission: List of permissions (typically empty)
        root: Root bot name (often same as id)
        parent: Parent bot if this is a variant (optional)
        architecture: Bot capabilities and modalities
        pricing: Unified pricing information (API + scraped)
        api_last_updated: Timestamp when the bot was last observed in the API
        pricing_error: Error message if pricing scraping failed (optional)
        bot_info: Scraped bot metadata from info card (optional)

    Note:
        Used by api.py for bot querying and by updater.py for data management.
        See BotCollection for working with multiple bots.

    Example:
        ```python
        bot = PoeBot(
            id="Claude-3-Opus",
            created=1709574492024,
            owned_by="anthropic",
            root="Claude-3-Opus",
            architecture=Architecture(...),
            pricing=UnifiedPricing(...)
        )
        ```
    """

    id: str
    object: str = "bot"
    created: int
    owned_by: str
    permission: list[Any] = Field(default_factory=list)
    root: str
    parent: str | None = None
    architecture: Architecture
    pricing: UnifiedPricing | None = None
    api_last_updated: datetime | None = None
    pricing_error: str | None = None
    bot_info: BotInfo | None = None

    def has_pricing(self) -> bool:
        """Check if bot has any pricing information.

        Returns:
            True if bot has either API or scraped pricing data.
        """
        return self.pricing is not None and self.pricing.has_any_pricing

    def has_api_pricing(self) -> bool:
        """Check if bot has API pricing information.

        Returns:
            True if bot has API pricing data.
        """
        return self.pricing is not None and self.pricing.has_api_pricing

    def has_scraped_pricing(self) -> bool:
        """Check if bot has scraped pricing information.

        Returns:
            True if bot has scraped pricing data.
        """
        return self.pricing is not None and self.pricing.has_scraped_pricing

    def needs_pricing_update(self) -> bool:
        """Check if bot needs pricing information updated.

        Returns:
            True if pricing is completely missing or has errors.
        """
        return self.pricing is None or self.pricing_error is not None

    def needs_scraping_update(self) -> bool:
        """Check if bot needs scraped pricing updated.

        Returns:
            True if scraped pricing is missing.
        """
        return self.pricing is None or not self.pricing.has_scraped_pricing

    def get_primary_cost(self) -> str | None:
        """Get the most relevant cost information for display.

        Returns the primary cost string from unified pricing,
        preferring API pricing over scraped pricing.

        Returns:
            Primary cost string or None if no pricing available.
        """
        if not self.pricing:
            return None
        return self.pricing.display_primary()


class BotCollection(BaseModel):
    """Collection of Poe bots with query and search capabilities.

    This class represents the complete dataset of Poe bots loaded from
    the JSON data file. It provides methods for querying and searching
    bots efficiently.

    Attributes:
        object: Always "list" for API compatibility
        data: List of all PoeBot instances
        version: Data format version for migration support

    Note:
        Used by api.py as the main data structure for bot operations.
        Loaded from poe_models.json by the get_models() function.

    Example:
        ```python
        collection = BotCollection(data=[model1, model2, model3])
        claude_models = collection.search("claude")
        specific_model = collection.get_by_id("Claude-3-Opus")
        ```
    """

    object: str = "list"
    data: list[PoeBot]
    version: int = 2  # Incremented for dual pricing support

    def sort_by_api_last_updated(self) -> None:
        """Sort bots by API update timestamp, oldest first.

        Bots without a timestamp are treated as the oldest entries.
        """
        self.data.sort(key=lambda bot: bot.api_last_updated or datetime.min)

    def get_by_id(self, model_id: str) -> PoeBot | None:
        """Get a specific bot by its unique identifier.

        Args:
            model_id: The bot ID to search for (case-sensitive)

        Returns:
            The matching PoeBot or None if not found
        """
        return next((bot for bot in self.data if bot.id == model_id), None)

    def search(self, query: str) -> list[PoeBot]:
        """Search bots by ID or name using case-insensitive matching.

        Searches both the bot ID and root name fields for matches.

        Args:
            query: Search term to match against bot names

        Returns:
            List of matching PoeBot instances (may be empty)
        """
        query_lower = query.lower()
        return [bot for bot in self.data if query_lower in bot.id.lower() or query_lower in bot.root.lower()]
