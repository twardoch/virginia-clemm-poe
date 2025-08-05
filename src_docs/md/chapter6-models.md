# Chapter 6: Data Models and Structure

## Overview

Virginia Clemm Poe uses Pydantic models to provide type-safe, validated data structures for all model information. This chapter explains the data models, their relationships, and how to work with them effectively.

## Core Data Models

### Architecture

Defines what types of data a Poe model can accept and produce.

```python
from virginia_clemm_poe.models import Architecture

# Example: Multimodal text model
arch = Architecture(
    input_modalities=["text", "image"],
    output_modalities=["text"],
    modality="multimodal->text"
)

print(f"Inputs: {arch.input_modalities}")    # ["text", "image"]
print(f"Outputs: {arch.output_modalities}")  # ["text"]
print(f"Mode: {arch.modality}")              # "multimodal->text"
```

**Properties:**
- `input_modalities: list[str]` - Supported input types
- `output_modalities: list[str]` - Supported output types  
- `modality: str` - Primary modality description

**Common Modality Types:**
- `"text->text"` - Pure text models (most common)
- `"multimodal->text"` - Accept text + images, output text
- `"text->image"` - Text-to-image generators
- `"text->video"` - Text-to-video generators

### PricingDetails

Captures all possible pricing structures found on Poe.com model pages.

```python
from virginia_clemm_poe.models import PricingDetails

# Example: Standard text model pricing
pricing_details = PricingDetails(
    input_text="10 points/1k tokens",      # Input cost
    bot_message="5 points/message",         # Output cost
    initial_points_cost="100 points"       # Upfront cost
)

# Access pricing information
print(f"Input cost: {pricing_details.input_text}")
print(f"Output cost: {pricing_details.bot_message}")
```

**Standard Pricing Fields:**
- `input_text` (alias: "Input (text)") - Cost per text input
- `input_image` (alias: "Input (image)") - Cost per image input
- `bot_message` (alias: "Bot message") - Cost per bot response
- `chat_history` (alias: "Chat history") - Chat history access cost
- `chat_history_cache_discount` - Caching discount rate

**Alternative Pricing Fields:**
- `total_cost` - Flat rate pricing
- `image_output` - Cost per generated image
- `video_output` - Cost per generated video
- `text_input` - Alternative text input format
- `per_message` - Cost per message interaction
- `finetuning` - Model fine-tuning cost
- `initial_points_cost` - Upfront cost from bot card

**Field Aliases:**
The model uses Pydantic field aliases to match exact text from Poe.com:

```python
# These are equivalent:
pricing.input_text
pricing.model_dump(by_alias=True)["Input (text)"]
```

### Pricing

Combines pricing details with a timestamp for data freshness tracking.

```python
from datetime import datetime, timezone
from virginia_clemm_poe.models import Pricing, PricingDetails

pricing = Pricing(
    checked_at=datetime.now(timezone.utc),
    details=PricingDetails(input_text="10 points/1k tokens")
)

# Check data age
age = datetime.now(timezone.utc) - pricing.checked_at
print(f"Pricing data is {age.days} days old")
```

**Properties:**
- `checked_at: datetime` - UTC timestamp of last scrape
- `details: PricingDetails` - Complete pricing breakdown

### BotInfo

Creator and description metadata scraped from Poe.com bot info cards.

```python
from virginia_clemm_poe.models import BotInfo

bot_info = BotInfo(
    creator="@anthropic",
    description="Claude is an AI assistant created by Anthropic",
    description_extra="Powered by Claude-3 Sonnet"
)

print(f"Created by: {bot_info.creator}")
print(f"Description: {bot_info.description}")
```

**Properties:**
- `creator: str | None` - Bot creator handle (includes "@" prefix)
- `description: str | None` - Main bot description text
- `description_extra: str | None` - Additional details or disclaimers

### PoeModel

The main model class representing a complete Poe.com model.

```python
from virginia_clemm_poe.models import PoeModel, Architecture, Pricing, BotInfo

model = PoeModel(
    id="Claude-3-Opus",
    created=1709574492024,
    owned_by="anthropic",
    root="Claude-3-Opus",
    architecture=Architecture(
        input_modalities=["text"],
        output_modalities=["text"],
        modality="text->text"
    ),
    pricing=Pricing(...),
    bot_info=BotInfo(...)
)
```

**Core Properties:**
- `id: str` - Unique model identifier
- `object: str` - Always "model" (API compatibility)
- `created: int` - Unix timestamp of creation
- `owned_by: str` - Organization owning the model
- `root: str` - Root model name
- `parent: str | None` - Parent model for variants
- `architecture: Architecture` - Capability information

**Enhanced Properties:**
- `pricing: Pricing | None` - Scraped pricing data
- `pricing_error: str | None` - Error if pricing scraping failed
- `bot_info: BotInfo | None` - Scraped bot metadata

