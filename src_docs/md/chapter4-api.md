# Chapter 4: Python API Reference

## Overview

The Virginia Clemm Poe Python API provides programmatic access to comprehensive Poe.com model data. The API is designed for simplicity and performance, with intelligent caching and type safety through Pydantic models.

## Core Functions

### Data Loading and Management

#### `load_models(force_reload: bool = False) -> ModelCollection`

The foundational function that loads the complete Poe model dataset from the local JSON file.

```python
from virginia_clemm_poe import api

# Standard usage (cached)
collection = api.load_models()
print(f"Loaded {len(collection.data)} models")

# Force reload after external update
collection = api.load_models(force_reload=True)
```

**Parameters:**
- `force_reload` (bool): If True, bypasses cache and reloads from file

**Returns:**
- `ModelCollection`: Container with all model data and search capabilities

**Performance:**
- First call: ~50-200ms (file I/O + JSON parsing)
- Cached calls: <1ms (in-memory access)
- Memory usage: ~2-5MB for typical dataset

#### `reload_models() -> ModelCollection`

Convenience function to force reload models from disk, bypassing cache.

```python
# After external update
fresh_collection = api.reload_models()
```

### Model Retrieval

#### `get_all_models() -> list[PoeModel]`

Retrieves the complete list of models without any filtering.

```python
# Get all models
models = api.get_all_models()
print(f"Total models: {len(models)}")

# Analyze by provider
by_owner = {}
for model in models:
    owner = model.owned_by
    by_owner.setdefault(owner, []).append(model)

for owner, owner_models in sorted(by_owner.items()):
    print(f"{owner}: {len(owner_models)} models")
```

**Returns:**
- `list[PoeModel]`: Complete list of models with full metadata

#### `get_model_by_id(model_id: str) -> PoeModel | None`

Fast, exact-match lookup for a specific model by ID.

```python
# Get specific model
model = api.get_model_by_id("Claude-3-Opus")
if model:
    print(f"Found: {model.model_name}")
    if model.pricing:
        print(f"Input cost: {model.pricing.details.get('Input (text)', 'N/A')}")
else:
    print("Model not found")
```

**Parameters:**
- `model_id` (str): Exact model ID (case-sensitive)

**Returns:**
- `PoeModel | None`: The matching model or None if not found

**Performance:**
- Lookup time: <1ms (uses internal dictionary mapping)

### Model Search and Filtering

#### `search_models(query: str) -> list[PoeModel]`

Case-insensitive search across model IDs and names.

```python
# Find Claude models
claude_models = api.search_models("claude")
print(f"Found {len(claude_models)} Claude models")

# Find models by capability
vision_models = api.search_models("vision")
coding_models = api.search_models("code")
```

**Parameters:**
- `query` (str): Search term (case-insensitive)

**Returns:**
- `list[PoeModel]`: Matching models sorted by ID

#### `get_models_with_pricing() -> list[PoeModel]`

Get all models that have valid pricing information.

```python
# Get models with pricing for cost analysis
priced_models = api.get_models_with_pricing()
print(f"Models with pricing: {len(priced_models)}")

# Find affordable models
budget_models = [
    m for m in priced_models 
    if m.pricing and "Input (text)" in m.pricing.details
]
```

**Returns:**
- `list[PoeModel]`: Models with valid pricing data

#### `get_models_needing_update() -> list[PoeModel]`

Identify models that need pricing information updated.

```python
# Check data completeness
need_update = api.get_models_needing_update()
all_models = api.get_all_models()

completion_rate = (len(all_models) - len(need_update)) / len(all_models) * 100
print(f"Data completion: {completion_rate:.1f}%")
```

**Returns:**
- `list[PoeModel]`: Models requiring data updates

## Data Models

### PoeModel

The core model representing a Poe.com AI model.

```python
from virginia_clemm_poe.models import PoeModel

# Access model properties
model = api.get_model_by_id("Claude-3-Opus")
if model:
    print(f"ID: {model.id}")
    print(f"Name: {model.model_name}")
    print(f"Owner: {model.owned_by}")
    print(f"Created: {model.created}")
    print(f"Description: {model.description}")
```

**Key Properties:**
- `id: str` - Unique model identifier
- `model_name: str` - Display name
- `owned_by: str` - Model provider/owner
- `created: str` - Creation timestamp
- `description: str` - Model description
- `architecture: Architecture` - Input/output capabilities
- `pricing: Pricing | None` - Cost information
- `bot_info: BotInfo | None` - Creator and metadata
- `pricing_error: str | None` - Error message if scraping failed

