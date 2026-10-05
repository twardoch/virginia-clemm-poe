#!/usr/bin/env -S uv run python
# this_file: src_docs/update_docs.py

"""Build the catalogue from saved poe_bots.json observations without rescraping."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from virginia_clemm_poe.pricing import parse_price_text, parse_rate_card


def load_bots_data(json_path: Path) -> dict[str, Any]:
    """Load the saved poe_bots.json data."""
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
    content = [f"---\nthis_file: src_docs/md/models/{model['id']}.md\n---\n"]

    # Title and basic info
    content.append(f"# [{model['id']}](https://poe.com/{model['id']}){{ .md-button .md-button--primary }}\n")

    if reference := model.get("point_estimate"):
        content.append(f"**Tier {model['pricing_tier']}:** {reference['label']} · {reference['basis']}\n")
        if conversion := reference.get("conversion"):
            content.append(
                f"Dollar conversion: ≈ {conversion['pointsPerDollar']:,.0f} points/$ ({conversion['source']}).\n"
            )
        content.append("[Comparison method and assumptions](../pricing-method.md).\n")

    # Pricing section
    if pricing := model.get("pricing"):
        content.append("## Pricing\n")

        # API pricing (dollar-based)
        if api_pricing := pricing.get("api"):
            content.append("### API Pricing (USD)\n")
            content.append("| Type | Cost |")
            content.append("|------|------|")
            if (prompt := api_pricing.get("prompt")) is not None:
                content.append(f"| Prompt | ${prompt}/token |")
            if (completion := api_pricing.get("completion")) is not None:
                content.append(f"| Completion | ${completion}/token |")
            if (image := api_pricing.get("image")) is not None:
                content.append(f"| Image | ${image}/image |")
            if (request := api_pricing.get("request")) is not None:
                content.append(f"| Request | ${request}/request |")
            content.append("")

        # Scraped pricing (points-based)
        if scraped := pricing.get("scraped"):
            content.append("### Website Pricing\n")
            if details := scraped.get("details"):
                content.append("| Type | Cost |")
                content.append("|------|------|")
                for key, value in details.items():
                    if value and key not in {"rates", "rate_card"}:
                        formatted_key = key.replace("_", " ").title()
                        display = " · ".join(value) if isinstance(value, list) else str(value)
                        content.append(f"| {formatted_key} | {display.replace('|', '&#124;')} |")
                if rates := details.get("rates"):
                    content.extend(
                        [
                            "",
                            "All parsed rates (both currencies):",
                            "",
                            "| Service | Currency | Amount | Per |",
                            "|---|---|---|---|",
                        ]
                    )
                    for rate in rates:
                        amount = ("From " if rate.get("lower_bound") else "") + str(rate["amount"])
                        content.append(
                            f"| {rate['label']} | {rate['currency'].upper()} | {amount} | {rate['quantity']} {rate['unit']} |"
                        )
            content.append(f"\n**Last Checked:** {scraped.get('checked_at', 'N/A')}\n")
            content.append("")

        # Legacy format support
        if details := pricing.get("details"):
            content.append("### Pricing Details\n")
            content.append("| Type | Cost |")
            content.append("|------|------|")
            for key, value in details.items():
                if value:
                    formatted_key = key.replace("_", " ").title()
                    content.append(f"| {formatted_key} | {value} |")
            if checked_at := pricing.get("checked_at"):
                content.append(f"\n**Last Checked:** {checked_at}\n")
            content.append("")

    # Bot info section
    if bot_info := model.get("bot_info"):
        content.append("## Bot Information\n")
        content.append(f"**Creator:** {bot_info.get('creator', 'N/A')}\n")
        description = (bot_info.get("description") or "Unknown").replace("[", r"\[").replace("]", r"\]")
        content.append(f"**Description:** {description}\n")
        if extra := bot_info.get("description_extra"):
            content.append(f"**Extra:** {extra}\n")
        content.append("")

    # Architecture section
    if arch := model.get("architecture"):
        content.append("## Architecture\n")
        content.append(f"**Input Modalities:** {', '.join(arch.get('input_modalities', [])) or 'Unknown'}\n")
        content.append(f"**Output Modalities:** {', '.join(arch.get('output_modalities', [])) or 'Unknown'}\n")
        content.append(f"**Modality:** {arch.get('modality', 'N/A')}\n")
        content.append("")

    # Technical details
    content.append("## Technical Details\n")
    content.append(f"**Model ID:** `{model['id']}`\n")
    content.append(f"**Object Type:** {model.get('object', 'N/A')}\n")
    content.append(f"**Created:** {model.get('created') if model.get('created') is not None else 'Unknown'}\n")
    content.append(f"**Owned By:** {model.get('owned_by', 'N/A')}\n")
    content.append(f"**Root:** {model.get('root', 'N/A')}\n")
    content.append(f"**API Last Updated:** {model.get('api_last_updated') or 'Not listed in API'}\n")

    return "\n".join(content)


def normalize_saved_rates(model: dict[str, Any]) -> None:
    """Reparse saved observations locally; never contact Poe during a docs build."""
    details = ((model.get("pricing") or {}).get("scraped") or {}).get("details", {})
    existing = details.get("rates", [])
    parsed = parse_rate_card(details.get("rate_card", "")).get("rates", [])
    if parsed and len(parsed) >= len(existing):
        details["rates"] = parsed
        return
    repaired = []
    for rate in existing:
        candidates = parse_price_text(rate["label"], rate.get("raw", ""), rate.get("source", "table"))
        replacement = next((r for r in candidates if r.currency == rate["currency"]), None)
        # Explicit matrix/table units are stronger than a raw string's inferred unit.
        if replacement and replacement.unit == rate["unit"]:
            rate = rate | {"amount": str(replacement.amount), "quantity": str(replacement.quantity)}
        repaired.append(rate)
    if repaired:
        details["rates"] = repaired


def add_reference_prices(models: list[dict[str, Any]], script: Path) -> dict[str, Any]:
    """Use the browser's comparison implementation for every static model page."""
    program = """const prices = require(process.argv[1]);
const models = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const conversion = prices.configure(models);
console.log(JSON.stringify({conversion, rows: models.map(m => ({id: m.id, point_estimate: prices.cost(m), pricing_tier: prices.tier(m)}))}));
"""
    result = subprocess.run(
        ["node", "-e", program, str(script)], input=json.dumps(models), text=True, capture_output=True, check=True
    )
    references = json.loads(result.stdout)
    for model, reference in zip(models, references["rows"], strict=True):
        model.update(reference)
    return references["conversion"]


