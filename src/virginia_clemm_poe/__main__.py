# this_file: src/virginia_clemm_poe/__main__.py

"""CLI entry point for Virginia Clemm Poe."""

import asyncio
import os
import subprocess
import sys

import fire
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from . import api
from .browser import BrowserManager
from .config import DATA_FILE_PATH
from .updater import ModelUpdater

console = Console()


class CLI:
    """Virginia Clemm Poe - Poe.com model data management CLI."""
    
    def setup(self):
        """Set up browser for web scraping (installs Chrome for Testing)."""
        rprint("[bold blue]Setting up browser for Virginia Clemm Poe...[/bold blue]")
        
        # Check if Chrome is already available
        chrome_path = BrowserManager.find_chrome_path()
        if chrome_path:
            rprint(f"[green]✓ Chrome found at: {chrome_path}[/green]")
            rprint("\n[bold]You're all set![/bold]")
            rprint("\nTo get started:")
            rprint("1. Set your Poe API key: [cyan]export POE_API_KEY=your_key[/cyan]")
            rprint("2. Update model data: [cyan]virginia-clemm-poe update --pricing[/cyan]")
            rprint("3. Search models: [cyan]virginia-clemm-poe search claude[/cyan]")
            return
        
        rprint("[yellow]Chrome not found. Installing Chrome for Testing...[/yellow]")
        
        try:
            # Install playwright browsers
            subprocess.run(["playwright", "install", "chromium"], check=True)
            rprint("[green]✓ Successfully installed Chrome for Testing[/green]")
            
            rprint("\n[bold]Setup complete![/bold]")
            rprint("\nTo get started:")
            rprint("1. Set your Poe API key: [cyan]export POE_API_KEY=your_key[/cyan]")
            rprint("2. Update model data: [cyan]virginia-clemm-poe update --pricing[/cyan]")
            rprint("3. Search models: [cyan]virginia-clemm-poe search claude[/cyan]")
            
        except subprocess.CalledProcessError as e:
            rprint(f"[red]✗ Failed to install browser: {e}[/red]")
            rprint("\nPlease install Chrome or Chromium manually:")
            rprint("- macOS: brew install --cask google-chrome")
            rprint("- Ubuntu: sudo apt-get install google-chrome-stable")
            rprint("- Windows: Download from https://www.google.com/chrome/")
            sys.exit(1)
    
    def update(
        self,
        info: bool = False,
        pricing: bool = False,
        all: bool = True,
        api_key: str | None = None,
        force: bool = False,
        debug_port: int = 9222,
        verbose: bool = False
    ):
        """Update model data.
        
        Args:
            info: Update only bot info (creator, description)
            pricing: Update only pricing information
            all: Update both info and pricing (default: True)
            api_key: Override POE_API_KEY environment variable
            force: Force update even if data exists
            debug_port: Chrome debug port (default: 9222)
            verbose: Enable verbose logging
        """
        # Get API key
        api_key = api_key or os.environ.get("POE_API_KEY")
        if not api_key:
            rprint("[red]Error: POE_API_KEY not set[/red]")
            rprint("Set it with: export POE_API_KEY=your_api_key")
            rprint("Or pass it as: --api_key your_api_key")
            sys.exit(1)
        
        # Determine what to update
        # If user explicitly sets --info or --pricing, disable --all
        if info or pricing:
            all = False
        
        update_info = info or all
        update_pricing = pricing or all
        
        if not update_info and not update_pricing:
            rprint("[yellow]No update mode selected.[/yellow]")
            rprint("Available options:")
            rprint("  --info     Update bot info (creator, description)")
            rprint("  --pricing  Update pricing information")
            rprint("  --all      Update both (default)")
            return
        
        # Show what will be updated
        if all:
            rprint("[green]Updating all data (bot info + pricing)...[/green]")
        else:
            updates = []
            if update_info:
                updates.append("bot info")
            if update_pricing:
                updates.append("pricing")
            rprint(f"[green]Updating {' and '.join(updates)}...[/green]")
        
        # Run update
        async def run_update():
            updater = ModelUpdater(api_key, debug_port=debug_port, verbose=verbose)
            await updater.update_all(
                force=force, 
                update_info=update_info,
                update_pricing=update_pricing
            )
        
        asyncio.run(run_update())
    
    def search(self, query: str, show_pricing: bool = True, show_bot_info: bool = False):
        """Search for models by ID or name.
        
        Args:
            query: Search query (matches ID or name)
            show_pricing: Show pricing information if available
            show_bot_info: Show bot info (creator, description)
        """
        if not DATA_FILE_PATH.exists():
            rprint("[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]")
            return
        
        models = api.search_models(query)
        
        if not models:
            rprint(f"[yellow]No models found matching '{query}'[/yellow]")
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
        rprint(f"\n[green]Found {len(models)} models[/green]")
        
        # Show detailed bot info if requested and only one model found
        if show_bot_info and len(models) == 1 and models[0].bot_info:
            bot_info = models[0].bot_info
            rprint("\n[bold]Bot Information:[/bold]")
            if bot_info.description:
                rprint(f"[blue]Description:[/blue] {bot_info.description}")
            if bot_info.description_extra:
                rprint(f"[dim]Details:[/dim] {bot_info.description_extra}")
    
    def list(self, with_pricing: bool = False, limit: int | None = None):
        """List all available models.
        
        Args:
            with_pricing: Only show models with pricing information
            limit: Limit number of results
        """
        if not DATA_FILE_PATH.exists():
            rprint("[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]")
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
            rprint(f"\n[bold]Showing {len(models)} models:[/bold]")
            for model in models:
                status = "✓" if model.has_pricing() else "✗"
                rprint(f"{status} {model.id}")


def main():
    """Main CLI entry point."""
    fire.Fire(CLI)


if __name__ == "__main__":
    main()