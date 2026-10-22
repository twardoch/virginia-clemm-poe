---
this_file: README.md
---

# Virginia Clemm Poe

[![PyPI version](https://badge.fury.io/py/virginia-clemm-poe.svg)](https://badge.fury.io/py/virginia-clemm-poe) [![Python Support](https://img.shields.io/pypi/pyversions/virginia-clemm-poe.svg)](https://pypi.org/project/virginia-clemm-poe/) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python package for accessing Poe.com model data and pricing information.

## Overview

Virginia Clemm Poe fetches and maintains Poe.com model data including pricing. It provides both a Python API for querying model data and a CLI for updating the dataset.

This link points to a static copy of the data file updated by the CLI tool. It does not reflect real-time changes from Poe's API.

## Features

- **Model Data Access**: Query Poe.com models by ID, name, or other attributes
- **Vendor Discovery**: Include bots from 28 curated Poe vendor profiles, alongside the API catalog
- **Bot Information**: Retrieve bot creator, description, and metadata
- **Pricing Information**: Scrape and sync pricing data for all models
- **Pydantic Models**: Typed data models for easy integration
- **CLI Interface**: Fire-based command line tool for data management
- **Browser Automation**: PlaywrightAuthor with Chrome for Testing
- **Session Reuse**: Reuse authenticated browser sessions across runs

Vendor handles are packaged in `src/virginia_clemm_poe/data/good_vendors.txt`.
Every update scrolls each vendor's Created list and scrapes discovered bots through
the normal info/pricing flow. `vendor_profile` records where a bot was discovered.
API metadata wins for matching bots; website-only bots have no API pricing or API
update timestamp, a null creation time, and empty modalities until known. Failed
or incomplete profiles retain existing bots and report a warning. Forced updates
also retain this recovery data. Website rates do not prove API availability or cost.
See [issue 330 verification](issues/330-verification.md) for dated live evidence.

The [interactive catalogue](https://code.twardoch.com/virginia-clemm-poe/models/index.html)
opens cheapest first. Website prices are parsed from every rendered table, raw
Markdown rate cards, and explicit prose rates. Numeric records retain both
currencies, units, ranges, and sources; failed refreshes retain dated observations.
Comparison prefers disclosed points per message/image; otherwise it uses 1,000
total tokens (500 input + 500 output), 4,000 characters, one 1024×1024 image or
10 seconds of video. Dollar-only costs use a labelled estimate from matched
points/dollar observations. Every bot has a tier from 0 (explicitly free in both
currencies) to 9 (unknown). Filter by output Modality, Creator and Tier.
Model pages retain original rates and show the estimate and assumptions.
See the [pricing method](src_docs/md/pricing-method.md).

Documentation uses MaterialX with the shared [FontLab theme 2026](https://i.fontlab.com/fltheme26/)
assets and native navigation/search, without FontLab's global menu or footer.
To rebuild without rescraping: `uv sync --locked`, then
`uv run python src_docs/update_docs.py` (Node 22+ is also required).
Generated site JSON adds `point_estimate`, `pricing_tier`, and conversion metadata;
the packaged source observations remain unchanged.

## Installation

```bash
pip install virginia-clemm-poe
```

## Quick Start

### Python API

```python
from virginia_clemm_poe import api

# Search for models
models = api.search_bots("claude")
for model in models:
    print(f"{model.id}: {model.get_primary_cost()}")

# Get model by ID
model = api.get_bot_by_id("claude-3-opus")
if model and model.pricing:
    print(f"Cost: {model.get_primary_cost()}")
    if model.pricing.scraped:
        print(f"Updated: {model.pricing.scraped.checked_at}")

# Get all models with pricing
priced_models = api.get_bots_with_pricing()
print(f"Found {len(priced_models)} models with pricing")
```

#### Browser identity and unattended commands

Commands default to Chrome for Testing, profile `poe-primary`, mode `auto`.
Auto runs headlessly and raises `AUTH_REQUIRED` (exit 3) when a fresh Poe settings
probe cannot verify authorization. Only explicit `login` / `balance --login` opens
an interactive browser; it leaves OAuth redirects, popups and MFA to you.

```bash
virginia-clemm-poe login --browser-engine=chrome --browser-profile=poe-primary
virginia-clemm-poe balance --browser-engine=chrome --browser-profile=poe-primary
virginia-clemm-poe update --browser-mode=auto
```

Use `--browser-engine=chromium` or `firefox` for installed Playwright browsers;
profiles are separate per engine. `VCP_BROWSER_ENGINE`, `VCP_BROWSER_PROFILE`,
`VCP_BROWSER_MODE`, and `VCP_BROWSER_EXECUTABLE_PATH` provide defaults, overridden
by command flags. `--browser-executable=PATH` selects an installed CfT binary.
A session-capable PlaywrightAuthor is required; older installations return
`ENGINE_UNAVAILABLE` instead of opening a fallback window. Local development can
install the paired checkout with `uv pip install -e ../playwrightauthor`.

Browser pools share one authorized context and create one tab per task. HTTP
cookie exports and balance caches are separate, private and scoped to the same
engine/profile. Exports are never injected into another browser identity.
`logout` clears that HTTP export/cache; persistent browser sign-in is retained.
Existing browser profiles and legacy unscoped exports are not migrated.
See [issue 340 verification](issues/340-poe-verification.md) for tested scope.

### Command Line Interface

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

# Force update all data
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

Use `virginia-clemm-poe COMMAND --help` for current command options.


## Data and API reference

The packaged dataset is `src/virginia_clemm_poe/data/poe_bots.json`.
`api.get_all_bots()`, `api.get_bot_by_id()`, `api.search_bots()`, and
`api.get_bots_with_pricing()` include API and vendor-discovered entries after an
update. Call `api.reload_bots()` to reload persisted changes.

`PoeBot.pricing.api` holds USD API rates; `PoeBot.pricing.scraped` holds website
rates and their check timestamp. These are separate evidence sources.
For full usage and data-model documentation, see [docs](docs/) and
[the documentation source](src_docs/md/).

## Development

```bash
uv sync
./test.sh
uv build
```

`test.sh` runs all regression tests and checks discovery coverage separately.
`uvx hatch test` also applies the configured repository-wide 85% coverage gate;
that broader target currently exceeds measured coverage. See [WORK.md](WORK.md)
for exact results and [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance.

## Author and licence

Adam Twardoch. Licensed under [Apache 2.0](LICENSE).
