# this_file: tests/test_pricing_models.py
"""Tests for the dual pricing bot system."""

from datetime import UTC, datetime
from decimal import Decimal

from virginia_clemm_poe.bots import (
    ApiPricing,
    Architecture,
    BotCollection,
    PoeBot,
    ScrapedPricing,
    ScrapedPricingDetails,
    UnifiedPricing,
)


class TestApiPricing:
    """Test API dollar-based pricing bot."""

    def test_valid_api_pricing_creation(self) -> None:
        """Test creating a valid ApiPricing instance."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.0000011"),
            completion=Decimal("0.0000090"),
            image=None,
            request=None,
        )
        assert api_pricing.prompt == Decimal("0.0000011")
        assert api_pricing.completion == Decimal("0.0000090")
        assert api_pricing.image is None
        assert api_pricing.request is None

    def test_api_pricing_string_conversion(self) -> None:
        """Test converting string prices to Decimal."""
        api_pricing = ApiPricing(
            prompt="0.0000011",
            completion="0.0000090",
        )
        assert isinstance(api_pricing.prompt, Decimal)
        assert isinstance(api_pricing.completion, Decimal)
        assert api_pricing.prompt == Decimal("0.0000011")

    def test_api_pricing_numeric_conversion(self) -> None:
        """Test converting numeric values to Decimal."""
        api_pricing = ApiPricing(
            prompt=0.0000011,
            completion=0.0000090,
        )
        assert isinstance(api_pricing.prompt, Decimal)
        assert isinstance(api_pricing.completion, Decimal)

    def test_cost_per_1k_tokens(self) -> None:
        """Test calculating cost for 1k tokens."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),  # $1 per million tokens
            completion=Decimal("0.000002"),  # $2 per million tokens
        )
        # Default: 500 input + 500 output
        cost = api_pricing.cost_per_1k_tokens()
        assert cost == Decimal("0.0015")  # 500 * 0.000001 + 500 * 0.000002

        # Custom ratio: 700 input + 300 output
        cost = api_pricing.cost_per_1k_tokens(input_tokens=700, output_tokens=300)
        assert cost == Decimal("0.0013")  # 700 * 0.000001 + 300 * 0.000002

    def test_cost_per_1k_tokens_missing_pricing(self) -> None:
        """Test cost calculation when pricing is missing."""
        api_pricing = ApiPricing(prompt=Decimal("0.000001"))
        assert api_pricing.cost_per_1k_tokens() is None

    def test_format_price(self) -> None:
        """Test price formatting for display."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.0000011"),
            completion=Decimal("0.15"),
        )

        # Small number uses scientific notation
        assert api_pricing.format_price(api_pricing.prompt, "token") == "$1.10e-6/token"

        # Larger number uses regular format
        assert api_pricing.format_price(api_pricing.completion, "token") == "$0.150000/token"

        # None returns empty string
        assert api_pricing.format_price(None, "token") == ""

    def test_display_summary(self) -> None:
        """Test API pricing summary display."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
            image=Decimal("0.01"),
        )
        summary = api_pricing.display_summary()
        assert "$1.00e-6/in" in summary
        assert "$2.00e-6/out" in summary
        assert "$0.010000/img" in summary

    def test_display_summary_no_pricing(self) -> None:
        """Test display when no pricing is available."""
        api_pricing = ApiPricing()
        assert api_pricing.display_summary() == "No API pricing"


class TestScrapedPricing:
    """Test scraped point-based pricing bot."""

    def test_valid_scraped_pricing_creation(self) -> None:
        """Test creating a valid ScrapedPricing instance."""
        details = ScrapedPricingDetails(
            input_text="10 points/1k tokens",
            bot_message="5 points/message",
        )
        scraped = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=details,
        )
        assert scraped.details.input_text == "10 points/1k tokens"
        assert scraped.details.bot_message == "5 points/message"

    def test_scraped_pricing_with_aliases(self) -> None:
        """Test ScrapedPricingDetails with field aliases."""
        details = ScrapedPricingDetails(
            **{
                "Input (text)": "15 points/1k tokens",
                "Bot message": "8 points/message",
                "Total cost": "170 points/message",
            }
        )
        assert details.input_text == "15 points/1k tokens"
        assert details.bot_message == "8 points/message"
        assert details.total_cost == "170 points/message"

    def test_get_primary_cost_priority(self) -> None:
        """Test primary cost extraction priority."""
        # Test input_text priority
        details = ScrapedPricingDetails(
            input_text="10 points/1k tokens",
            total_cost="500 points",
            per_message="15 points/message",
        )
        scraped = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=details,
        )
        assert scraped.get_primary_cost() == "10 points/1k tokens"

        # Test total_cost when input_text is missing
        details = ScrapedPricingDetails(
            total_cost="500 points",
            per_message="15 points/message",
        )
        scraped = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=details,
        )
        assert scraped.get_primary_cost() == "500 points"

    def test_get_primary_cost_none(self) -> None:
        """Test primary cost when no pricing is available."""
        details = ScrapedPricingDetails()
        scraped = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=details,
        )
        assert scraped.get_primary_cost() is None


