# Virginia Clemm Poe

[![PyPI version](https://badge.fury.io/py/virginia-clemm-poe.svg)](https://badge.fury.io/py/virginia-clemm-poe)
[![Python Support](https://img.shields.io/pypi/pyversions/virginia-clemm-poe.svg)](https://pypi.org/project/virginia-clemm-poe/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python package providing programmatic access to Poe.com model data with pricing information.

## Overview

Virginia Clemm Poe is a companion tool for Poe.com's API (introduced August 25, 2024) that fetches and maintains comprehensive model data including pricing information. The package provides both a Python API for querying model data and a CLI for updating the dataset.

## Features

- **Model Data Access**: Query Poe.com models by various criteria including ID, name, and other attributes
- **Pricing Information**: Automatically scrapes and syncs pricing data for all available models
- **Pydantic Models**: Fully typed data models for easy integration
- **CLI Interface**: Fire-based CLI for updating data and searching models
- **Browser Setup**: Automated setup for web scraping dependencies

## Installation

```bash
pip install virginia-clemm-poe
```

## Quick Start

### Python API

```python
from virginia_clemm_poe import api

# Search for models
models = api.search_models("claude")
for model in models:
    print(f"{model.id}: {model.get_primary_cost()}")

# Get model by ID
model = api.get_model_by_id("claude-3-opus")
if model and model.pricing:
    print(f"Cost: {model.get_primary_cost()}")
    print(f"Updated: {model.pricing.checked_at}")

# Get all models with pricing
priced_models = api.get_models_with_pricing()
print(f"Found {len(priced_models)} models with pricing")
```

### Command Line Interface

```bash
# Set up browser for web scraping
virginia-clemm-poe setup

# Update model data with pricing information
export POE_API_KEY=your_api_key
virginia-clemm-poe update --pricing

# Search for models
virginia-clemm-poe search "gpt-4"

# List all models with summary
virginia-clemm-poe list

# List only models with pricing
virginia-clemm-poe list --with-pricing
```

## API Reference

### Core Functions

#### `api.search_models(query: str) -> List[PoeModel]`
Search for models by ID or name (case-insensitive).

#### `api.get_model_by_id(model_id: str) -> Optional[PoeModel]`
Get a specific model by its ID.

#### `api.get_all_models() -> List[PoeModel]`
Get all available models.

#### `api.get_models_with_pricing() -> List[PoeModel]`
Get all models that have pricing information.

#### `api.get_models_needing_update() -> List[PoeModel]`
Get models that need pricing update.

#### `api.reload_models() -> ModelCollection`
Force reload models from disk.

### Data Models

#### PoeModel
```python
class PoeModel:
    id: str
    created: int
    owned_by: str
    root: str
    parent: Optional[str]
    architecture: Architecture
    pricing: Optional[Pricing]
    pricing_error: Optional[str]
    
    def has_pricing() -> bool
    def needs_pricing_update() -> bool
    def get_primary_cost() -> Optional[str]
```

#### Architecture
```python
class Architecture:
    input_modalities: List[str]
    output_modalities: List[str]
    modality: str
```

#### Pricing
```python
class Pricing:
    checked_at: datetime
    details: PricingDetails
```

#### PricingDetails
Flexible pricing details supporting various cost structures:
- Standard fields: `input_text`, `input_image`, `bot_message`, `chat_history`
- Alternative fields: `total_cost`, `image_output`, `video_output`, etc.

## CLI Commands

### setup
Set up browser for web scraping (installs Chrome for Testing if needed).

```bash
virginia-clemm-poe setup
```

### update
Update model data from Poe API and optionally scrape pricing information.

```bash
virginia-clemm-poe update --pricing [--force] [--verbose]
```

Options:
- `--pricing`: Update pricing information (requires web scraping)
- `--all`: Update all data (equivalent to --pricing)
- `--api_key`: Override POE_API_KEY environment variable
- `--force`: Force update even if data exists
- `--debug_port`: Chrome debug port (default: 9222)
- `--verbose`: Enable verbose logging

### search
Search for models by ID or name.

```bash
virginia-clemm-poe search "claude" [--show-pricing]
```

Options:
- `--show-pricing`: Show pricing information if available (default: True)

### list
List all available models.

```bash
virginia-clemm-poe list [--with-pricing] [--limit 10]
```

Options:
- `--with-pricing`: Only show models with pricing information
- `--limit`: Limit number of results

## Requirements

- Python 3.12+
- Chrome or Chromium browser (for pricing data scraping)
- Poe API key (set as `POE_API_KEY` environment variable)

## Data Storage

Model data is stored in `src/virginia_clemm_poe/data/poe_models.json` within the package directory. The data includes:
- Basic model information (ID, name, capabilities)
- Detailed pricing structure
- Timestamps for data freshness

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/twardoch/virginia-clemm-poe.git
cd virginia-clemm-poe

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Set up browser for development
virginia-clemm-poe setup
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=virginia_clemm_poe
```

### Dependencies

This package uses:
- `uv` for dependency management
- `httpx` for API requests
- `playwright` for web scraping
- `pydantic` for data models
- `fire` for CLI interface
- `rich` for terminal UI
- `loguru` for logging
- `hatch-vcs` for automatic versioning from git tags

## API Examples

### Get Model Information

```python
from virginia_clemm_poe import api

# Get a specific model
model = api.get_model_by_id("claude-3-opus")
if model:
    print(f"Model: {model.id}")
    print(f"Input modalities: {model.architecture.input_modalities}")
    if model.pricing:
        primary_cost = model.get_primary_cost()
        print(f"Cost: {primary_cost}")
        print(f"Last updated: {model.pricing.checked_at}")

# Search for models
gpt_models = api.search_models("gpt")
for model in gpt_models:
    print(f"- {model.id}: {model.architecture.modality}")
```

### Filter Models by Criteria

```python
from virginia_clemm_poe import api

# Get all models with pricing
priced_models = api.get_models_with_pricing()
print(f"Models with pricing: {len(priced_models)}")

# Get models needing pricing update
need_update = api.get_models_needing_update()
print(f"Models needing update: {len(need_update)}")

# Get models with specific modality
all_models = api.get_all_models()
text_to_image = [m for m in all_models if m.architecture.modality == "text->image"]
print(f"Text-to-image models: {len(text_to_image)}")
```

### Working with Pricing Data

```python
from virginia_clemm_poe import api

# Get pricing details for a model
model = api.get_model_by_id("claude-3-haiku")
if model and model.pricing:
    details = model.pricing.details
    
    # Access standard pricing fields
    if details.input_text:
        print(f"Text input: {details.input_text}")
    if details.bot_message:
        print(f"Bot message: {details.bot_message}")
    
    # Alternative pricing formats
    if details.total_cost:
        print(f"Total cost: {details.total_cost}")
    
    # Get primary cost (auto-detected)
    print(f"Primary cost: {model.get_primary_cost()}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Author

Adam Twardoch <adam+github@twardoch.com>

## License

Licensed under the Apache License 2.0. See LICENSE file for details.

## Acknowledgments

Named after Virginia Clemm Poe (1822–1847), wife of Edgar Allan Poe, reflecting the connection to Poe.com.

## Disclaimer

This is an unofficial companion tool for Poe.com's API. It is not affiliated with or endorsed by Poe.com or Quora, Inc.