def add_saved_modalities(model: dict[str, Any]) -> None:
    """Include explicit media outputs in saved rate cards in the filter metadata."""
    details = ((model.get("pricing") or {}).get("scraped") or {}).get("details", {})
    rates = details.get("rates", [])
    outputs = set((model.get("architecture") or {}).get("output_modalities", []))
    for rate in rates:
        label = rate["label"].lower()
        if "input" in label and "output" not in label:
            continue
        if rate["unit"] == "video" or "video" in label:
            outputs.add("video")
        if rate["unit"] in {"image", "megapixel"} or "image" in label:
            outputs.add("image")
        if label.startswith("audio output"):
            outputs.add("audio")
    if rates and "video generation" in details.get("rate_card", "").lower():
        outputs.add("video")
    if outputs:
        architecture = model.setdefault("architecture", {})
        if outputs != set(architecture.get("output_modalities", [])):
            architecture["output_modalities"] = sorted(outputs)
            architecture["modality"] = (
                "+".join(architecture.get("input_modalities", []) or ["unknown"]) + "->" + "+".join(sorted(outputs))
            )
            model["comparison_modalities_source"] = "saved_rate_card"


def main() -> None:
    """Main function to update documentation."""
    logger.info("🚀 Starting documentation update process")

    # Define paths
    project_root = Path(__file__).parent.parent
    src_models_json = project_root / "src" / "virginia_clemm_poe" / "data" / "poe_bots.json"
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
    data = load_bots_data(src_models_json)
    models = data.get("data", [])
    for model in models:
        normalize_saved_rates(model)
        add_saved_modalities(model)
    data["point_conversion"] = add_reference_prices(models, docs_md_dir / "price_compare.js")

    # Copy JSON to docs data directory
    logger.info("📋 Copying JSON data to docs directory")
    dest_json = docs_data_dir / "poe_bots.json"
    dest_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logger.success(f"Copied JSON data to: {dest_json}")

    # Generate individual model pages
    models = data.get("data", [])
    logger.info(f"📄 Generating {len(models)} individual model pages")

    expected_names = {f"{model['id']}.md" for model in models} | {"index.md"}
    for old_page in docs_models_dir.glob("*.md"):
        if old_page.name not in expected_names:
            old_page.unlink()  # Remove stale/case-mismatched generated pages before writing.

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
    dest_json = docs_data_dest / "poe_bots.json"
    shutil.copy2(docs_data_dir / "poe_bots.json", dest_json)
    logger.success(f"Copied poe_bots.json to: {dest_json}")

    # Generate models index page
    logger.info("📑 Generating models index page")
    models_index_path = docs_models_dir / "index.md"
    models_index_content = ["---\nthis_file: src_docs/md/models/index.md\nhide:\n  - toc\n---\n\n# Models Database\n\n"]
    models_index_content.append(
        '<iframe class="poe-catalogue" src="../table.html" title="Poe model prices and filters" loading="eager"></iframe>\n\n'
    )
    models_index_content.append('Browse model details:\n\n<ul class="poe-model-links">\n')

    for model in sorted(models, key=lambda x: x["id"]):
        models_index_content.append(f'<li><a href="{model["id"]}.html">{model["id"]}</a></li>\n')

    models_index_content.append("</ul>\n")

    models_index_path.write_text("".join(models_index_content))
    logger.success(f"Generated models index: {models_index_path}")

    # Build the MkDocs site
    logger.info("🔨 Building MkDocs site")
    src_docs_dir = project_root / "src_docs"

    try:
        # Change to src_docs directory and run mkdocs build
        result = subprocess.run(
            ["mkdocs", "build", "--clean", "--strict"], cwd=src_docs_dir, capture_output=True, text=True, check=True
        )
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
        logger.info("Install the locked documentation environment with: uv sync --locked")

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