**Utility Methods:**
```python
# Check if model has pricing data
if model.has_pricing():
    print("Pricing available")

# Check if model needs update
if model.needs_pricing_update():
    print("Needs pricing update")
```

### Pricing

Contains cost information for a model.

```python
if model.pricing:
    # Access pricing details
    details = model.pricing.details
    input_cost = details.get("Input (text)", "N/A")
    output_cost = details.get("Bot message", "N/A")
    
    print(f"Input: {input_cost}")
    print(f"Output: {output_cost}")
    print(f"Last checked: {model.pricing.checked_at}")
```

**Properties:**
- `details: dict[str, str]` - Cost breakdown
- `checked_at: datetime` - Last update timestamp

**Common Pricing Fields:**
- `"Input (text)"` - Cost per text input
- `"Input (image)"` - Cost per image input
- `"Bot message"` - Cost per output message
- `"Chat history loaded"` - History loading cost
- `"Cache discount"` - Caching discount rate

### BotInfo

Creator and description metadata.

```python
if model.bot_info:
    print(f"Creator: {model.bot_info.creator}")
    print(f"Description: {model.bot_info.description}")
    if model.bot_info.description_extra:
        print(f"Extra info: {model.bot_info.description_extra}")
```

**Properties:**
- `creator: str` - Bot creator handle
- `description: str` - Main description
- `description_extra: str | None` - Additional details

### Architecture

Model capability information.

```python
arch = model.architecture
print(f"Input types: {arch.input_modalities}")
print(f"Output types: {arch.output_modalities}")
print(f"Modality: {arch.modality}")
```

**Properties:**
- `input_modalities: list[str]` - Supported inputs
- `output_modalities: list[str]` - Supported outputs
- `modality: str` - Primary mode description

## Advanced Usage Examples

### Cost Analysis

```python
def analyze_costs():
    """Analyze model costs across providers."""
    models = api.get_models_with_pricing()
    
    # Group by provider
    by_provider = {}
    for model in models:
        provider = model.owned_by
        by_provider.setdefault(provider, []).append(model)
    
    # Calculate average costs
    for provider, provider_models in by_provider.items():
        costs = []
        for model in provider_models:
            if model.pricing and "Input (text)" in model.pricing.details:
                cost_str = model.pricing.details["Input (text)"]
                # Extract numeric cost (simplified parsing)
                try:
                    cost = float(cost_str.replace("$", "").split()[0])
                    costs.append(cost)
                except:
                    continue
        
        if costs:
            avg_cost = sum(costs) / len(costs)
            print(f"{provider}: ${avg_cost:.4f} average")

analyze_costs()
```

### Model Comparison

```python
def compare_models(model_ids: list[str]):
    """Compare multiple models side by side."""
    models = [api.get_model_by_id(mid) for mid in model_ids]
    models = [m for m in models if m is not None]
    
    print(f"{'Model':<25} {'Provider':<15} {'Input Cost':<15}")
    print("-" * 55)
    
    for model in models:
        provider = model.owned_by
        if model.pricing and "Input (text)" in model.pricing.details:
            cost = model.pricing.details["Input (text)"]
        else:
            cost = "N/A"
        
        print(f"{model.model_name:<25} {provider:<15} {cost:<15}")

# Compare popular models
compare_models([
    "Claude-3-Opus",
    "Claude-3-Sonnet", 
    "GPT-4",
    "GPT-4-Turbo"
])
```

### Data Quality Monitoring

```python
def check_data_quality():
    """Monitor data quality and coverage."""
    all_models = api.get_all_models()
    priced_models = api.get_models_with_pricing()
    need_update = api.get_models_needing_update()
    
    print(f"📊 Data Quality Report")
    print(f"Total models: {len(all_models)}")
    print(f"With pricing: {len(priced_models)}")
    print(f"Need update: {len(need_update)}")
    
    # Coverage percentage
    coverage = len(priced_models) / len(all_models) * 100 if all_models else 0
    print(f"Coverage: {coverage:.1f}%")
    
    # Error analysis
    errors = [m for m in all_models if m.pricing_error]
    if errors:
        print(f"Models with errors: {len(errors)}")
        error_types = {}
        for model in errors:
            error = model.pricing_error or "Unknown"
            error_types[error] = error_types.get(error, 0) + 1
        
        for error, count in sorted(error_types.items()):
            print(f"  {error}: {count}")

check_data_quality()
```

### Real-time Monitoring

