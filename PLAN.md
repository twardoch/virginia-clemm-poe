# this_file: PLAN.md

# Virginia Clemm Poe - Development Plan

## Current Status: Major API Update Refactoring (Phase 9) 🚧

The Poe API has introduced native pricing information in a new format, requiring a comprehensive refactoring to support dual pricing models while maintaining backward compatibility.

## Phase 9: Dual Pricing Model Support (IN PROGRESS - Started 2025-10-15)

### Objective
Refactor the entire pricing system to support both the new API pricing format (dollars per token) and the existing scraped pricing format (points per message), with API pricing as the authoritative source.

### Context & Analysis

#### New API Pricing Format
The Poe API now returns pricing information directly:
```json
"pricing": {
  "prompt": "0.0000011",      // dollars per input token
  "completion": "0.0000090",   // dollars per output token
  "image": null,               // dollars per image (if applicable)
  "request": null              // dollars per request (if applicable)
}
```

#### Existing Scraped Pricing Format
Our current scraped pricing provides different metrics:
```json
"pricing": {
  "checked_at": "2025-09-20 12:03:46",
  "details": {
    "input_text": "10 points/1k tokens",
    "bot_message": "5 points/message",
    "total_cost": "170 points/message",
    // ... other point-based metrics
  }
}
```

### Architecture Design

#### 9.1 New Data Model Structure

We'll implement a unified pricing model that accommodates both formats:

```python
# New pricing models hierarchy
ApiPricing          # Dollar-based pricing from API
ScrapedPricing      # Point-based pricing from web scraping
UnifiedPricing      # Container for both pricing types
  ├── api: ApiPricing (primary/authoritative)
  └── scraped: ScrapedPricing (contextual/supplementary)
```

Key design principles:
1. **API First**: API pricing is the single source of truth when available
2. **Graceful Fallback**: Use scraped pricing when API pricing unavailable
3. **Dual Display**: Show both pricing types when both exist
4. **Backward Compatible**: Support models with only scraped pricing

#### 9.2 Implementation Strategy

##### Phase 9.2.1: Data Model Refactoring
1. Create new pricing models:
   - `ApiPricing`: For dollar-based API pricing
   - `ScrapedPricingDetails`: Renamed from current `PricingDetails`
   - `ScrapedPricing`: Renamed from current `Pricing`
   - `UnifiedPricing`: New container model

2. Update `PoeBot`:
   - Replace `pricing: Pricing` with `pricing: UnifiedPricing`
   - Add migration logic for existing data
   - Implement conversion utilities

##### Phase 9.2.2: Updater Refactoring
1. Parse API pricing into `ApiPricing` model
2. Keep scraping logic for `ScrapedPricing`
3. Merge both into `UnifiedPricing`
4. Implement intelligent update strategy:
   - Always update API pricing from API
   - Only scrape if missing scraped pricing or force flag
   - Preserve existing scraped data when updating API data

##### Phase 9.2.3: Display & CLI Updates
1. Unified pricing display logic:
   - Primary line: API pricing in $/token
   - Secondary line: Scraped pricing in points
   - Smart formatting based on available data

2. Enhanced CLI commands:
   - `--show-pricing`: Display detailed pricing breakdown
   - `--pricing-format`: Choose display format (api/scraped/both)
   - Cost calculator updates for dual pricing

##### Phase 9.2.4: Migration & Compatibility
1. Data migration script:
   - Convert existing `Pricing` to `ScrapedPricing`
   - Wrap in `UnifiedPricing` container
   - Preserve all existing data

2. Backward compatibility:
   - Support old JSON format on load
   - Auto-migrate on first update
   - Version field in JSON for format detection

### Technical Implementation Details

#### 9.3 Detailed Model Definitions

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ApiPricing(BaseModel):
    """Dollar-based pricing from official API."""
    prompt: Optional[Decimal] = None        # $/input token
    completion: Optional[Decimal] = None    # $/output token
    image: Optional[Decimal] = None         # $/image
    request: Optional[Decimal] = None       # $/request

    def cost_per_1k_tokens(self, input_tokens: int = 500, output_tokens: int = 500) -> Decimal:
        """Calculate cost for 1k tokens with given input/output ratio."""
        ...

