# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Architecture Modernization**: Comprehensive refactoring following PlaywrightAuthor patterns
- **Exception Hierarchy**: Full exception system in `exceptions.py` with:
  - Base `VirginiaPoeError` class for all package exceptions
  - Browser-specific exceptions: `BrowserManagerError`, `ChromeNotFoundError`, `ChromeLaunchError`, `CDPConnectionError`
  - Data-specific exceptions: `ModelDataError`, `ModelNotFoundError`, `DataUpdateError`
  - API-specific exceptions: `APIError`, `AuthenticationError`, `RateLimitError`
  - Network and scraping exceptions: `NetworkError`, `ScrapingError`
- **Utilities Module**: New `utils/` package with modular components:
  - `utils/logger.py` - Centralized loguru configuration
  - `utils/paths.py` - Cross-platform path management utilities
- **File Navigation**: `this_file:` comments in all source files showing relative paths
- **CLI Commands**: Three new diagnostic and maintenance commands:
  - `status` - Comprehensive system health checks (browser installation, data freshness, API key validation)
  - `clear-cache` - Selective cache clearing with granular options (data, browser, or both)
  - `doctor` - Advanced diagnostics with issue detection and actionable solution suggestions
- **Enhanced Logging**: Verbose flag support across all CLI commands with consistent logger configuration
- **Rich UI**: Color-coded console output with formatting for enhanced user experience

### Changed
- **BREAKING**: Replaced entire internal browser management system with external PlaywrightAuthor package
  - Removed ~500+ lines of browser-related code
  - Simplified architecture by delegating complex browser operations to proven external package
  - Maintained API compatibility while dramatically reducing maintenance burden
- **BREAKING**: CLI class renamed from `CLI` to `Cli` following PlaywrightAuthor naming conventions
- **Browser Management**: Complete rewrite of browser orchestration:
  - `browser_manager.py` now uses PlaywrightAuthor's `ensure_browser()` for setup
  - Direct Playwright CDP connection for actual browser operations
  - Async context manager support for resource cleanup
  - Robust error handling with specific exception types
- **CLI Architecture**: Modernized command-line interface:
  - Centralized logger configuration with verbose mode support
  - All commands now use `console.print()` for consistent rich formatting
  - Enhanced error messages with actionable solutions and recovery guidance
  - Improved user onboarding with clearer setup instructions
- **Error Handling**: Comprehensive upgrade across entire codebase:
  - Custom exception types for specific error scenarios
  - Better error messages with context and suggested solutions
  - Graceful degradation for non-critical failures

### Removed
- **Internal Browser System**: Eliminated entire `browser/` module hierarchy:
  - `browser/finder.py` - Chrome executable detection (now in PlaywrightAuthor)
  - `browser/installer.py` - Chrome for Testing installation (now in PlaywrightAuthor)
  - `browser/launcher.py` - Chrome process launching (now in PlaywrightAuthor)
  - `browser/process.py` - Process management utilities (now in PlaywrightAuthor)
- **Legacy Browser Interface**: Removed `browser.py` compatibility module
- **Dependencies**: No longer directly depends on `psutil` and `platformdirs` (provided by PlaywrightAuthor)

### Technical Improvements
- **Codebase Reduction**: Eliminated ~500+ lines while maintaining full functionality
- **Dependency Simplification**: Reduced direct dependencies by leveraging PlaywrightAuthor's mature browser management
- **Architecture Clarity**: Cleaner separation of concerns with focused modules
- **Maintenance Reduction**: Browser management complexity delegated to external, well-maintained package

### From Previous Release
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