class TestUnifiedPricing:
    """Test unified pricing container."""

    def test_unified_pricing_both_sources(self) -> None:
        """Test unified pricing with both API and scraped data."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
        )
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(api=api_pricing, scraped=scraped_pricing)

        assert unified.has_api_pricing
        assert unified.has_scraped_pricing
        assert unified.has_any_pricing

    def test_unified_pricing_api_only(self) -> None:
        """Test unified pricing with only API data."""
        api_pricing = ApiPricing(prompt=Decimal("0.000001"))
        unified = UnifiedPricing(api=api_pricing)

        assert unified.has_api_pricing
        assert not unified.has_scraped_pricing
        assert unified.has_any_pricing

    def test_unified_pricing_scraped_only(self) -> None:
        """Test unified pricing with only scraped data."""
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(scraped=scraped_pricing)

        assert not unified.has_api_pricing
        assert unified.has_scraped_pricing
        assert unified.has_any_pricing

    def test_unified_pricing_none(self) -> None:
        """Test unified pricing with no data."""
        unified = UnifiedPricing()

        assert not unified.has_api_pricing
        assert not unified.has_scraped_pricing
        assert not unified.has_any_pricing

    def test_display_primary_api_preferred(self) -> None:
        """Test that API pricing is preferred in primary display."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
        )
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(api=api_pricing, scraped=scraped_pricing)

        display = unified.display_primary()
        assert "$" in display  # Should show API pricing (dollar format)
        assert "points" not in display

    def test_display_primary_scraped_fallback(self) -> None:
        """Test that scraped pricing is used when API is unavailable."""
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(scraped=scraped_pricing)

        display = unified.display_primary()
        assert "170 points/message" in display

    def test_display_full(self) -> None:
        """Test full pricing display with both sources."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
        )
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(api=api_pricing, scraped=scraped_pricing)

        display = unified.display_full()
        assert "API:" in display
        assert "Points:" in display
        assert "170 points/message" in display

    def test_display_for_cli_formats(self) -> None:
        """Test different CLI display formats."""
        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
        )
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(api=api_pricing, scraped=scraped_pricing)

        # Test primary format (default)
        display = unified.display_for_cli("primary")
        assert "$" in display

        # Test API only format
        display = unified.display_for_cli("api")
        assert "$" in display
        assert "points" not in display

        # Test scraped only format
        display = unified.display_for_cli("scraped")
        assert "170 points/message" in display

        # Test both format
        display = unified.display_for_cli("both")
        assert "API:" in display
        assert "Points:" in display


class TestPoeBotWithUnifiedPricing:
    """Test PoeBot with unified pricing system."""

    def test_poe_model_with_unified_pricing(self) -> None:
        """Test PoeBot with unified pricing."""
        arch = Architecture(
            input_modalities=["text"],
            output_modalities=["text"],
            modality="text->text",
        )

        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
        )
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(api=api_pricing, scraped=scraped_pricing)

        bot = PoeBot(
            id="test-bot",
            created=1704369600,
            owned_by="testorg",
            root="test-bot",
            architecture=arch,
            pricing=unified,
        )

        assert bot.has_pricing()
        assert bot.has_api_pricing()
        assert bot.has_scraped_pricing()
        assert not bot.needs_pricing_update()

    def test_poe_model_needs_scraping_update(self) -> None:
        """Test bot needing scraped pricing update."""
        arch = Architecture(
            input_modalities=["text"],
            output_modalities=["text"],
            modality="text->text",
        )

        # Bot with only API pricing
        api_pricing = ApiPricing(prompt=Decimal("0.000001"))
        unified = UnifiedPricing(api=api_pricing)

        bot = PoeBot(
            id="test-bot",
            created=1704369600,
            owned_by="testorg",
            root="test-bot",
            architecture=arch,
            pricing=unified,
        )

        assert bot.has_api_pricing()
        assert not bot.has_scraped_pricing()
        assert bot.needs_scraping_update()

    def test_get_primary_cost_with_unified(self) -> None:
        """Test getting primary cost from unified pricing."""
        arch = Architecture(
            input_modalities=["text"],
            output_modalities=["text"],
            modality="text->text",
        )

        api_pricing = ApiPricing(
            prompt=Decimal("0.000001"),
            completion=Decimal("0.000002"),
        )
        scraped_pricing = ScrapedPricing(
            checked_at=datetime.now(UTC),
            details=ScrapedPricingDetails(total_cost="170 points/message"),
        )
        unified = UnifiedPricing(api=api_pricing, scraped=scraped_pricing)

        bot = PoeBot(
            id="test-bot",
            created=1704369600,
            owned_by="testorg",
            root="test-bot",
            architecture=arch,
            pricing=unified,
        )

        cost = bot.get_primary_cost()
        assert cost is not None
        assert "$" in cost  # Should show API pricing


class TestBotCollectionWithVersion:
    """Test BotCollection with version support."""

    def test_model_collection_version(self) -> None:
        """Test BotCollection with version field."""
        arch = Architecture(
            input_modalities=["text"],
            output_modalities=["text"],
            modality="text->text",
        )

        bot = PoeBot(
            id="test-bot",
            created=1704369600,
            owned_by="testorg",
            root="test-bot",
            architecture=arch,
        )

        collection = BotCollection(
            data=[bot],
            version=2,  # Version 2 for dual pricing support
        )

        assert collection.version == 2
        assert len(collection.data) == 1


class TestBackwardCompatibility:
    """Test backward compatibility with old pricing format."""

    def test_old_alias_names_still_work(self) -> None:
        """Test that old alias names still work for backward compatibility."""
        from virginia_clemm_poe.bots import Pricing, PricingDetails

        # These should be aliases to the new classes
        assert Pricing is ScrapedPricing
        assert PricingDetails is ScrapedPricingDetails

        # Test creating with old names
        details = PricingDetails(input_text="10 points/1k tokens")
        pricing = Pricing(
            checked_at=datetime.now(UTC),
            details=details,
        )

        assert isinstance(pricing, ScrapedPricing)
        assert isinstance(details, ScrapedPricingDetails)
