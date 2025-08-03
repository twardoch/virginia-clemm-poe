# this_file: src/virginia_clemm_poe/__main__.py

"""CLI entry point for Virginia Clemm Poe."""

import asyncio
import os
import subprocess
import sys
from typing import Optional

import fire
from loguru import logger
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
        pricing: bool = False,
        all: bool = False,
        api_key: Optional[str] = None,
        force: bool = False,
        debug_port: int = 9222,
        verbose: bool = False
    ):
        """Update model data.
        
        Args:
            pricing: Update pricing information (requires web scraping)
            all: Update all data (equivalent to --pricing)
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
        update_pricing = pricing or all
        
        if not update_pricing:
            rprint("[yellow]No update mode specified. Use --pricing or --all[/yellow]")
            rprint("Available options:")
            rprint("  --pricing  Update pricing information (web scraping)")
            rprint("  --all      Update all data")
            return
        
        # Run update
        async def run_update():
            updater = ModelUpdater(api_key, debug_port=debug_port, verbose=verbose)
            await updater.update_all(force=force)
        
        asyncio.run(run_update())
    
    def search(self, query: str, show_pricing: bool = True):
        """Search for models by ID or name.
        
        Args:
            query: Search query (matches ID or name)
            show_pricing: Show pricing information if available
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
            
            if show_pricing:
                if model.pricing:
                    primary_cost = model.get_primary_cost()
                    pricing_info = primary_cost if primary_cost else "[dim]No cost info[/dim]"
                    updated = model.pricing.checked_at.strftime("%Y-%m-%d")
                    row.extend([pricing_info, updated])
                elif model.pricing_error:
                    row.extend([f"[red]Error: {model.pricing_error}[/red]", "-"])
                else:
                    row.extend(["[dim]Not checked[/dim]", "-"])
            
            table.add_row(*[str(x) for x in row])
        
        console.print(table)
        rprint(f"\n[green]Found {len(models)} models[/green]")
    
    def list(self, with_pricing: bool = False, limit: Optional[int] = None):
        """List all available models.
        
        Args:
            with_pricing: Only show models with pricing information
            limit: Limit number of results
        """
        if not DATA_FILE_PATH.exists():
            rprint("[yellow]No model data found. Run 'virginia-clemm-poe update' first.[/yellow]")
            return
        
        if with_pricing:
            models = api.get_models_with_pricing()
        else:
            models = api.get_all_models()
        
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