**Utility Methods:**

```python
# Check if model has pricing data
if model.has_pricing():
    print("Pricing available")

# Check if model needs pricing update
if model.needs_pricing_update():
    print("Needs pricing update")

# Get primary cost for display
primary_cost = model.get_primary_cost()
if primary_cost:
    print(f"Cost: {primary_cost}")
```

### ModelCollection

Container for working with multiple models with search capabilities.

```python
from virginia_clemm_poe.models import ModelCollection

collection = ModelCollection(data=[model1, model2, model3])

# Search for models
claude_models = collection.search("claude")

# Get specific model
model = collection.get_by_id("Claude-3-Opus")
```

**Properties:**
- `object: str` - Always "list" (API compatibility)
- `data: list[PoeModel]` - List of all models

**Methods:**
- `get_by_id(model_id)` - Exact ID lookup
- `search(query)` - Case-insensitive substring search

## Data Relationships

### Hierarchy

```
ModelCollection
├── data: list[PoeModel]
    ├── architecture: Architecture
    │   ├── input_modalities: list[str]
    │   ├── output_modalities: list[str]
    │   └── modality: str
    ├── pricing: Pricing | None
    │   ├── checked_at: datetime
    │   └── details: PricingDetails
    │       ├── input_text: str | None
    │       ├── bot_message: str | None
    │       └── ... (other pricing fields)
    └── bot_info: BotInfo | None
        ├── creator: str | None
        ├── description: str | None
        └── description_extra: str | None
```

### Data Sources

1. **API Data** (from Poe API):
   - `id`, `created`, `owned_by`, `root`, `parent`
   - `architecture` information

2. **Scraped Data** (from Poe website):
   - `pricing` details and timestamp
   - `bot_info` metadata
   - `pricing_error` if scraping failed

## Working with Models

### Type Safety

All models use Pydantic for runtime validation:

```python
from virginia_clemm_poe.models import PoeModel

# This will raise ValidationError
try:
    invalid_model = PoeModel(
        id="test",
        created="not_a_number",  # Should be int
        owned_by="test",
        root="test",
        architecture="invalid"   # Should be Architecture object
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### JSON Serialization

Models can be serialized to/from JSON:

```python
# Serialize to JSON
model_json = model.model_dump_json()

# Deserialize from JSON
model_dict = json.loads(model_json)
restored_model = PoeModel(**model_dict)

# With aliases (matches website field names)
model_with_aliases = model.model_dump(by_alias=True)
```

### Filtering and Queries

Common patterns for working with model data:

```python
from virginia_clemm_poe import api

# Get all models
models = api.get_all_models()

# Filter by capability
text_models = [m for m in models if "text" in m.architecture.input_modalities]
image_models = [m for m in models if "image" in m.architecture.input_modalities]

# Filter by provider
anthropic_models = [m for m in models if m.owned_by == "anthropic"]
openai_models = [m for m in models if m.owned_by == "openai"]

# Filter by pricing availability
priced_models = [m for m in models if m.has_pricing()]
free_models = [m for m in models if m.pricing and "free" in m.get_primary_cost().lower()]

# Filter by creation date
import datetime
recent_models = [m for m in models if m.created > 1700000000]  # After Nov 2023
```

### Advanced Queries

```python
# Find cheapest models (simplified cost extraction)
def extract_numeric_cost(cost_str):
    """Extract numeric cost from pricing string."""
    if not cost_str:
        return float('inf')
    
    # Simple extraction - matches "X points" patterns
    import re
    match = re.search(r'(\d+(?:\.\d+)?)', cost_str)
    return float(match.group(1)) if match else float('inf')

priced_models = [m for m in models if m.has_pricing()]
cheapest_models = sorted(
    priced_models,
    key=lambda m: extract_numeric_cost(m.get_primary_cost())
)[:10]

# Find models by capability combination
multimodal_models = [
    m for m in models 
    if len(m.architecture.input_modalities) > 1
]

# Group models by provider
from collections import defaultdict
by_provider = defaultdict(list)
for model in models:
    by_provider[model.owned_by].append(model)

for provider, provider_models in by_provider.items():
    print(f"{provider}: {len(provider_models)} models")
```

## Data File Structure

The local dataset is stored as JSON in `poe_models.json`:

```json
{
  "object": "list",
  "data": [
    {
      "id": "Claude-3-Opus",
      "object": "model",
      "created": 1709574492024,
      "owned_by": "anthropic",
      "permission": [],
      "root": "Claude-3-Opus",
      "parent": null,
      "architecture": {
        "input_modalities": ["text"],
        "output_modalities": ["text"],
        "modality": "text->text"
      },
      "pricing": {
        "checked_at": "2024-03-15T10:30:00Z",
        "details": {
          "Input (text)": "15 points/message",
          "initial_points_cost": null
        }
      },
      "pricing_error": null,
      "bot_info": {
        "creator": "@anthropic",
        "description": "Claude-3 Opus is Anthropic's most powerful model",
        "description_extra": null
      }
    }
  ]
}
```

### File Management

```python
from virginia_clemm_poe.config import DATA_FILE_PATH
import json

