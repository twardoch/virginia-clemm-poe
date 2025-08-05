# Virginia Clemm Poe

[![PyPI version](https://badge.fury.io/py/virginia-clemm-poe.svg)](https://badge.fury.io/py/virginia-clemm-poe) [![Python Support](https://img.shields.io/pypi/pyversions/virginia-clemm-poe.svg)](https://pypi.org/project/virginia-clemm-poe/) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python package providing programmatic access to Poe.com model data with pricing information.

## [∞](#overview) Overview

Virginia Clemm Poe is a companion tool for Poe.com's API (introduced August 25, 2024) that fetches and maintains comprehensive model data including pricing information. The package provides both a Python API for querying model data and a CLI for updating the dataset.

This link points to the data file that is updated by the `virginia-clemm-poe` CLI tool. Note: this is a static copy, does not reflect the latest data from Poe’s API. 

### [∞](#) 

## [∞](#features) Features

- **Model Data Access**: Query Poe.com models by various criteria including ID, name, and other attributes
- **Bot Information**: Captures bot creator, description, and additional metadata
- **Pricing Information**: Automatically scrapes and syncs pricing data for all available models
- **Pydantic Models**: Fully typed data models for easy integration
- **CLI Interface**: Fire-based CLI for updating data and searching models
- **Browser Automation**: Powered by PlaywrightAuthor with Chrome for Testing support
- **Session Reuse**: Maintains authenticated browser sessions across script runs for efficient scraping

## [∞](#installation) Installation

```bash
pip install virginia-clemm-poe
```

## [∞](#quick-start) Quick Start

### [∞](#python-api) Python API

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

#### [∞](#programmatic-session-reuse) Programmatic Session Reuse

```python
from virginia_clemm_poe.browser_pool import BrowserPool

# Use session reuse for authenticated scraping
async def scrape_with_session_reuse():
    pool = BrowserPool(reuse_sessions=True)
    await pool.start()
    
    # Get a page that reuses existing authenticated session
    page = await pool.get_reusable_page()
    await page.goto("https://poe.com/some-protected-page")
    # You're already logged in!
    
    await pool.stop()
```

### [∞](#command-line-interface) Command Line Interface

```bash
# Set up browser for web scraping
virginia-clemm-poe setup

# Update model data (bot info + pricing) - default behavior
export POE_API_KEY=your_api_key
virginia-clemm-poe update

# Update only bot info (creator, description)
virginia-clemm-poe update --info

# Update only pricing information
virginia-clemm-poe update --pricing

# Force update all data even if it exists
virginia-clemm-poe update --force

# Search for models
virginia-clemm-poe search "gpt-4"

# Search with bot info displayed
virginia-clemm-poe search "claude" --show-bot-info

# List all models with summary
virginia-clemm-poe list

# List only models with pricing
virginia-clemm-poe list --with-pricing
```

```
NAME
    __main__.py - Virginia Clemm Poe - Poe.com model data management CLI.

SYNOPSIS
    __main__.py COMMAND

DESCRIPTION
    A comprehensive tool for accessing and maintaining Poe.com model information with
    pricing data. Use 'virginia-clemm-poe COMMAND --help' for detailed command info.

    Quick Start:
        1. virginia-clemm-poe setup     # One-time browser installation
        2. virginia-clemm-poe update    # Fetch/refresh model data  
        3. virginia-clemm-poe search    # Query models by name/ID

    Common Workflows:
        - Initial Setup: setup → update → search
        - Regular Use: search (data cached locally)
        - Maintenance: status → update (if needed)
        - Troubleshooting: doctor → follow recommendations

COMMANDS
    COMMAND is one of the following:

     cache
       Monitor cache performance and hit rates - optimize your API usage.

     clear_cache
       Clear cache and stored data - use when experiencing stale data issues.

     doctor
       Diagnose and fix common issues - run this when something goes wrong.

     list
       List all available models - get an overview of the entire dataset.

     search
       Find models by name or ID - your primary command for discovering models.

     setup
       Set up Chrome browser for web scraping - required before first update.

     status
       Check system health and data freshness - your go-to diagnostic command.

     update
       Fetch latest model data from Poe - run weekly or when new models appear.
```

### [∞](#session-reuse-workflow-recommended) Session Reuse Workflow (Recommended)

Virginia Clemm Poe now supports PlaywrightAuthor's session reuse feature, which maintains authenticated browser sessions across script runs. This is particularly useful for scraping data that requires login.

```bash
# Step 1: Launch Chrome for Testing and log in manually
playwrightauthor browse

# Step 2: In the browser window that opens, log into Poe.com
# The browser stays running after you close the terminal

# Step 3: Run virginia-clemm-poe commands - they'll reuse the authenticated session
export POE_API_KEY=your_api_key
virginia-clemm-poe update --pricing

# The scraper will reuse your logged-in session for faster, more reliable data collection
```

This approach provides several benefits:
- **One-time authentication**: Log in once manually, then all scripts use that session
- **Faster scraping**: No need to handle login flows in automation
- **More reliable**: Avoids bot detection during login

## [∞](#api-reference) API Reference

### [∞](#core-functions) Core Functions

#### [∞](#apisearch_modelsquery-str---listpoemodel) `api.search_models(query: str) -> List[PoeModel]`

Search for models by ID or name (case-insensitive).

#### [∞](#apiget_model_by_idmodel_id-str---optionalpoemodel) `api.get_model_by_id(model_id: str) -> Optional[PoeModel]`

Get a specific model by its ID.

#### [∞](#apiget_all_models---listpoemodel) `api.get_all_models() -> List[PoeModel]`

Get all available models.

#### [∞](#apiget_models_with_pricing---listpoemodel) `api.get_models_with_pricing() -> List[PoeModel]`

Get all models that have pricing information.

#### [∞](#apiget_models_needing_update---listpoemodel) `api.get_models_needing_update() -> List[PoeModel]`

Get models that need pricing update.

#### [∞](#apireload_models---modelcollection) `api.reload_models() -> ModelCollection`

Force reload models from disk.

### [∞](#data-models) Data Models

#### [∞](#poemodel) PoeModel

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
    bot_info: Optional[BotInfo]

    def has_pricing() -> bool
    def needs_pricing_update() -> bool
    def get_primary_cost() -> Optional[str]
```

#### [∞](#architecture) Architecture

```python
class Architecture:
    input_modalities: List[str]
    output_modalities: List[str]
    modality: str
```

#### [∞](#botinfo) BotInfo

```python
class BotInfo:
    creator: Optional[str]        # e.g., "@openai"
    description: Optional[str]    # Main bot description
    description_extra: Optional[str]  # Additional disclaimer text
```

#### [∞](#pricing) Pricing

```python
class Pricing:
    checked_at: datetime
    details: PricingDetails
```

#### [∞](#pricingdetails) PricingDetails

Flexible pricing details supporting various cost structures:

- Standard fields: `input_text`, `input_image`, `bot_message`, `chat_history`
- Alternative fields: `total_cost`, `image_output`, `video_output`, etc.
- Bot info field: `initial_points_cost` (e.g., "206+ points")

## [∞](#cli-commands) CLI Commands

### [∞](#setup) setup

Set up browser for web scraping (handled automatically by PlaywrightAuthor).

```bash
virginia-clemm-poe setup
```

### [∞](#update) update

Update model data from Poe API and scrape additional information.

```bash
virginia-clemm-poe update [--info] [--pricing] [--all] [--force] [--verbose]
```

Options:

- `--info`: Update only bot info (creator, description)
- `--pricing`: Update only pricing information
- `--all`: Update both info and pricing (default: True)
- `--api_key`: Override POE_API_KEY environment variable
- `--force`: Force update even if data exists
- `--debug_port`: Chrome debug port (default: 9222)
- `--verbose`: Enable verbose logging

By default, the update command updates both bot info and pricing. Use `--info` or `--pricing` to update only specific data.

### [∞](#search) search

Search for models by ID or name.

```bash
virginia-clemm-poe search "claude" [--show-pricing] [--show-bot-info]
```

Options:

- `--show-pricing`: Show pricing information if available (default: True)
- `--show-bot-info`: Show bot info (creator, description) (default: False)

### [∞](#list) list

List all available models.

```bash
virginia-clemm-poe list [--with-pricing] [--limit 10]
```

Options:

- `--with-pricing`: Only show models with pricing information
- `--limit`: Limit number of results

## [∞](#requirements) Requirements

- Python 3.12+
- Chrome or Chromium browser (automatically managed by PlaywrightAuthor)
- Poe API key (set as `POE_API_KEY` environment variable)

## [∞](#data-storage) Data Storage

Model data is stored in `src/virginia_clemm_poe/data/poe_models.json` within the package directory. The data includes:

- Basic model information (ID, name, capabilities)
- Detailed pricing structure
- Timestamps for data freshness

## [∞](#development) Development

### [∞](#setting-up-development-environment) Setting Up Development Environment

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

### [∞](#running-tests) Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=virginia_clemm_poe
```

### [∞](#dependencies) Dependencies

This package uses:

- `uv` for dependency management
- `httpx` for API requests
- `playwrightauthor` for browser automation
- `pydantic` for data models
- `fire` for CLI interface
- `rich` for terminal UI
- `loguru` for logging
- `hatch-vcs` for automatic versioning from git tags

## [∞](#api-examples) API Examples

### [∞](#get-model-information) Get Model Information

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

### [∞](#filter-models-by-criteria) Filter Models by Criteria

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

### [∞](#working-with-pricing-data) Working with Pricing Data

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

## [∞](#contributing) Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## [∞](#author) Author

Adam Twardoch <adam+github@twardoch.com>

## [∞](#license) License

Licensed under the Apache License 2.0. See LICENSE file for details.

## [∞](#acknowledgments) Acknowledgments

Named after Virginia Clemm Poe (1822–1847), wife of Edgar Allan Poe, reflecting the connection to Poe.com.

## [∞](#disclaimer) Disclaimer

This is an unofficial companion tool for Poe.com's API. It is not affiliated with or endorsed by Poe.com or Quora, Inc.