class ScrapedPricingDetails(BaseModel):
    """Point-based pricing details from web scraping."""
    input_text: Optional[str] = None
    input_image: Optional[str] = None
    bot_message: Optional[str] = None
    chat_history: Optional[str] = None
    chat_history_cache_discount: Optional[str] = None
    total_cost: Optional[str] = None
    image_output: Optional[str] = None
    video_output: Optional[str] = None
    text_input: Optional[str] = None
    per_message: Optional[str] = None
    finetuning: Optional[str] = None
    initial_points_cost: Optional[str] = None

class ScrapedPricing(BaseModel):
    """Container for scraped pricing with metadata."""
    checked_at: datetime
    details: ScrapedPricingDetails

class UnifiedPricing(BaseModel):
    """Unified container for all pricing information."""
    api: Optional[ApiPricing] = None
    scraped: Optional[ScrapedPricing] = None

    @property
    def has_api_pricing(self) -> bool:
        return self.api is not None

    @property
    def has_scraped_pricing(self) -> bool:
        return self.scraped is not None

    def display_primary(self) -> str:
        """Primary pricing display (API if available)."""
        ...

    def display_full(self) -> str:
        """Full pricing display (both if available)."""
        ...
```

#### 9.4 Update Flow Refactoring

```python
async def update_model_pricing(model: PoeBot, api_data: dict, force_scrape: bool = False):
    """Update model with both API and scraped pricing."""

    # Step 1: Process API pricing if available
    if "pricing" in api_data:
        model.pricing = model.pricing or UnifiedPricing()
        model.pricing.api = ApiPricing(**api_data["pricing"])

    # Step 2: Determine if scraping needed
    needs_scraping = (
        force_scrape or
        not model.pricing or
        not model.pricing.scraped or
        model.pricing_error
    )

    # Step 3: Scrape if needed
    if needs_scraping:
        scraped_data = await scrape_pricing(model.id)
        if scraped_data:
            model.pricing = model.pricing or UnifiedPricing()
            model.pricing.scraped = ScrapedPricing(
                checked_at=datetime.utcnow(),
                details=ScrapedPricingDetails(**scraped_data)
            )
```

### Success Metrics

1. **Data Integrity**: 100% of models with API pricing properly stored
2. **Backward Compatibility**: Zero data loss during migration
3. **Performance**: <10% increase in update time despite dual sources
4. **User Experience**: Clear, unified pricing display in all commands
5. **Test Coverage**: >95% coverage for pricing-related code

### Risk Mitigation

1. **API Changes**: Abstract pricing parsers for easy updates
2. **Data Loss**: Comprehensive backup before migration
3. **Performance**: Parallel processing for API and scraping
4. **User Confusion**: Clear documentation and help text

### Testing Strategy

1. **Unit Tests**:
   - Model validation with various pricing combinations
   - Migration logic with edge cases
   - Display formatting with all scenarios

2. **Integration Tests**:
   - Full update cycle with both pricing sources
   - CLI commands with unified pricing
   - Data persistence and loading

3. **Regression Tests**:
   - Existing functionality remains intact
   - Old data formats still loadable
   - Performance benchmarks maintained

## Phase 10: Future Enhancements (After Phase 9)

### 10.1 Advanced Pricing Analytics
- Historical pricing tracking with trends
- Cost optimization recommendations
- Price-performance analysis
- Usage-based cost projections

### 10.2 Enhanced Data Export
- Export both pricing formats
- Custom export templates
- Pricing comparison reports
- Bulk pricing updates via CSV

### 10.3 Real-time Pricing Updates
- Webhook support for API pricing changes
- Automatic background updates
- Price change notifications
- Pricing alert thresholds

## Implementation Timeline

### Week 1 (2025-10-15 to 2025-10-22)
- [x] Analyze new API format
- [x] Design unified pricing model
- [ ] Implement new model classes
- [ ] Write migration logic
- [ ] Update data persistence

### Week 2 (2025-10-23 to 2025-10-29)
- [ ] Refactor updater for dual sources
- [ ] Implement parallel update strategy
- [ ] Update CLI display logic
- [ ] Add new CLI options
- [ ] Comprehensive testing

### Week 3 (2025-10-30 to 2025-11-05)
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] User migration guide
- [ ] Release preparation
- [ ] Post-release monitoring

## Long-term Vision

Transform Virginia Clemm Poe into the definitive Poe.com model intelligence platform with:
- **Comprehensive Pricing Intelligence**: Complete understanding of all pricing models
- **Real-time Market Analysis**: Track pricing trends across all providers
- **Cost Optimization Engine**: Recommend best models for specific use cases
- **Enterprise Integration**: API endpoints for programmatic access
- **Predictive Analytics**: Forecast pricing changes and model availability