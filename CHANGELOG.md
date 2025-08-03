# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced bot information capture from Poe.com bot info cards
- New `bot_info` field in PoeModel with BotInfo model containing:
  - `creator`: Bot creator handle (e.g., "@openai")
  - `description`: Main bot description text
  - `description_extra`: Additional disclaimer text (e.g., "Powered by...")
- `initial_points_cost` field in PricingDetails model for upfront point costs
- Improved web scraper with automatic "View more" button clicking for expanded descriptions
- Robust CSS selector fallbacks for all bot info extraction (future-proofing against class name changes)
- CLI enhancement: `--show_bot_info` flag for search command to display bot creators and descriptions
- CLI enhancement: `--info` flag for update command to update only bot information
- Display initial points cost alongside regular pricing in CLI output
- Comprehensive test suite for bot info extraction functionality
- Test results documentation in TEST_RESULTS.md

### Changed
- **BREAKING**: CLI `update` command now defaults to `--all` (updates both bot info and pricing)
- **BREAKING**: Previous `--pricing` flag now only updates pricing (use `--all` or no flags for full update)
- **BREAKING**: New `--info` flag updates only bot information
- Renamed `scrape_model_pricing()` to `scrape_model_info()` to reflect expanded functionality
- Bot info data is now preserved when syncing models (similar to pricing data)
- Type annotations updated to Python 3.12+ style (using `|` union syntax)
- Import optimizations and code formatting improvements via ruff
- `update_all()` and `sync_models()` methods now accept `update_info` and `update_pricing` parameters
- Updated README.md with new CLI examples and BotInfo model documentation
- Updated all documentation to reflect new bot info feature

## [0.1.0] - 2025-08-03

### Added
- Initial release of Virginia Clemm Poe
- Python API for querying Poe.com model data
- CLI interface for updating and searching models
- Comprehensive Pydantic data models for type safety
- Web scraping functionality for pricing information
- Browser automation setup command
- Flexible pricing structure support for various model types
- Model search capabilities by ID and name
- Caching mechanism for improved performance
- Rich terminal output for better user experience
- Comprehensive README with examples and documentation

### Technical Details
- Built with Python 3.12+ support
- Uses httpx for API requests
- Uses playwright for web scraping
- Uses pydantic for data validation
- Uses fire for CLI framework
- Uses rich for terminal formatting
- Uses loguru for logging
- Automatic versioning with hatch-vcs

### Data
- Includes initial dataset of 240 Poe.com models
- Pricing data for 238 models (98% coverage)
- Support for various pricing structures (standard, total cost, image/video output, etc.)

[0.1.0]: https://github.com/twardoch/virginia-clemm-poe/releases/tag/v0.1.0