```python
import time
from pathlib import Path

def monitor_updates(interval: int = 60):
    """Monitor for data file changes and reload automatically."""
    from virginia_clemm_poe.config import DATA_FILE_PATH
    
    if not DATA_FILE_PATH.exists():
        print("Data file not found. Run update first.")
        return
    
    last_modified = DATA_FILE_PATH.stat().st_mtime
    print(f"Monitoring {DATA_FILE_PATH} for changes...")
    
    while True:
        try:
            current_modified = DATA_FILE_PATH.stat().st_mtime
            if current_modified > last_modified:
                print("📊 Data file updated, reloading...")
                collection = api.reload_models()
                print(f"✅ Reloaded {len(collection.data)} models")
                last_modified = current_modified
            
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Monitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval)

# Start monitoring
# monitor_updates(60)  # Check every minute
```

## Error Handling

### Common Error Patterns

```python
def safe_model_access(model_id: str):
    """Safely access model data with comprehensive error handling."""
    try:
        # Load models
        collection = api.load_models()
        if not collection.data:
            print("No data available. Run 'virginia-clemm-poe update'")
            return None
        
        # Get specific model
        model = api.get_model_by_id(model_id)
        if not model:
            print(f"Model '{model_id}' not found")
            # Try fuzzy search
            results = api.search_models(model_id.lower())
            if results:
                print(f"Similar models: {[m.id for m in results[:3]]}")
            return None
        
        # Access pricing safely
        if model.pricing:
            return model
        elif model.pricing_error:
            print(f"Pricing error: {model.pricing_error}")
            return model
        else:
            print("No pricing data available")
            return model
            
    except FileNotFoundError:
        print("Data file missing. Run 'virginia-clemm-poe update --all'")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Data Validation

```python
def validate_model_data(model: PoeModel) -> bool:
    """Validate model data completeness."""
    issues = []
    
    if not model.id:
        issues.append("Missing model ID")
    
    if not model.model_name:
        issues.append("Missing model name")
    
    if not model.owned_by:
        issues.append("Missing owner information")
    
    if model.pricing is None and model.pricing_error is None:
        issues.append("No pricing data or error information")
    
    if issues:
        print(f"Validation issues for {model.id}: {', '.join(issues)}")
        return False
    
    return True

# Validate all models
models = api.get_all_models()
valid_models = [m for m in models if validate_model_data(m)]
print(f"Valid models: {len(valid_models)}/{len(models)}")
```

## Best Practices

### Performance Optimization

1. **Use Caching**: Don't call `reload_models()` unnecessarily
2. **Exact Lookups**: Use `get_model_by_id()` for known IDs instead of search
3. **Batch Operations**: Process multiple models in single loops
4. **Filter Early**: Use specific functions like `get_models_with_pricing()`

### Data Freshness

1. **Check Timestamps**: Monitor `pricing.checked_at` for data age
2. **Reload After Updates**: Call `reload_models()` after external updates
3. **Monitor Coverage**: Use `get_models_needing_update()` for quality checks

### Error Resilience

1. **Check for None**: Always verify pricing and bot_info existence
2. **Handle Missing Data**: Gracefully handle missing models
3. **Validate Assumptions**: Don't assume specific pricing fields exist

## Integration Patterns

### With Data Analysis Libraries

```python
import pandas as pd

def models_to_dataframe():
    """Convert model data to pandas DataFrame for analysis."""
    models = api.get_models_with_pricing()
    
    data = []
    for model in models:
        row = {
            'id': model.id,
            'name': model.model_name,
            'provider': model.owned_by,
            'created': model.created,
        }
        
        if model.pricing:
            row['input_cost'] = model.pricing.details.get('Input (text)', None)
            row['output_cost'] = model.pricing.details.get('Bot message', None)
            row['pricing_date'] = model.pricing.checked_at
        
        if model.bot_info:
            row['creator'] = model.bot_info.creator
        
        data.append(row)
    
    return pd.DataFrame(data)

# Create DataFrame for analysis
df = models_to_dataframe()
print(df.head())
```

### With Web Frameworks

```python
from fastapi import FastAPI, HTTPException
from virginia_clemm_poe import api

app = FastAPI()

@app.get("/models")
def list_models(with_pricing: bool = False):
    """API endpoint to list models."""
    if with_pricing:
        models = api.get_models_with_pricing()
    else:
        models = api.get_all_models()
    
    return {
        "count": len(models),
        "models": [{"id": m.id, "name": m.model_name} for m in models]
    }

@app.get("/models/{model_id}")
def get_model(model_id: str):
    """API endpoint to get specific model."""
    model = api.get_model_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return model.dict()
```

This comprehensive API reference provides everything you need to integrate Virginia Clemm Poe into your Python applications efficiently and reliably.