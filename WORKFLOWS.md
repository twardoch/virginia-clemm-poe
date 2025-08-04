# this_file: WORKFLOWS.md

# Virginia Clemm Poe - Workflow Guide

This guide provides step-by-step workflows for common Virginia Clemm Poe use cases. Each workflow includes commands, expected outputs, and troubleshooting tips.

## Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Regular Maintenance](#regular-maintenance)
3. [Data Discovery Workflows](#data-discovery-workflows)
4. [CI/CD Integration](#cicd-integration)
5. [Automation Scripts](#automation-scripts)
6. [Troubleshooting Common Issues](#troubleshooting-common-issues)
7. [Performance Optimization](#performance-optimization)

## First-Time Setup

Complete workflow for new users setting up Virginia Clemm Poe.

### Step 1: Install the Package

```bash
# Using pip
pip install virginia-clemm-poe

# Using uv (recommended)
uv pip install virginia-clemm-poe
```

### Step 2: Verify Installation

```bash
# Check version and basic functionality
virginia-clemm-poe --version

# Run doctor to check system requirements
virginia-clemm-poe doctor
```

Expected output:
```
Virginia Clemm Poe Doctor

Python Version:
✓ Python 3.12.0

API Key:
✗ POE_API_KEY not set
  Solution: export POE_API_KEY=your_api_key

Browser:
✗ Browser not available
  Solution: Run 'virginia-clemm-poe setup'
```

### Step 3: Get Your Poe API Key

1. Visit https://poe.com/api_key
2. Log in to your Poe account
3. Copy your API key
4. Set it as an environment variable:

```bash
# Temporary (current session only)
export POE_API_KEY=your_actual_api_key_here

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export POE_API_KEY=your_actual_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Set Up Browser Environment

```bash
# Install and configure Chrome for web scraping
virginia-clemm-poe setup
```

Expected output:
```
Setting up browser for Virginia Clemm Poe...
✓ Chrome is available!

You're all set!

To get started:
1. Set your Poe API key: export POE_API_KEY=your_key
2. Update model data: virginia-clemm-poe update
3. Search models: virginia-clemm-poe search claude
```

### Step 5: Initial Data Download

```bash
# Fetch all model data (first time takes 5-10 minutes)
virginia-clemm-poe update --verbose
```

Expected progress:
```
Updating all data (bot info + pricing)...
Fetching models from Poe API...
Found 245 models
Launching browser for web scraping...
Processing models: 100%|████████████| 245/245 [05:32<00:00]
✓ Updated 245 models successfully
```

### Step 6: Verify Data

```bash
# Check data status
virginia-clemm-poe status

# Search for a model to test
virginia-clemm-poe search "claude-3"
```

## Regular Maintenance

Keep your model data fresh with these maintenance workflows.

### Weekly Data Refresh

```bash
# Quick update (only missing data)
virginia-clemm-poe update

# Check what needs updating first
virginia-clemm-poe status
```

### Monthly Full Refresh

```bash
# Force update all data
virginia-clemm-poe update --force

# Clear caches if experiencing issues
virginia-clemm-poe cache --clear
virginia-clemm-poe clear-cache --all
```

### Data Health Check

```bash
# Run comprehensive diagnostics
virginia-clemm-poe doctor --verbose

# Check cache performance
virginia-clemm-poe cache --stats
```

## Data Discovery Workflows

### Finding Models by Capability

```python
#!/usr/bin/env python3
"""Find models with specific capabilities."""

from virginia_clemm_poe import api

# Find all vision-capable models
all_models = api.get_all_models()
vision_models = [
    m for m in all_models 
    if "image" in m.architecture.input_modalities
]

print(f"Found {len(vision_models)} vision-capable models:")
for model in vision_models[:5]:  # Show first 5
    print(f"- {model.id}: {model.architecture.modality}")
```

### Cost Analysis Workflow

```python
#!/usr/bin/env python3
"""Analyze model costs for budget planning."""

from virginia_clemm_poe import api

# Get all priced models
priced_models = api.get_models_with_pricing()

# Find budget-friendly models (< 50 points per message)
budget_models = []
for model in priced_models:
    if model.pricing and model.pricing.details.bot_message:
        cost_str = model.pricing.details.bot_message
        # Extract numeric cost (assumes format like "X points/message")
        if "points" in cost_str:
            cost = int(cost_str.split()[0])
            if cost < 50:
                budget_models.append((model, cost))

# Sort by cost
budget_models.sort(key=lambda x: x[1])

print("Top 10 Budget-Friendly Models:")
for model, cost in budget_models[:10]:
    print(f"{model.id}: {cost} points/message")
```

### Model Comparison Workflow

```bash
# Compare specific models
virginia-clemm-poe search "claude-3" --show_bot_info

# Export for analysis
virginia-clemm-poe search "gpt" > gpt_models.txt
virginia-clemm-poe search "claude" > claude_models.txt
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/update-poe-data.yml
name: Update Poe Model Data

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sundays
  workflow_dispatch:  # Manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install Virginia Clemm Poe
      run: |
        pip install virginia-clemm-poe
        virginia-clemm-poe --version
    
    - name: Set up browser
      run: virginia-clemm-poe setup
    
    - name: Update model data
      env:
        POE_API_KEY: ${{ secrets.POE_API_KEY }}
      run: |
        virginia-clemm-poe update --verbose
        virginia-clemm-poe status
    
    - name: Generate cost report
      run: |
        python scripts/generate_cost_report.py > cost_report.md
    
    - name: Commit updates
      run: |
        git config --global user.name 'github-actions[bot]'
        git config --global user.email 'github-actions[bot]@users.noreply.github.com'
        git add cost_report.md
        git commit -m 'Update Poe model cost report' || echo "No changes"
        git push
```

### GitLab CI Pipeline

```yaml
# .gitlab-ci.yml
update-poe-data:
  image: python:3.12
  
  variables:
    POE_API_KEY: $POE_API_KEY
  
  script:
    - pip install virginia-clemm-poe
    - virginia-clemm-poe setup
    - virginia-clemm-poe update
    - virginia-clemm-poe status
  
  only:
    - schedules
    - web
```

## Automation Scripts

### Daily Model Monitor

```python
#!/usr/bin/env python3
"""Monitor for new models and pricing changes."""

import json
from datetime import datetime
from pathlib import Path

from virginia_clemm_poe import api

# Load previous data
cache_file = Path("model_cache.json")
if cache_file.exists():
    with open(cache_file) as f:
        previous_data = json.load(f)
else:
    previous_data = {}

# Get current data
current_models = api.get_all_models()
current_data = {m.id: m.dict() for m in current_models}

# Find changes
new_models = set(current_data.keys()) - set(previous_data.keys())
removed_models = set(previous_data.keys()) - set(current_data.keys())

# Check for pricing changes
price_changes = []
for model_id in set(current_data.keys()) & set(previous_data.keys()):
    old_pricing = previous_data[model_id].get("pricing")
    new_pricing = current_data[model_id].get("pricing")
    
    if old_pricing != new_pricing:
        price_changes.append(model_id)

# Report changes
if new_models or removed_models or price_changes:
    print(f"Model Changes Detected - {datetime.now()}")
    print("=" * 50)
    
    if new_models:
        print(f"\nNew Models ({len(new_models)}):")
        for model_id in sorted(new_models):
            print(f"  + {model_id}")
    
    if removed_models:
        print(f"\nRemoved Models ({len(removed_models)}):")
        for model_id in sorted(removed_models):
            print(f"  - {model_id}")
    
    if price_changes:
        print(f"\nPricing Changes ({len(price_changes)}):")
        for model_id in sorted(price_changes)[:10]:  # Show first 10
            print(f"  * {model_id}")

# Save current data
with open(cache_file, "w") as f:
    json.dump(current_data, f)
```

### Bulk Cost Calculator

```python
#!/usr/bin/env python3
"""Calculate costs for bulk operations across models."""

from virginia_clemm_poe import api

def calculate_bulk_cost(model_id: str, messages: int, tokens_per_msg: int = 1000):
    """Calculate cost for bulk message processing."""
    model = api.get_model_by_id(model_id)
    if not model or not model.pricing:
        return None
    
    costs = []
    
    # Message cost
    if model.pricing.details.bot_message:
        msg_cost = model.pricing.details.bot_message
        if "points/message" in msg_cost:
            points = int(msg_cost.split()[0])
            costs.append(("Messages", messages * points))
    
    # Input token cost
    if model.pricing.details.input_text:
        input_cost = model.pricing.details.input_text
        if "points/1k tokens" in input_cost:
            points_per_1k = int(input_cost.split()[0])
            total_tokens = messages * tokens_per_msg
            costs.append(("Input Tokens", (total_tokens / 1000) * points_per_1k))
    
    return costs

# Example: Process 1000 messages with different models
models_to_compare = ["Claude-3-Opus", "GPT-4", "Claude-3-Sonnet"]
messages = 1000

print("Bulk Processing Cost Comparison")
print("=" * 50)
print(f"Processing {messages} messages (~1000 tokens each)\n")

for model_id in models_to_compare:
    costs = calculate_bulk_cost(model_id, messages)
    if costs:
        total = sum(cost for _, cost in costs)
        print(f"{model_id}:")
        for cost_type, cost in costs:
            print(f"  {cost_type}: {cost:.0f} points")
        print(f"  Total: {total:.0f} points\n")
```

## Troubleshooting Common Issues

### Issue: "No model data found"

```bash
# Check if data file exists
virginia-clemm-poe status

# If missing, run update
virginia-clemm-poe update

# If update fails, check API key
echo $POE_API_KEY
```

### Issue: "Browser not available"

```bash
# Re-run setup
virginia-clemm-poe setup --verbose

# Clear browser cache and retry
virginia-clemm-poe clear-cache --browser
virginia-clemm-poe setup
```

### Issue: "Timeout errors during update"

```bash
# Use custom timeout and retry
virginia-clemm-poe update --verbose

# Update in smaller batches
virginia-clemm-poe update --pricing  # Just pricing first
virginia-clemm-poe update --info     # Then bot info
```

### Issue: "Stale cache data"

```bash
# Check cache statistics
virginia-clemm-poe cache --stats

# Clear all caches
virginia-clemm-poe cache --clear
virginia-clemm-poe clear-cache --all

# Force reload in Python
from virginia_clemm_poe import api
api.reload_models()
```

## Performance Optimization

### Memory-Efficient Processing

```python
#!/usr/bin/env python3
"""Process models in batches to minimize memory usage."""

from virginia_clemm_poe import api

def process_models_in_batches(batch_size=50):
    """Process models in memory-efficient batches."""
    all_models = api.get_all_models()
    
    for i in range(0, len(all_models), batch_size):
        batch = all_models[i:i + batch_size]
        
        # Process batch
        for model in batch:
            # Your processing logic here
            pass
        
        # Clear batch from memory
        del batch
        
        print(f"Processed models {i} to {i + batch_size}")

# Run with optimized batch size
process_models_in_batches(batch_size=100)
```

### Cache Warming Strategy

```python
#!/usr/bin/env python3
"""Pre-warm caches for better performance."""

import asyncio
from virginia_clemm_poe import api

async def warm_caches():
    """Pre-load frequently accessed data."""
    
    # Load all models to warm primary cache
    print("Warming model cache...")
    all_models = api.get_all_models()
    print(f"Loaded {len(all_models)} models")
    
    # Pre-load common searches
    common_searches = ["claude", "gpt", "llama", "mixtral"]
    print("\nWarming search cache...")
    for query in common_searches:
        results = api.search_models(query)
        print(f"Cached '{query}': {len(results)} results")
    
    # Pre-load priced models
    print("\nWarming pricing cache...")
    priced = api.get_models_with_pricing()
    print(f"Cached {len(priced)} priced models")

# Run cache warming
asyncio.run(warm_caches())
```

### Parallel Processing Example

```python
#!/usr/bin/env python3
"""Process multiple models in parallel."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from virginia_clemm_poe import api

def analyze_model(model):
    """Analyze a single model (CPU-bound task)."""
    # Simulate analysis work
    costs = []
    if model.pricing:
        if model.pricing.details.bot_message:
            costs.append(model.pricing.details.bot_message)
        if model.pricing.details.input_text:
            costs.append(model.pricing.details.input_text)
    
    return {
        "id": model.id,
        "has_pricing": model.has_pricing(),
        "costs": costs,
        "modalities": model.architecture.input_modalities
    }

async def analyze_models_parallel():
    """Analyze all models using parallel processing."""
    models = api.get_all_models()
    
    # Use thread pool for CPU-bound tasks
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        
        # Create tasks
        tasks = [
            loop.run_in_executor(executor, analyze_model, model)
            for model in models
        ]
        
        # Wait for all tasks
        results = await asyncio.gather(*tasks)
    
    # Process results
    priced_count = sum(1 for r in results if r["has_pricing"])
    vision_count = sum(1 for r in results if "image" in r["modalities"])
    
    print(f"Analysis Complete:")
    print(f"- Total models: {len(models)}")
    print(f"- With pricing: {priced_count}")
    print(f"- Vision capable: {vision_count}")

# Run parallel analysis
asyncio.run(analyze_models_parallel())
```

## Best Practices

1. **Always check status before updates**: Run `virginia-clemm-poe status` to avoid unnecessary updates
2. **Use selective updates**: Use `--pricing` or `--info` flags for faster partial updates
3. **Monitor cache performance**: Regular `cache --stats` checks ensure optimal performance
4. **Automate maintenance**: Set up weekly cron jobs or CI pipelines for data freshness
5. **Handle errors gracefully**: Always check for None values in pricing and bot_info fields
6. **Batch operations**: Process models in batches for memory efficiency
7. **Use verbose mode for debugging**: Add `--verbose` when troubleshooting issues

## Next Steps

- Explore the [API Reference](api.py) for programmatic access
- Check [CHANGELOG.md](CHANGELOG.md) for latest features
- Read [README.md](README.md) for quick examples
- Run `virginia-clemm-poe --help` for all CLI options