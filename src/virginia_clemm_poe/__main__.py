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
from .config import DATA_FILE_PATH
from .updater import ModelUpdater
from .utils.logger import configure_logger, log_user_action, log_operation

console = Console()


class Cli:
    """Virginia Clemm Poe - Poe.com model data management CLI."""

    def setup(self, verbose: bool = False):
        """Initialize browser environment for Virginia Clemm Poe web scraping operations.

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

        async def run_setup():
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

    def status(self, verbose: bool = False):
        """Check browser and data status."""
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
                data = json.load(f)

            total_models = len(data.get("models", []))
            with_pricing = sum(1 for m in data.get("models", []) if m.get("pricing"))
            with_bot_info = sum(1 for m in data.get("models", []) if m.get("bot_info"))

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

    def clear_cache(self, data: bool = False, browser: bool = False, all: bool = True, verbose: bool = False):
        """Clear cache and stored data.

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
                console.print(f"[red]Error clearing browser cache: {e}[/red]")

        console.print("\n[green]Cache cleared successfully![/green]")

    def doctor(self, verbose: bool = False):
        """Diagnose common issues and provide solutions."""
        configure_logger(verbose)
        console.print("[bold blue]Virginia Clemm Poe Doctor[/bold blue]\n")

        issues_found = 0

        # Check Python version
        console.print("[bold]Python Version:[/bold]")
        import sys

        version = sys.version_info
        if version >= (3, 12):
            console.print(f"[green]✓ Python {version.major}.{version.minor}.{version.micro}[/green]")
        else:
            console.print(f"[red]✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.12+)[/red]")
            console.print("  Solution: Install Python 3.12 or later")
            issues_found += 1

        # Check API key
        console.print("\n[bold]API Key:[/bold]")
        if os.environ.get("POE_API_KEY"):
            console.print("[green]✓ POE_API_KEY is set[/green]")
            # Test API key validity
            api_key = os.environ.get("POE_API_KEY")
            import httpx

            try:
                response = httpx.get(
                    "https://api.poe.com/v2/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=5.0
                )
                if response.status_code == 200:
                    console.print("[green]✓ API key is valid[/green]")
                else:
                    console.print(f"[red]✗ API key might be invalid (status: {response.status_code})[/red]")
                    console.print("  Solution: Check your API key at https://poe.com/api")
                    issues_found += 1
            except Exception as e:
                console.print(f"[yellow]⚠ Could not validate API key: {e}[/yellow]")
        else:
            console.print("[red]✗ POE_API_KEY not set[/red]")
            console.print("  Solution: export POE_API_KEY=your_api_key")
            issues_found += 1

        # Check browser availability
        console.print("\n[bold]Browser:[/bold]")
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
                issues_found += 1
        except Exception as e:
            console.print(f"[red]✗ Browser not available: {e}[/red]")
            console.print("  Solution: Run 'virginia-clemm-poe setup'")
            issues_found += 1

        # Check network connectivity
        console.print("\n[bold]Network:[/bold]")
        import httpx

        try:
            response = httpx.get("https://poe.com", timeout=5.0)
            if response.status_code == 200:
                console.print("[green]✓ Can reach poe.com[/green]")
            else:
                console.print(f"[yellow]⚠ Unexpected status from poe.com: {response.status_code}[/yellow]")
        except Exception as e:
            console.print(f"[red]✗ Cannot reach poe.com: {e}[/red]")
            console.print("  Solution: Check your internet connection")
            issues_found += 1

        # Check dependencies
        console.print("\n[bold]Dependencies:[/bold]")
        required_packages = ["httpx", "playwright", "pydantic", "fire", "rich", "loguru", "beautifulsoup4"]
        import importlib

        for package in required_packages:
            try:
                importlib.import_module(package)
                console.print(f"[green]✓ {package}[/green]")
            except ImportError:
                console.print(f"[red]✗ {package} not installed[/red]")
                console.print(f"  Solution: pip install {package}")
                issues_found += 1

        # Check PlaywrightAuthor
        import importlib.util

        if importlib.util.find_spec("playwrightauthor") is not None:
            console.print("[green]✓ playwrightauthor[/green]")
        else:
            console.print("[red]✗ playwrightauthor not installed[/red]")
            console.print("  Solution: Check pyproject.toml dependencies")
            issues_found += 1

        # Check data file
        console.print("\n[bold]Data File:[/bold]")
        if DATA_FILE_PATH.exists():
            size = DATA_FILE_PATH.stat().st_size
            console.print(f"[green]✓ Model data exists ({size:,} bytes)[/green]")

            # Check if data is valid JSON
            try:
                import json

                with open(DATA_FILE_PATH) as f:
                    data = json.load(f)
                console.print(f"[green]✓ Valid JSON with {len(data.get('models', []))} models[/green]")
            except Exception as e:
                console.print(f"[red]✗ Invalid JSON: {e}[/red]")
                console.print("  Solution: Run 'virginia-clemm-poe update --force'")
                issues_found += 1
        else:
            console.print("[yellow]⚠ No model data found[/yellow]")
            console.print("  Solution: Run 'virginia-clemm-poe update'")

        # Summary
        console.print("\n" + "=" * 50)
        if issues_found == 0:
            console.print("[green]✓ All checks passed! Virginia Clemm Poe is ready to use.[/green]")
        else:
            console.print(f"[red]Found {issues_found} issue(s). Please fix them and try again.[/red]")
            console.print("\nQuick setup commands:")
            console.print("  1. export POE_API_KEY=your_api_key")
            console.print("  2. virginia-clemm-poe setup")
            console.print("  3. virginia-clemm-poe update")

    def update(
        self,
        info: bool = False,
        pricing: bool = False,
        all: bool = True,
        api_key: str | None = None,
        force: bool = False,
        debug_port: int = 9222,
        verbose: bool = False,
    ):
        """Update Poe model data with pricing and bot information from web scraping.

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
            debug_port: Chrome DevTools Protocol port (default: 9222). Change if port
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
        # Configure logger first
        configure_logger(verbose)
        
        # Log user action with context
        log_user_action(
            "update", 
            command=f"update --info={info} --pricing={pricing} --all={all} --force={force}",
            info=info,
            pricing=pricing,
            all=all,
            force=force,
            verbose=verbose
        )

        # Get API key
        api_key = api_key or os.environ.get("POE_API_KEY")
        if not api_key:
            console.print("[red]Error: POE_API_KEY not set[/red]")
            console.print("Set it with: export POE_API_KEY=your_api_key")
            console.print("Or pass it as: --api_key your_api_key")
            sys.exit(1)

        # Determine what to update
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
            return

        # Show what will be updated
        if all:
            console.print("[green]Updating all data (bot info + pricing)...[/green]")
        else:
            updates = []
            if update_info:
                updates.append("bot info")
            if update_pricing:
                updates.append("pricing")
            console.print(f"[green]Updating {' and '.join(updates)}...[/green]")

        # Run update
        async def run_update():
            updater = ModelUpdater(api_key, debug_port=debug_port, verbose=verbose)
            await updater.update_all(force=force, update_info=update_info, update_pricing=update_pricing)

        asyncio.run(run_update())

    def search(self, query: str, show_pricing: bool = True, show_bot_info: bool = False, verbose: bool = False):
        """Search and display Poe models by ID or name with flexible filtering.

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
            verbose=verbose
        )

        if not DATA_FILE_PATH.exists():
            console.print("[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]")
            return

        with log_operation("model_search", {"query": query}) as ctx:
            models = api.search_models(query)
            ctx["results_count"] = len(models)

        if not models:
            console.print(f"[yellow]No models found matching '{query}'[/yellow]")
            return

        # Create table
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

        for model in models:
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
                if model.pricing:
                    primary_cost = model.get_primary_cost()
                    pricing_info = primary_cost if primary_cost else "[dim]No cost info[/dim]"

                    # Include initial points cost if available
                    if model.pricing.details.initial_points_cost:
                        pricing_info = f"{model.pricing.details.initial_points_cost} | {pricing_info}"

                    updated = model.pricing.checked_at.strftime("%Y-%m-%d")
                    row.extend([pricing_info, updated])
                elif model.pricing_error:
                    row.extend([f"[red]Error: {model.pricing_error}[/red]", "-"])
                else:
                    row.extend(["[dim]Not checked[/dim]", "-"])

            table.add_row(*[str(x) for x in row])

        console.print(table)
        console.print(f"\n[green]Found {len(models)} models[/green]")

        # Show detailed bot info if requested and only one model found
        if show_bot_info and len(models) == 1 and models[0].bot_info:
            bot_info = models[0].bot_info
            console.print("\n[bold]Bot Information:[/bold]")
            if bot_info.description:
                console.print(f"[blue]Description:[/blue] {bot_info.description}")
            if bot_info.description_extra:
                console.print(f"[dim]Details:[/dim] {bot_info.description_extra}")

    def list(self, with_pricing: bool = False, limit: int | None = None, verbose: bool = False):
        """List all available models.

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
        with_pricing = len([m for m in all_models if m.has_pricing()])
        need_update = len([m for m in all_models if m.needs_pricing_update()])

        table.add_row(str(len(all_models)), str(with_pricing), str(need_update))
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