# Read raw JSON data
with open(DATA_FILE_PATH) as f:
    raw_data = json.load(f)

# Load into Pydantic models
from virginia_clemm_poe.models import ModelCollection
collection = ModelCollection(**raw_data)

# Save back to JSON
with open(DATA_FILE_PATH, 'w') as f:
    json.dump(collection.model_dump(), f, indent=2)
```

## Validation and Error Handling

### Model Validation

```python
from pydantic import ValidationError
from virginia_clemm_poe.models import PoeModel

def safe_model_creation(data_dict):
    """Safely create model with error handling."""
    try:
        return PoeModel(**data_dict)
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

# Example usage
raw_data = {"id": "test", "created": "invalid"}
model = safe_model_creation(raw_data)  # Returns None
```

### Data Integrity Checks

```python
def validate_collection_integrity(collection: ModelCollection):
    """Validate model collection data integrity."""
    issues = []
    
    for i, model in enumerate(collection.data):
        # Check required fields
        if not model.id:
            issues.append(f"Model {i}: Missing ID")
        
        # Check pricing consistency
        if model.pricing and model.pricing_error:
            issues.append(f"Model {model.id}: Has both pricing and error")
        
        # Check architecture validity
        if not model.architecture.input_modalities:
            issues.append(f"Model {model.id}: No input modalities")
    
    return issues
```

## Performance Considerations

### Memory Usage

```python
import sys
from virginia_clemm_poe import api

# Check memory usage of model collection
collection = api.load_models()
size_bytes = sys.getsizeof(collection)
model_count = len(collection.data)

print(f"Collection size: {size_bytes:,} bytes")
print(f"Per model: {size_bytes / model_count:.1f} bytes")
```

### Efficient Queries

```python
# Use generator expressions for large datasets
def find_models_by_criteria(models, criteria_func):
    """Memory-efficient model filtering."""
    return (model for model in models if criteria_func(model))

# Example: Find expensive models without loading all into memory
expensive_models = find_models_by_criteria(
    models,
    lambda m: m.has_pricing() and extract_numeric_cost(m.get_primary_cost()) > 100
)

# Process one at a time
for model in expensive_models:
    print(f"Expensive: {model.id}")
```

## Custom Model Extensions

### Extending PoeModel

```python
from virginia_clemm_poe.models import PoeModel
from pydantic import computed_field

class ExtendedPoeModel(PoeModel):
    """Extended model with custom computed properties."""
    
    @computed_field
    @property
    def is_multimodal(self) -> bool:
        """Check if model supports multiple input types."""
        return len(self.architecture.input_modalities) > 1
    
    @computed_field
    @property
    def cost_per_token_estimate(self) -> float | None:
        """Estimate cost per token (simplified)."""
        if not self.pricing:
            return None
        
        primary_cost = self.get_primary_cost()
        if not primary_cost or "points" not in primary_cost:
            return None
        
        # Extract points and estimate
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*points', primary_cost)
        if match:
            return float(match.group(1)) / 1000  # Assume per 1k tokens
        
        return None

# Use extended model
def upgrade_to_extended(standard_model: PoeModel) -> ExtendedPoeModel:
    """Convert standard model to extended version."""
    return ExtendedPoeModel(**standard_model.model_dump())
```

### Custom Collections

```python
from virginia_clemm_poe.models import ModelCollection, PoeModel

class SmartModelCollection(ModelCollection):
    """Enhanced collection with additional query methods."""
    
    def get_by_provider(self, provider: str) -> list[PoeModel]:
        """Get all models from a specific provider."""
        return [m for m in self.data if m.owned_by.lower() == provider.lower()]
    
    def get_by_capability(self, input_type: str = None, output_type: str = None) -> list[PoeModel]:
        """Get models by input/output capabilities."""
        results = self.data
        
        if input_type:
            results = [m for m in results if input_type in m.architecture.input_modalities]
        
        if output_type:
            results = [m for m in results if output_type in m.architecture.output_modalities]
        
        return results
    
    def get_price_range(self, min_cost: float = None, max_cost: float = None) -> list[PoeModel]:
        """Get models within a price range."""
        results = []
        
        for model in self.data:
            if not model.has_pricing():
                continue
            
            cost = extract_numeric_cost(model.get_primary_cost())
            if cost == float('inf'):
                continue
            
            if min_cost is not None and cost < min_cost:
                continue
            
            if max_cost is not None and cost > max_cost:
                continue
            
            results.append(model)
        
        return results
```

This comprehensive guide to the data models provides everything you need to understand and work with Virginia Clemm Poe's type-safe, validated data structures efficiently.