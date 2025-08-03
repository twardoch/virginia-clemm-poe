# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Enhanced bot information capture from Poe.com bot info cards
- New bot_info field in PoeModel with creator, description, and description_extra
- Initial points cost information in pricing model
- Improved scraper with view more button handling
- Robust CSS selector fallbacks for future-proofing
- Comprehensive test suite
- Additional documentation (CONTRIBUTING.md, API.md, CLI.md, DEVELOPMENT.md)
- Development tooling (ruff, mypy, pre-commit hooks)
- GitHub Actions CI/CD workflows

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