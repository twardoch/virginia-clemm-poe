# this_file: src/virginia_clemm_poe/__main__.py

"""CLI entry point for Virginia Clemm Poe."""

import asyncio
import os
import shutil
import sys

import fire
from rich.console import Console
from rich.table import Table

from . import api
from .browser_manager import BrowserManager
from .config import DATA_FILE_PATH, DEFAULT_DEBUG_PORT
from .updater import ModelUpdater
from .utils.logger import configure_logger, log_operation, log_user_action

console = Console()


class Cli:
    """Virginia Clemm Poe - Poe.com model data management CLI.
    
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
    """

    def setup(self, verbose: bool = False) -> None:
        """Set up Chrome browser for web scraping - required before first update.
        
        Initialize browser environment for Virginia Clemm Poe web scraping operations.

        This command prepares your system for data collection by ensuring Chrome/Chromium
        is properly installed and configured for web scraping. It uses the PlaywrightAuthor
        package to handle complex browser management automatically.

        The setup process includes:
        1. Detecting existing Chrome/Chromium installations
        2. Installing Chrome for Testing if no suitable browser is found
        3. Configuring Chrome with appropriate flags for automation
        4. Verifying the browser can launch successfully with DevTools Protocol

        This is a one-time setup that prepares your environment for the 'update' command,
        which requires browser automation to scrape pricing and bot information from Poe.com.

        Args:
            verbose: Enable detailed logging to see browser detection, installation steps,
                    and configuration details. Useful for troubleshooting setup failures.

        Raises:
            SystemExit: If browser setup fails completely and cannot be resolved
                       automatically. Manual Chrome installation may be required.

        Examples:
            Basic setup (recommended for most users):
            ```bash
            virginia-clemm-poe setup
            ```

            Troubleshooting setup issues:
            ```bash
            # See detailed setup process
            virginia-clemm-poe setup --verbose
            ```

        What This Command Does:
            - Searches for Chrome/Chromium in standard system locations
            - Downloads Chrome for Testing if no suitable browser found
            - Creates browser profile directory for automation
            - Tests browser launch with DevTools Protocol enabled
            - Displays next steps for getting started

        System Requirements:
            - Operating System: Windows, macOS, or Linux
            - Available disk space: ~200MB for Chrome for Testing
            - Network access: Required for downloading browser if needed
            - Permissions: Write access to user cache directory

        Installation Locations:
            - macOS: ~/Library/Caches/virginia-clemm-poe/
            - Linux: ~/.cache/virginia-clemm-poe/
            - Windows: %LOCALAPPDATA%\\virginia-clemm-poe\\

        Manual Installation (if setup fails):
            - macOS: `brew install --cask google-chrome`
            - Ubuntu/Debian: `sudo apt-get install google-chrome-stable`
            - Windows: Download from https://www.google.com/chrome/
            - Arch Linux: `sudo pacman -S google-chrome`

        Common Issues:
            - Permission errors: Run with appropriate user permissions
            - Network timeouts: Check internet connection and retry
            - Disk space: Ensure adequate space in cache directory
            - Antivirus interference: Temporarily disable real-time scanning

        Success Indicators:
            - "✓ Chrome is available!" message displayed
            - Next steps instructions shown
            - No error messages during browser launch test

        Note:
            This command only needs to be run once per system. If you move your
            cache directory or upgrade your system, you may need to run setup again.
            The browser installation is managed by PlaywrightAuthor for reliability.

        See Also:
            - update(): Use the configured browser to fetch model data
            - status(): Check if browser is still properly configured
            - doctor(): Diagnose and fix browser-related issues
        """
        configure_logger(verbose)

        # Log user action
        log_user_action("setup", command="setup", verbose=verbose)

        console.print("[bold blue]Setting up browser for Virginia Clemm Poe...[/bold blue]")

        async def run_setup() -> None:
            success = await BrowserManager.setup_chrome()
            if success:
                console.print("[green]✓ Chrome is available![/green]")
                console.print("\n[bold]You're all set![/bold]")
                console.print("\nTo get started:")
                console.print("1. Set your Poe API key: [cyan]export POE_API_KEY=your_key[/cyan]")
                console.print("2. Update model data: [cyan]virginia-clemm-poe update[/cyan]")
                console.print("3. Search models: [cyan]virginia-clemm-poe search claude[/cyan]")
            else:
                console.print("[red]✗ Failed to set up Chrome[/red]")
                console.print("\nPlease install Chrome or Chromium manually:")
                console.print("- macOS: brew install --cask google-chrome")
                console.print("- Ubuntu: sudo apt-get install google-chrome-stable")
                console.print("- Windows: Download from https://www.google.com/chrome/")
                sys.exit(1)

        asyncio.run(run_setup())

    def status(self, verbose: bool = False) -> None:
        """Check system health and data freshness - your go-to diagnostic command.
        
        Comprehensive system health check for Virginia Clemm Poe installation.

        This diagnostic command verifies that all components are properly installed and
        configured for successful operation. It's the first command to run when setting
        up a new installation or troubleshooting issues with data updates.

        The status check covers:
        1. **Browser Environment**: Verifies Chrome/Chromium is installed and accessible
        2. **Model Dataset**: Checks if local data file exists and reports last update time
        3. **API Configuration**: Validates POE_API_KEY environment variable (without exposing the key)
        4. **System Dependencies**: Confirms all required Python packages are available

        **When to Use This Command**:
        - After first installation to verify setup is complete
        - Before running update operations to ensure environment is ready
        - When troubleshooting failed update or search operations
        - To check data freshness and determine if updates are needed
        - As part of CI/CD health checks or automated monitoring

        Args:
            verbose: Enable detailed diagnostic output including browser paths, data
                    file details, and dependency versions. Useful for troubleshooting
                    and providing detailed system information for support requests.

        Examples:
            Quick health check (recommended for routine use):
            ```bash
            virginia-clemm-poe status
            ```

            Detailed system diagnosis:
            ```bash
            # Show detailed paths and configuration
            virginia-clemm-poe status --verbose
            ```

        Exit Codes:
            - 0: All systems healthy and ready for operation
            - 1: Issues found that may prevent normal operation

        What This Command Checks:
            - Browser installation status and launch capability
            - Local model dataset existence and freshness (age in days)
            - POE_API_KEY environment variable presence (key value not displayed)
            - Critical Python dependencies and version compatibility
            - File system permissions for data directory access

        **Interpreting Results**:
        - ✓ Green checkmarks indicate components are working properly
        - ✗ Red X marks show issues that need attention before running updates
        - ⚠ Yellow warnings indicate non-critical issues or recommendations

        **Next Steps Based on Results**:
        - If browser not ready: Run `virginia-clemm-poe setup`
        - If API key missing: Set POE_API_KEY environment variable
        - If data outdated: Run `virginia-clemm-poe update` to refresh dataset
        - If issues persist: Run `virginia-clemm-poe doctor` for detailed diagnosis
        """
        configure_logger(verbose)
        console.print("[bold blue]Virginia Clemm Poe Status[/bold blue]\n")

        # Check browser status
        console.print("[bold]Browser Status:[/bold]")
        try:
            from playwrightauthor.browser_manager import ensure_browser

            browser_path, data_dir = ensure_browser(verbose=verbose)
            console.print("[green]✓ Browser is ready[/green]")
            console.print(f"  Path: {browser_path}")
            console.print(f"  User Data: {data_dir}")
        except Exception as e:
            console.print(f"[red]✗ Browser not available: {e}[/red]")
            console.print("  Run 'virginia-clemm-poe setup' to install")

        # Check data status
        console.print("\n[bold]Data Status:[/bold]")
        if DATA_FILE_PATH.exists():
            import json

            with open(DATA_FILE_PATH) as f:
                models_data = json.load(f)

            total_models = len(models_data.get("models", []))
            with_pricing = sum(1 for model in models_data.get("models", []) if model.get("pricing"))
            with_bot_info = sum(1 for model in models_data.get("models", []) if model.get("bot_info"))

            console.print("[green]✓ Model data found[/green]")
            console.print(f"  Path: {DATA_FILE_PATH}")
            console.print(f"  Total models: {total_models}")
            console.print(f"  With pricing: {with_pricing}")
            console.print(f"  With bot info: {with_bot_info}")

            # Check data freshness
            if total_models > 0:
                from datetime import datetime

                models = api.get_all_models()
                latest_pricing = None
                for model in models:
                    if model.pricing and (latest_pricing is None or model.pricing.checked_at > latest_pricing):
                        latest_pricing = model.pricing.checked_at

                if latest_pricing:
                    days_old = (datetime.now(latest_pricing.tzinfo) - latest_pricing).days
                    if days_old > 7:
                        console.print(f"  [yellow]Data is {days_old} days old[/yellow]")
                    else:
                        console.print(f"  [green]Data is {days_old} days old[/green]")
        else:
            console.print("[red]✗ No model data found[/red]")
            console.print("  Run 'virginia-clemm-poe update' to fetch data")

        # Check API key
        console.print("\n[bold]API Key Status:[/bold]")
        if os.environ.get("POE_API_KEY"):
            console.print("[green]✓ POE_API_KEY is set[/green]")
        else:
            console.print("[yellow]⚠ POE_API_KEY not set[/yellow]")
            console.print("  Set with: export POE_API_KEY=your_key")

    def clear_cache(self, data: bool = False, browser: bool = False, all: bool = True, verbose: bool = False) -> None:
        """Clear cache and stored data - use when experiencing stale data issues.
        
        **When to Use This Command**:
        - Model data appears outdated even after update
        - Browser automation stops working correctly
        - Starting fresh after configuration changes
        - Recovering from corrupted data files

        Args:
            data: Clear only model data
            browser: Clear only browser cache (delegates to PlaywrightAuthor)
            all: Clear both data and browser cache (default)
            verbose: Enable verbose logging
        """
        configure_logger(verbose)

        # If user explicitly sets --data or --browser, disable --all
        if data or browser:
            all = False

        clear_data = data or all
        clear_browser = browser or all

        if not clear_data and not clear_browser:
            console.print("[yellow]No cache type selected.[/yellow]")
            console.print("Available options:")
            console.print("  --data     Clear model data")
            console.print("  --browser  Clear browser cache")
            console.print("  --all      Clear both (default)")
            return

        console.print("[bold blue]Clearing cache...[/bold blue]\n")

        # Clear model data
        if clear_data:
            console.print("[bold]Model Data:[/bold]")
            if DATA_FILE_PATH.exists():
                DATA_FILE_PATH.unlink()
                console.print("[green]✓ Model data cleared[/green]")
            else:
                console.print("[yellow]No model data to clear[/yellow]")

        # Clear browser cache (delegate to PlaywrightAuthor)
        if clear_browser:
            console.print("\n[bold]Browser Cache:[/bold]")
            try:
                from playwrightauthor.utils.paths import install_dir

                install_path = install_dir()
                if install_path.exists():
                    console.print(f"Removing {install_path}...")
                    shutil.rmtree(install_path)
                    console.print("[green]✓ Browser cache cleared[/green]")
                else:
                    console.print("[yellow]No browser cache to clear[/yellow]")
            except Exception as e:
                console.print(f"[red]✗ Failed to clear browser cache: {e}[/red]")
                console.print("  Solution: Try running the command again or restart your system")

        console.print("\n[green]Cache cleared successfully![/green]")

    def cache(self, stats: bool = True, clear: bool = False, verbose: bool = False) -> None:
        """Monitor cache performance and hit rates - optimize your API usage.
        
        Manage request cache for improved performance.
        
        Args:
            stats: Show cache statistics (default)
            clear: Clear all cache entries
            verbose: Enable verbose logging
        """
        configure_logger(verbose)
        
        if clear:
            console.print("[bold blue]Clearing all caches...[/bold blue]\n")
            
            # Import here to avoid circular imports
            import asyncio
            from .utils.cache import get_api_cache, get_scraping_cache, get_global_cache
            
            async def clear_all_caches():
                # Clear all cache instances
                caches = {
                    "Global": get_global_cache(),
                    "API": get_api_cache(), 
                    "Scraping": get_scraping_cache(),
                }
                
                for name, cache in caches.items():
                    await cache.clear()
                    console.print(f"[green]✓ Cleared {name} cache[/green]")
            
            asyncio.run(clear_all_caches())
            console.print("\n[green]All caches cleared successfully![/green]")
            return
        
        if stats:
            console.print("[bold blue]Cache Statistics[/bold blue]\n")
            
            # Import here to avoid circular imports
            import asyncio
            from .utils.cache import get_all_cache_stats
            
            async def show_cache_stats():
                stats = await get_all_cache_stats()
                
                if not stats:
                    console.print("[yellow]No cache statistics available[/yellow]")
                    return
                
                for cache_name, cache_stats in stats.items():
                    console.print(f"[bold]{cache_name.title()} Cache:[/bold]")
                    console.print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']} entries")
                    console.print(f"  Hit Rate: {cache_stats['hit_rate_percent']:.1f}%")
                    console.print(f"  Total Requests: {cache_stats['total_requests']}")
                    console.print(f"  Hits: {cache_stats['hits']}")
                    console.print(f"  Misses: {cache_stats['misses']}")
                    console.print(f"  Evictions: {cache_stats['evictions']}")
                    console.print(f"  Expired Cleanups: {cache_stats['expired_removals']}")
                    
                    # Show cache hit rate status
                    hit_rate = cache_stats['hit_rate_percent']
                    if hit_rate >= 80:
                        console.print(f"  Status: [green]Excellent (≥80%)[/green]")
                    elif hit_rate >= 60:
                        console.print(f"  Status: [yellow]Good (≥60%)[/yellow]")
                    else:
                        console.print(f"  Status: [red]Poor (<60%)[/red]")
                    
                    console.print()
                
                # Overall performance summary
                total_requests = sum(s['total_requests'] for s in stats.values())
                total_hits = sum(s['hits'] for s in stats.values())
                overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
                
                console.print("[bold]Overall Performance:[/bold]")
                console.print(f"  Combined Hit Rate: {overall_hit_rate:.1f}%")
                console.print(f"  Target: 80% (for optimal performance)")
                
                if overall_hit_rate >= 80:
                    console.print("  [green]✓ Performance target achieved![/green]")
                else:
                    console.print(f"  [yellow]Performance could be improved[/yellow]")
                    console.print(f"  Suggestion: Consider longer cache TTL values")
            
            asyncio.run(show_cache_stats())

    def _check_python_version(self) -> int:
        """Check if Python version meets requirements.
        
        Returns:
            Number of issues found (0 or 1)
        """
        console.print("[bold]Python Version:[/bold]")
        import sys

        version = sys.version_info
        if version >= (3, 12):
            console.print(f"[green]✓ Python {version.major}.{version.minor}.{version.micro}[/green]")
            return 0
        else:
            console.print(f"[red]✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.12+)[/red]")
            console.print("  Solution: Install Python 3.12 or later")
            return 1
    
    def _check_api_key(self) -> int:
        """Check API key presence and validity.
        
        Returns:
            Number of issues found (0 or 1)
        """
        console.print("\n[bold]API Key:[/bold]")
        if not os.environ.get("POE_API_KEY"):
            console.print("[red]✗ POE_API_KEY not set[/red]")
            console.print("  Solution: export POE_API_KEY=your_api_key")
            return 1
            
        console.print("[green]✓ POE_API_KEY is set[/green]")
        
        # Test API key validity
        api_key = os.environ.get("POE_API_KEY")
        import httpx
        from .config import API_TIMEOUT_SECONDS

        try:
            response = httpx.get(
                "https://api.poe.com/v2/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=API_TIMEOUT_SECONDS,
            )
            if response.status_code == 200:
                console.print("[green]✓ API key is valid[/green]")
                return 0
            else:
                console.print(f"[red]✗ API key might be invalid (status: {response.status_code})[/red]")
                console.print("  Solution: Check your API key at https://poe.com/api")
                return 1
        except Exception as e:
            console.print(f"[yellow]⚠ Could not validate API key: {e}[/yellow]")
            return 0
    
    def _check_browser(self) -> int:
        """Check browser availability and configuration.
        
        Returns:
            Number of issues found
        """
        console.print("\n[bold]Browser:[/bold]")
        issues = 0
        
        try:
            from playwrightauthor.browser_manager import ensure_browser

            browser_path, data_dir = ensure_browser(verbose=False)
            console.print("[green]✓ Browser is available[/green]")

            # Check if browser is accessible
            if os.path.exists(browser_path):
                console.print(f"[green]✓ Browser executable exists at {browser_path}[/green]")
            else:
                console.print(f"[red]✗ Browser executable not found at {browser_path}[/red]")
                console.print("  Solution: Run 'virginia-clemm-poe setup'")
                issues += 1
        except Exception as e:
            console.print(f"[red]✗ Browser not available: {e}[/red]")
            console.print("  Solution: Run 'virginia-clemm-poe setup'")
            issues += 1
            
        return issues
    
    def _check_network(self) -> int:
        """Check network connectivity to poe.com.
        
        Returns:
            Number of issues found (0 or 1)
        """
        console.print("\n[bold]Network:[/bold]")
        import httpx
        from .config import NETWORK_TIMEOUT_SECONDS

        try:
            response = httpx.get("https://poe.com", timeout=NETWORK_TIMEOUT_SECONDS)
            if response.status_code == 200:
                console.print("[green]✓ Can reach poe.com[/green]")
                return 0
            else:
                console.print(f"[yellow]⚠ Unexpected status from poe.com: {response.status_code}[/yellow]")
                return 0
        except Exception as e:
            console.print(f"[red]✗ Cannot reach poe.com: {e}[/red]")
            console.print("  Solution: Check your internet connection")
            return 1
    
    def _check_dependencies(self) -> int:
        """Check if all required packages are installed.
        
        Returns:
            Number of issues found
        """
        console.print("\n[bold]Dependencies:[/bold]")
        required_packages = ["httpx", "playwright", "pydantic", "fire", "rich", "loguru", "beautifulsoup4"]
        import importlib
        import importlib.util
        
        issues = 0
        
        for package in required_packages:
            try:
                importlib.import_module(package)
                console.print(f"[green]✓ {package}[/green]")
            except ImportError:
                console.print(f"[red]✗ {package} not installed[/red]")
                console.print(f"  Solution: pip install {package}")
                issues += 1

        # Check PlaywrightAuthor
        if importlib.util.find_spec("playwrightauthor") is not None:
            console.print("[green]✓ playwrightauthor[/green]")
        else:
            console.print("[red]✗ playwrightauthor not installed[/red]")
            console.print("  Solution: Check pyproject.toml dependencies")
            issues += 1
            
        return issues
    
    def _check_data_file(self) -> int:
        """Check data file existence and validity.
        
        Returns:
            Number of issues found
        """
        console.print("\n[bold]Data File:[/bold]")
        if not DATA_FILE_PATH.exists():
            console.print("[yellow]⚠ No model data found[/yellow]")
            console.print("  Solution: Run 'virginia-clemm-poe update'")
            return 0
            
        size = DATA_FILE_PATH.stat().st_size
        console.print(f"[green]✓ Model data exists ({size:,} bytes)[/green]")

        # Check if data is valid JSON
        try:
            import json
            with open(DATA_FILE_PATH) as f:
                models_data = json.load(f)
            console.print(f"[green]✓ Valid JSON with {len(models_data.get('models', []))} models[/green]")
            return 0
        except Exception as e:
            console.print(f"[red]✗ Invalid JSON: {e}[/red]")
            console.print("  Solution: Run 'virginia-clemm-poe update --force'")
            return 1
    
    def _display_summary(self, issues_found: int) -> None:
        """Display summary of diagnostic results.
        
        Args:
            issues_found: Total number of issues found
        """
        console.print("\n" + "=" * 50)
        if issues_found == 0:
            console.print("[green]✓ All checks passed! Virginia Clemm Poe is ready to use.[/green]")
        else:
            console.print(f"[red]Found {issues_found} issue(s). Please fix them and try again.[/red]")
            console.print("\nQuick setup commands:")
            console.print("  1. export POE_API_KEY=your_api_key")
            console.print("  2. virginia-clemm-poe setup")
            console.print("  3. virginia-clemm-poe update")

    def doctor(self, verbose: bool = False) -> None:
        """Diagnose and fix common issues - run this when something goes wrong.
        
        **When to Use This Command**:
        - Update command fails with errors
        - Search returns no results when it should
        - After system updates or configuration changes  
        - Before reporting bugs or seeking support"""
        configure_logger(verbose)
        console.print("[bold blue]Virginia Clemm Poe Doctor[/bold blue]\n")

        # Run all diagnostic checks
        issues_found = 0
        issues_found += self._check_python_version()
        issues_found += self._check_api_key()
        issues_found += self._check_browser()
        issues_found += self._check_network()
        issues_found += self._check_dependencies()
        issues_found += self._check_data_file()
        
        # Display summary
        self._display_summary(issues_found)

    def _validate_api_key(self, api_key: str | None) -> str:
        """Validate and return API key.
        
        Args:
            api_key: Optional API key override
            
        Returns:
            Valid API key
            
        Raises:
            SystemExit: If no API key is available
        """
        api_key = api_key or os.environ.get("POE_API_KEY")
        if not api_key:
            console.print("[red]✗ POE_API_KEY not set[/red]")
            console.print("  Solution: export POE_API_KEY=your_api_key")
            console.print("  Or pass it as: virginia-clemm-poe update --api_key your_api_key")
            sys.exit(1)
        return api_key
    
    def _determine_update_mode(self, info: bool, pricing: bool, all: bool) -> tuple[bool, bool]:
        """Determine what data to update based on flags.
        
        Args:
            info: Update bot info flag
            pricing: Update pricing flag
            all: Update all flag
            
        Returns:
            Tuple of (update_info, update_pricing)
        """
        # If user explicitly sets --info or --pricing, disable --all
        if info or pricing:
            all = False

        update_info = info or all
        update_pricing = pricing or all

        if not update_info and not update_pricing:
            console.print("[yellow]No update mode selected.[/yellow]")
            console.print("Available options:")
            console.print("  --info     Update bot info (creator, description)")
            console.print("  --pricing  Update pricing information")
            console.print("  --all      Update both (default)")
            
        return update_info, update_pricing
    
    def _display_update_status(self, all: bool, update_info: bool, update_pricing: bool) -> None:
        """Display what will be updated.
        
        Args:
            all: True if updating all data
            update_info: True if updating bot info
            update_pricing: True if updating pricing
        """
        if all:
            console.print("[green]Updating all data (bot info + pricing)...[/green]")
        else:
            updates = []
            if update_info:
                updates.append("bot info")
            if update_pricing:
                updates.append("pricing")
            console.print(f"[green]Updating {' and '.join(updates)}...[/green]")

    def update(
        self,
        info: bool = False,
        pricing: bool = False,
        all: bool = True,
        api_key: str | None = None,
        force: bool = False,
        debug_port: int = DEFAULT_DEBUG_PORT,
        verbose: bool = False,
    ) -> None:
        """Fetch latest model data from Poe - run weekly or when new models appear.
        
        Update Poe model data with pricing and bot information from web scraping.

        This is the primary command for refreshing your local model dataset. It fetches
        the complete model list from Poe's API, then uses browser automation to scrape
        detailed pricing information and bot metadata that isn't available through the API.

        The update process involves:
        1. Fetching all models from Poe API (requires valid API key)
        2. Launching Chrome browser for web scraping via PlaywrightAuthor
        3. Visiting each model's page to extract pricing tables and bot info cards
        4. Saving the enriched dataset to local JSON file for fast API access

        Args:
            info: Update only bot information (creator handles, descriptions, disclaimers).
                 Skips pricing scraping for faster updates when only metadata is needed.
            pricing: Update only pricing information (costs, points, rate structures).
                    Skips bot info scraping when only pricing data is required.
            all: Update both pricing and bot info (default: True). This is the recommended
                 mode for complete data freshness. Automatically disabled if --info or
                 --pricing flags are used.
            api_key: Poe API key for authentication. Overrides POE_API_KEY environment
                    variable if provided. Get your key from: https://poe.com/api_key
            force: Force update all models even if they already have data. Without this,
                  only models missing data or with previous errors are updated.
            debug_port: Chrome DevTools Protocol port (default: DEFAULT_DEBUG_PORT). Change if port
                       conflicts occur with other browser automation tools.
            verbose: Enable detailed logging for troubleshooting browser automation,
                    API calls, and data processing. Useful for debugging update failures.

        Raises:
            SystemExit: If API key is missing or invalid, or if browser setup fails.
                       Check error messages for specific resolution steps.

        Examples:
            Basic usage (updates everything):
            ```bash
            # Set API key and update all data
            export POE_API_KEY=your_key_here
            virginia-clemm-poe update
            ```

            Selective updates:
            ```bash
            # Update only pricing information
            virginia-clemm-poe update --pricing

            # Update only bot info (faster)
            virginia-clemm-poe update --info

            # Force refresh all data
            virginia-clemm-poe update --force
            ```

            Troubleshooting:
            ```bash
            # Enable verbose logging for debugging
            virginia-clemm-poe update --verbose

            # Use custom API key
            virginia-clemm-poe update --api_key your_key

            # Use different debug port if conflicts occur
            virginia-clemm-poe update --debug_port 9223
            ```

        Common Issues:
            - "POE_API_KEY not set": Export your API key or use --api_key flag
            - "Browser setup failed": Run 'virginia-clemm-poe setup' first
            - "Timeout errors": Use --verbose to see which models are failing
            - "Port conflicts": Try different --debug_port value

        Note:
            This command requires Chrome/Chromium for web scraping. Run 'setup' command
            first if you haven't already. The update process can take several minutes
            for the full dataset (240+ models). Use selective flags for faster updates.

        See Also:
            - setup(): Initial browser configuration
            - status(): Check data freshness and system health
            - search(): Query the updated model data
        """
        configure_logger(verbose)

        # Log user action with context
        log_user_action(
            "update",
            command=f"update --info={info} --pricing={pricing} --all={all} --force={force}",
            info=info,
            pricing=pricing,
            all=all,
            force=force,
            verbose=verbose,
        )

        # Validate API key
        api_key = self._validate_api_key(api_key)

        # Determine update mode
        update_info, update_pricing = self._determine_update_mode(info, pricing, all)
        if not update_info and not update_pricing:
            return

        # Display update status
        self._display_update_status(all, update_info, update_pricing)

        # Run update
        async def run_update() -> None:
            updater = ModelUpdater(api_key, debug_port=debug_port, verbose=verbose)
            await updater.update_all(force=force, update_info=update_info, update_pricing=update_pricing)

        asyncio.run(run_update())

    def _validate_data_exists(self) -> bool:
        """Check if model data file exists.
        
        Returns:
            True if data exists, False otherwise
        """
        if not DATA_FILE_PATH.exists():
            console.print("[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]")
            return False
        return True
    
    def _perform_search(self, query: str) -> list:
        """Search for models matching the query.
        
        Args:
            query: Search term
            
        Returns:
            List of matching models
        """
        with log_operation("model_search", {"query": query}) as ctx:
            models = api.search_models(query)
            ctx["results_count"] = len(models)
        
        if not models:
            console.print(f"[yellow]No models found matching '{query}'[/yellow]")
        
        return models
    
    def _create_results_table(self, query: str, show_pricing: bool, show_bot_info: bool) -> Table:
        """Create a formatted table for search results.
        
        Args:
            query: Search query for title
            show_pricing: Whether to include pricing columns
            show_bot_info: Whether to include bot info columns
            
        Returns:
            Configured Table object
        """
        table = Table(title=f"Models matching '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Created", style="green")
        table.add_column("Input", style="blue")
        table.add_column("Output", style="blue")

        if show_bot_info:
            table.add_column("Creator", style="magenta")

        if show_pricing:
            table.add_column("Pricing", style="yellow")
            table.add_column("Updated", style="dim")
            
        return table
    
    def _format_pricing_info(self, model) -> tuple[str, str]:
        """Format pricing information for display.
        
        Args:
            model: Model object with pricing data
            
        Returns:
            Tuple of (pricing_info, updated_date)
        """
        if model.pricing:
            primary_cost = model.get_primary_cost()
            pricing_info = primary_cost if primary_cost else "[dim]No cost info[/dim]"

            # Include initial points cost if available
            if model.pricing.details.initial_points_cost:
                pricing_info = f"{model.pricing.details.initial_points_cost} | {pricing_info}"

            updated = model.pricing.checked_at.strftime("%Y-%m-%d")
            return pricing_info, updated
        elif model.pricing_error:
            return f"[red]Error: {model.pricing_error}[/red]", "-"
        else:
            return "[dim]Not checked[/dim]", "-"
    
    def _add_model_row(self, table: Table, model, show_pricing: bool, show_bot_info: bool) -> None:
        """Add a single model row to the table.
        
        Args:
            table: Table to add row to
            model: Model data
            show_pricing: Whether to include pricing columns
            show_bot_info: Whether to include bot info columns
        """
        row = [
            model.id,
            model.created,
            ", ".join(model.architecture.input_modalities),
            ", ".join(model.architecture.output_modalities),
        ]

        if show_bot_info:
            creator = model.bot_info.creator if model.bot_info else "[dim]-[/dim]"
            row.append(creator)

        if show_pricing:
            pricing_info, updated = self._format_pricing_info(model)
            row.extend([pricing_info, updated])

        table.add_row(*[str(x) for x in row])
    
    def _display_single_model_bot_info(self, model) -> None:
        """Display detailed bot info for a single model result.
        
        Args:
            model: Model with bot info to display
        """
        if model.bot_info:
            bot_info = model.bot_info
            console.print("\n[bold]Bot Information:[/bold]")
            if bot_info.description:
                console.print(f"[blue]Description:[/blue] {bot_info.description}")
            if bot_info.description_extra:
                console.print(f"[dim]Details:[/dim] {bot_info.description_extra}")

    def search(self, query: str, show_pricing: bool = True, show_bot_info: bool = False, verbose: bool = False) -> None:
        """Find models by name or ID - your primary command for discovering models.
        
        Search and display Poe models by ID or name with flexible filtering.

        This command provides an intuitive way to find specific models in the local dataset
        using case-insensitive substring matching. It searches both model IDs and root names,
        making it easy to discover models even with partial information.

        The search uses fuzzy matching to help users find what they're looking for:
        - "claude" finds "Claude-3-Opus", "Claude-3.5-Sonnet", etc.
        - "gpt" finds "GPT-4", "GPT-4-Turbo", "ChatGPT", etc.
        - "son" finds "Claude-3.5-Sonnet", "Sonnet-3.5", etc.

        Results are displayed in a formatted table with model information, pricing data,
        and optional bot metadata for easy comparison and selection.

        Args:
            query: Search term to match against model IDs and names. Case-insensitive
                  substring matching is used, so partial matches work well.
            show_pricing: Display pricing information in results table (default: True).
                         Shows the primary cost metric for each model if available.
                         Disable to focus on model capabilities without cost data.
            show_bot_info: Include bot creator and description columns (default: False).
                          Shows "@creator" handles and bot descriptions when enabled.
                          Useful for understanding model origins and purposes.
            verbose: Enable detailed logging for search operations and data loading.
                    Helpful for debugging data file issues or search performance.

        Returns:
            None: Results are displayed directly to console in formatted table.

        Examples:
            Basic model search:
            ```bash
            # Find all Claude models
            virginia-clemm-poe search claude

            # Find GPT models
            virginia-clemm-poe search gpt

            # Search for specific model
            virginia-clemm-poe search "Claude-3-Opus"
            ```

            Customized output:
            ```bash
            # Show models with bot creator info
            virginia-clemm-poe search claude --show_bot_info

            # Search without pricing (faster display)
            virginia-clemm-poe search gpt --no-show_pricing

            # Verbose search for troubleshooting
            virginia-clemm-poe search claude --verbose
            ```

            Search patterns:
            ```bash
            # Partial matches work great
            virginia-clemm-poe search "son"     # Finds Sonnet models
            virginia-clemm-poe search "turbo"   # Finds Turbo variants
            virginia-clemm-poe search "vision"  # Finds vision-capable models
            ```

        Output Format:
            Results table includes:
            - ID: Model identifier (e.g., "Claude-3-Opus")
            - Created: Model creation timestamp
            - Input: Supported input modalities (text, image, etc.)
            - Output: Supported output modalities (text, image, etc.)
            - Cost: Primary pricing metric (if show_pricing=True)
            - Creator: Bot creator handle (if show_bot_info=True)
            - Description: Bot description (if show_bot_info=True)

        Common Issues:
            - "No model data found": Run 'virginia-clemm-poe update' to fetch data
            - "No models found": Try broader search terms or check spelling
            - Empty pricing columns: Update with --pricing flag to get cost data

        Performance Notes:
            - Search is performed on locally cached data for fast response
            - Large result sets may take longer to format and display
            - Bot info display adds extra columns that may wrap on narrow terminals

        Note:
            This command requires existing model data. If you see "No model data found",
            run the 'update' command first to populate your local dataset.

        See Also:
            - update(): Refresh model data from Poe.com
            - list(): Show all models with filtering options
            - status(): Check if model data is current
        """
        configure_logger(verbose)

        # Log user action
        log_user_action(
            "search",
            command=f"search '{query}' --show_pricing={show_pricing} --show_bot_info={show_bot_info}",
            query=query,
            show_pricing=show_pricing,
            show_bot_info=show_bot_info,
            verbose=verbose,
        )

        # Validate data exists
        if not self._validate_data_exists():
            return

        # Perform search
        models = self._perform_search(query)
        if not models:
            return

        # Create and populate results table
        table = self._create_results_table(query, show_pricing, show_bot_info)
        
        for model in models:
            self._add_model_row(table, model, show_pricing, show_bot_info)

        # Display results
        console.print(table)
        console.print(f"\n[green]Found {len(models)} models[/green]")

        # Show detailed bot info for single results
        if show_bot_info and len(models) == 1:
            self._display_single_model_bot_info(models[0])

    def list(self, with_pricing: bool = False, limit: int | None = None, verbose: bool = False) -> None:
        """List all available models - get an overview of the entire dataset.
        
        **When to Use This Command**:
        - Viewing summary statistics about model coverage
        - Checking how many models have pricing data
        - Getting a quick count of available models
        - Identifying models that need updating

        Args:
            with_pricing: Only show models with pricing information
            limit: Limit number of results
            verbose: Enable verbose logging
        """
        configure_logger(verbose)

        if not DATA_FILE_PATH.exists():
            console.print("[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]")
            return

        models = api.get_models_with_pricing() if with_pricing else api.get_all_models()

        if limit:
            models = models[:limit]

        # Create summary table
        table = Table(title="Poe Models Summary")
        table.add_column("Total Models", style="cyan")
        table.add_column("With Pricing", style="green")
        table.add_column("Need Update", style="yellow")

        all_models = api.get_all_models()
        count_with_pricing = len([m for m in all_models if m.has_pricing()])
        need_update = len([m for m in all_models if m.needs_pricing_update()])

        table.add_row(str(len(all_models)), str(count_with_pricing), str(need_update))
        console.print(table)

        if models:
            console.print(f"\n[bold]Showing {len(models)} models:[/bold]")
            for model in models:
                status = "✓" if model.has_pricing() else "✗"
                console.print(f"{status} {model.id}")


def main() -> None:
    """Main CLI entry point."""
    fire.Fire(Cli)


if __name__ == "__main__":
    main()
