#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["loguru"]
# ///
# this_file: src_docs/update_docs.py

"""Update documentation by parsing poe_models.json and generating static pages."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from loguru import logger


def load_models_data(json_path: Path) -> dict[str, Any]:
    """Load the poe_models.json data."""
    logger.info(f"Loading models data from: {json_path}")
    if not json_path.exists():
        logger.error(f"Models data file not found: {json_path}")
        raise FileNotFoundError(f"Models data file not found: {json_path}")

    try:
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)
        logger.success(f"Successfully loaded {len(data.get('data', []))} models from {json_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {json_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading {json_path}: {e}")
        raise


def generate_model_page(model: dict[str, Any]) -> str:
    """Generate markdown content for a single model page."""
    logger.debug(f"Generating page for model: {model['id']}")
    content = []

    # Title and basic info
    content.append(f"# [{model['id']}](https://poe.com/{model['id']}){{ .md-button .md-button--primary }}\n")

    # Pricing section
    if pricing := model.get("pricing"):
        content.append("## Pricing\n")
        if details := pricing.get("details"):
            content.append("| Type | Cost |")
            content.append("|------|------|")
            for key, value in details.items():
                if value:
                    formatted_key = key.replace("_", " ").title()
                    content.append(f"| {formatted_key} | {value} |")
        content.append(f"\n**Last Checked:** {pricing.get('checked_at', 'N/A')}\n")
        content.append("")

    # Bot info section
    if bot_info := model.get("bot_info"):
        content.append("## Bot Information\n")
        content.append(f"**Creator:** {bot_info.get('creator', 'N/A')}\n")
        content.append(f"**Description:** {bot_info.get('description', 'N/A')}\n")
        if extra := bot_info.get("description_extra"):
            content.append(f"**Extra:** {extra}\n")
        content.append("")

    # Architecture section
    if arch := model.get("architecture"):
        content.append("## Architecture\n")
        content.append(f"**Input Modalities:** {', '.join(arch.get('input_modalities', []))}\n")
        content.append(f"**Output Modalities:** {', '.join(arch.get('output_modalities', []))}\n")
        content.append(f"**Modality:** {arch.get('modality', 'N/A')}\n")
        content.append("")

    # Technical details
    content.append("## Technical Details\n")
    content.append(f"**Model ID:** `{model['id']}`\n")
    content.append(f"**Object Type:** {model.get('object', 'N/A')}\n")
    content.append(f"**Created:** {model.get('created', 'N/A')}\n")
    content.append(f"**Owned By:** {model.get('owned_by', 'N/A')}\n")
    content.append(f"**Root:** {model.get('root', 'N/A')}\n")

    return "\n".join(content)


def main() -> None:
    """Main function to update documentation."""
    logger.info("🚀 Starting documentation update process")

    # Define paths
    project_root = Path(__file__).parent.parent
    src_models_json = project_root / "src" / "virginia_clemm_poe" / "data" / "poe_models.json"
    docs_md_dir = project_root / "src_docs" / "md"
    docs_data_dir = docs_md_dir / "data"
    docs_models_dir = docs_md_dir / "models"

    logger.info(f"Project root: {project_root}")
    logger.info(f"Source JSON: {src_models_json}")
    logger.info(f"Docs output directory: {docs_md_dir}")

    # Create directories
    logger.info("📁 Creating output directories")
    docs_data_dir.mkdir(parents=True, exist_ok=True)
    docs_models_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created: {docs_data_dir}")
    logger.debug(f"Created: {docs_models_dir}")

    # Load models data
    data = load_models_data(src_models_json)

    # Copy JSON to docs data directory
    logger.info("📋 Copying JSON data to docs directory")
    dest_json = docs_data_dir / "poe_models.json"
    shutil.copy2(src_models_json, dest_json)
    logger.success(f"Copied JSON data to: {dest_json}")

    # Generate individual model pages
    models = data.get("data", [])
    logger.info(f"📄 Generating {len(models)} individual model pages")

    for i, model in enumerate(models, 1):
        model_id = model["id"]
        safe_filename = f"{model_id}.md"
        model_path = docs_models_dir / safe_filename

        content = generate_model_page(model)
        model_path.write_text(content)

        if i % 50 == 0 or i == len(models):
            logger.info(f"Progress: {i}/{len(models)} model pages generated")

    logger.success(f"✅ Generated {len(models)} model pages in: {docs_models_dir}")

    # Copy the static table HTML file (no generation needed)
    logger.info("📋 Copying static table HTML and data")
    src_table_html = docs_md_dir / "table.html"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    dest_table_html = docs_dir / "table.html"

    # Check if source table.html exists
    if src_table_html.exists():
        shutil.copy2(src_table_html, dest_table_html)
        logger.success(f"Copied table.html from {src_table_html} to {dest_table_html}")
    else:
        logger.warning(f"Source table.html not found at {src_table_html}, skipping copy")

    # Also copy the data directory to docs/data for the table to access
    docs_data_dest = docs_dir / "data"
    docs_data_dest.mkdir(parents=True, exist_ok=True)
    dest_json = docs_data_dest / "poe_models.json"
    shutil.copy2(docs_data_dir / "poe_models.json", dest_json)
    logger.success(f"Copied poe_models.json to: {dest_json}")

    # Generate models index page
    logger.info("📑 Generating models index page")
    models_index_path = docs_models_dir / "index.md"
    models_index_content = ["# Models Database\n\n"]
    models_index_content.append("## Interactive Table\n\n")
    models_index_content.append(
        '<iframe src="../table.html" width="100%" height="800px" frameborder="0" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>\n\n'
    )
    models_index_content.append("## All Models\n\n")
    models_index_content.append("Browse all available Poe models:\n\n")

    for model in sorted(models, key=lambda x: x["id"]):
        models_index_content.append(f"### [{model['id']}]({model['id']}.md)")
        models_index_content.append("\n\n")

    models_index_path.write_text("".join(models_index_content))
    logger.success(f"Generated models index: {models_index_path}")

    # Build the MkDocs site
    logger.info("🔨 Building MkDocs site")
    src_docs_dir = project_root / "src_docs"

    try:
        # Change to src_docs directory and run mkdocs build
        result = subprocess.run(["mkdocs", "build"], cwd=src_docs_dir, capture_output=True, text=True, check=True)
        logger.success("✅ MkDocs site built successfully")
        if result.stdout:
            logger.debug(f"MkDocs output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build MkDocs site: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        if e.stdout:
            logger.debug(f"Standard output: {e.stdout}")
        raise
    except FileNotFoundError:
        logger.warning("mkdocs command not found. Please install mkdocs to build the site automatically.")
        logger.info("You can install it with: pip install mkdocs mkdocs-material")

    logger.success("🎉 Documentation update and build completed successfully!")


def setup_logging(verbose: bool = False) -> None:
    """Configure loguru logging with appropriate level and format."""
    logger.remove()  # Remove default handler

    # Configure format based on verbose mode
    if verbose:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        level = "DEBUG"
    else:
        format_string = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        level = "INFO"

    logger.add(sys.stderr, format=format_string, level=level, colorize=True, backtrace=True, diagnose=True)


if __name__ == "__main__":
    # Simple argument parsing for verbose mode
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Setup logging
    setup_logging(verbose)

    try:
        main()
    except Exception as e:
        logger.error(f"❌ Documentation update failed: {e}")
        if verbose:
            logger.exception("Full error traceback:")
        sys.exit(1)
