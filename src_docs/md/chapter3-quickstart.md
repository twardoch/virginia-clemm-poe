# Chapter 3: Quick Start Guide

## Your First 5 Minutes

This guide will get you up and running with Virginia Clemm Poe in just a few minutes. By the end, you'll have:

- ✅ Installed and configured the package
- ✅ Updated your local model dataset
- ✅ Found and analyzed AI models
- ✅ Used both Python API and CLI

## Step 1: Installation and Setup

```bash
# Install the package
pip install virginia-clemm-poe

# Set up browser for web scraping
virginia-clemm-poe setup

# Set your Poe API key
export POE_API_KEY="your_poe_api_key_here"
```

!!! tip "Get Your API Key"
    Visit [Poe.com](https://poe.com) → Settings → API to generate your free API key.

## Step 2: Initial Data Update

```bash
# Update model data with pricing information
virginia-clemm-poe update --pricing
```

This command will:
- Fetch all models from the Poe API
- Scrape pricing information from the website
- Save the enriched dataset locally

!!! note "First Run"
    The first update may take 5-10 minutes as it scrapes data for hundreds of models. Subsequent updates are much faster as they only update changed models.

## Step 3: Basic CLI Usage

### Search for Models

```bash
# Find Claude models
virginia-clemm-poe search "claude"

# Find GPT models
virginia-clemm-poe search "gpt"

# Find models by capability
virginia-clemm-poe search "image"
```

### List All Models

```bash
# Show all available models
virginia-clemm-poe list

# Show only models with pricing data
virginia-clemm-poe list --with-pricing

# Show models in JSON format
virginia-clemm-poe list --format json
```

### Get Model Details

```bash
# Get detailed information about a specific model
virginia-clemm-poe info "claude-3-opus"
```

## Step 4: Basic Python API Usage

Create a Python script to explore the model data:

```python
# quick_start.py
from virginia_clemm_poe import api

def main():
    # Search for models
    print("🔍 Searching for Claude models...")
    claude_models = api.search_models(query="claude")
    print(f"Found {len(claude_models)} Claude models")
    
    # Get a specific model
    print("\n📊 Getting Claude 3 Opus details...")
    opus = api.get_model_by_id("claude-3-opus")
    if opus:
        print(f"Model: {opus.model_name}")
        print(f"Description: {opus.description}")
        if opus.pricing:
            input_cost = opus.pricing.details.get("Input (text)", "N/A")
            print(f"Input cost: {input_cost}")
    
    # List all models with pricing
    print("\n💰 Models with pricing data...")
    models_with_pricing = api.list_models(with_pricing=True)
    print(f"Found {len(models_with_pricing)} models with pricing")
    
    # Find cheapest text model
    print("\n🎯 Finding cheapest text models...")
    text_models = [m for m in models_with_pricing 
                   if m.pricing and "Input (text)" in m.pricing.details]
    
    if text_models:
        # Sort by input cost (assuming cost is in format like "$0.015 / 1k tokens")
        def extract_cost(model):
            cost_str = model.pricing.details.get("Input (text)", "$999")
            # Simple extraction - in real use, you'd want more robust parsing
            try:
                return float(cost_str.replace("$", "").split()[0])
            except:
                return 999.0
        
        cheapest = min(text_models, key=extract_cost)
        print(f"Cheapest: {cheapest.model_name}")
        print(f"Cost: {cheapest.pricing.details['Input (text)']}")

if __name__ == "__main__":
    main()
```

Run the script:
```bash
python quick_start.py
```

## Common Use Cases

### Use Case 1: Find Models by Price Range

```python
from virginia_clemm_poe import api

def find_affordable_models(max_cost=0.01):
    """Find models under a certain cost threshold."""
    models = api.list_models(with_pricing=True)
    affordable = []
    
    for model in models:
        if model.pricing and "Input (text)" in model.pricing.details:
            cost_str = model.pricing.details["Input (text)"]
            # Extract numeric cost (simplified)
            try:
                cost = float(cost_str.replace("$", "").split()[0])
                if cost <= max_cost:
                    affordable.append((model.model_name, cost))
            except:
                continue
    
    return sorted(affordable, key=lambda x: x[1])

# Find models under $0.01 per 1k tokens
cheap_models = find_affordable_models(0.01)
for name, cost in cheap_models[:5]:
    print(f"{name}: ${cost}")
```

### Use Case 2: Compare Model Capabilities

```python
from virginia_clemm_poe import api

def compare_models(model_ids):
    """Compare multiple models side by side."""
    models = [api.get_model_by_id(mid) for mid in model_ids]
    
    print(f"{'Model':<20} {'Input Cost':<15} {'Output Cost':<15}")
    print("-" * 50)
    
    for model in models:
        if model and model.pricing:
            input_cost = model.pricing.details.get("Input (text)", "N/A")
            output_cost = model.pricing.details.get("Bot message", "N/A")
            print(f"{model.model_name:<20} {input_cost:<15} {output_cost:<15}")

# Compare popular models
compare_models([
    "claude-3-opus", 
    "gpt-4", 
    "claude-3-sonnet"
])
```

### Use Case 3: Monitor Model Availability

```bash
#!/bin/bash
# monitor_models.sh - Check if specific models are available

models=("claude-3-opus" "gpt-4" "gemini-pro")

for model in "${models[@]}"; do
    echo "Checking $model..."
    virginia-clemm-poe info "$model" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $model is available"
    else
        echo "❌ $model is not available"
    fi
done
```

## CLI Workflow Examples

### Daily Update Routine

```bash
#!/bin/bash
# daily_update.sh - Daily model data maintenance

echo "🔄 Starting daily update..."

# Update models that might have changed
virginia-clemm-poe update --pricing --changed-only

# Check for new models
virginia-clemm-poe update --new-only

# Generate a summary report
virginia-clemm-poe stats

echo "✅ Daily update complete"
```

### Research Workflow

```bash
# 1. Update dataset
virginia-clemm-poe update --all

# 2. Search for specific capabilities
virginia-clemm-poe search "vision" > vision_models.txt
virginia-clemm-poe search "code" > coding_models.txt

# 3. Get detailed pricing for interesting models
virginia-clemm-poe info "claude-3-opus" --format json > opus_details.json
virginia-clemm-poe info "gpt-4-vision" --format json > gpt4v_details.json

# 4. Generate comparison report
virginia-clemm-poe compare "claude-3-opus" "gpt-4" --output report.html
```

## Integration Examples

### Jupyter Notebook Integration

```python
# In Jupyter notebook
import pandas as pd
from virginia_clemm_poe import api

# Load all models into a DataFrame
models = api.list_models(with_pricing=True)
df = pd.DataFrame([
    {
        'name': m.model_name,
        'provider': m.bot_info.creator if m.bot_info else 'Unknown',
        'input_cost': m.pricing.details.get('Input (text)', 'N/A') if m.pricing else 'N/A',
        'description': m.description[:100] + '...' if len(m.description) > 100 else m.description
    }
    for m in models
])

# Analyze the data
print(f"Total models: {len(df)}")
print(f"Unique providers: {df['provider'].nunique()}")
df.head()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from virginia_clemm_poe import api

app = FastAPI()

@app.get("/models/search/{query}")
def search_models(query: str):
    """Search for models matching the query."""
    models = api.search_models(query=query)
    return {"query": query, "count": len(models), "models": models}

@app.get("/models/{model_id}")
def get_model(model_id: str):
    """Get detailed information about a specific model."""
    model = api.get_model_by_id(model_id)
    if not model:
        return {"error": "Model not found"}
    return model

@app.get("/stats")
def get_stats():
    """Get statistics about the model dataset."""
    all_models = api.list_models()
    with_pricing = api.list_models(with_pricing=True)
    
    return {
        "total_models": len(all_models),
        "models_with_pricing": len(with_pricing),
        "coverage": len(with_pricing) / len(all_models) * 100
    }
```

## Next Steps

Now that you've got the basics down, explore:

1. **[Python API Reference](chapter4-api.md)** - Complete API documentation
2. **[CLI Commands](chapter5-cli.md)** - All available command-line options
3. **[Data Models](chapter6-models.md)** - Understanding the data structures
4. **[Configuration](chapter8-configuration.md)** - Advanced configuration options

## Quick Reference

### Essential Commands
```bash
# Setup
virginia-clemm-poe setup
virginia-clemm-poe update --pricing

# Search and explore
virginia-clemm-poe search "query"
virginia-clemm-poe list --with-pricing
virginia-clemm-poe info "model-id"

# Maintenance
virginia-clemm-poe update --changed-only
virginia-clemm-poe stats
virginia-clemm-poe diagnose
```

### Essential Python Imports
```python
from virginia_clemm_poe import api
from virginia_clemm_poe.models import PoeModel, Pricing, BotInfo
```

!!! tip "Performance Tips"
    - Use `--changed-only` for faster updates
    - Cache search results for repeated queries
    - Use `--format json` for programmatic processing
    - Monitor logs with `--verbose` for debugging