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
    content.append(f"# {model['id']}\n")

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

    # Technical details
    content.append("## Technical Details\n")
    content.append(f"**Model ID:** `{model['id']}`\n")
    content.append(f"**Object Type:** {model.get('object', 'N/A')}\n")
    content.append(f"**Created:** {model.get('created', 'N/A')}\n")
    content.append(f"**Owned By:** {model.get('owned_by', 'N/A')}\n")
    content.append(f"**Root:** {model.get('root', 'N/A')}\n")

    return "\n".join(content)


def generate_table_html() -> str:
    """Generate HTML page with dynamic table for models."""
    logger.info("Generating interactive table HTML")
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poe Models Interactive Table</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .controls {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        input, select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        input[type="text"] {
            flex: 1;
            min-width: 200px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            cursor: pointer;
            user-select: none;
        }
        th:hover {
            background: #e9ecef;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .model-link {
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }
        .model-link:hover {
            text-decoration: underline;
        }
        .modality {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            background: #e3f2fd;
            color: #1976d2;
        }
        .price {
            font-weight: 500;
            color: #2e7d32;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            color: #d32f2f;
            padding: 20px;
            text-align: center;
        }
        .sort-arrow {
            display: inline-block;
            margin-left: 5px;
            opacity: 0.5;
        }
        .sort-arrow.active {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Poe Models Database</h1>

        <div class="controls">
            <input type="text" id="searchInput" placeholder="Search models...">
            <select id="modalityFilter">
                <option value="">All Modalities</option>
                <option value="text->text">Text → Text</option>
                <option value="text->image">Text → Image</option>
                <option value="text->audio">Text → Audio</option>
                <option value="text->video">Text → Video</option>
            </select>
            <select id="ownerFilter">
                <option value="">All Owners</option>
            </select>
        </div>

        <div id="tableContainer">
            <div class="loading">Loading models data...</div>
        </div>
    </div>

    <script>
        let modelsData = [];
        let filteredData = [];
        let sortColumn = 'id';
        let sortDirection = 'asc';

        async function loadData() {
            try {
                const response = await fetch('data/poe_models.json');
                const data = await response.json();
                modelsData = data.data || [];
                initializeFilters();
                renderTable();
            } catch (error) {
                document.getElementById('tableContainer').innerHTML =
                    '<div class="error">Error loading models data: ' + error.message + '</div>';
            }
        }

        function initializeFilters() {
            const owners = [...new Set(modelsData.map(m => m.owned_by))].sort();
            const ownerFilter = document.getElementById('ownerFilter');
            owners.forEach(owner => {
                const option = document.createElement('option');
                option.value = owner;
                option.textContent = owner;
                ownerFilter.appendChild(option);
            });
        }

        function getInitialCost(model) {
            if (model.pricing?.details?.initial_points_cost) {
                return model.pricing.details.initial_points_cost;
            }
            return 'N/A';
        }

        function filterData() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const modalityFilter = document.getElementById('modalityFilter').value;
            const ownerFilter = document.getElementById('ownerFilter').value;

            filteredData = modelsData.filter(model => {
                const matchesSearch = !searchTerm ||
                    model.id.toLowerCase().includes(searchTerm) ||
                    (model.bot_info?.description || '').toLowerCase().includes(searchTerm) ||
                    (model.bot_info?.creator || '').toLowerCase().includes(searchTerm);

                const matchesModality = !modalityFilter ||
                    model.architecture?.modality === modalityFilter;

                const matchesOwner = !ownerFilter ||
                    model.owned_by === ownerFilter;

                return matchesSearch && matchesModality && matchesOwner;
            });

            sortData();
        }

        function sortData() {
            filteredData.sort((a, b) => {
                let aVal = a[sortColumn];
                let bVal = b[sortColumn];

                if (sortColumn === 'modality') {
                    aVal = a.architecture?.modality || '';
                    bVal = b.architecture?.modality || '';
                } else if (sortColumn === 'creator') {
                    aVal = a.bot_info?.creator || '';
                    bVal = b.bot_info?.creator || '';
                } else if (sortColumn === 'cost') {
                    aVal = getInitialCost(a);
                    bVal = getInitialCost(b);
                    // Extract numeric value for sorting
                    const aNum = parseInt(aVal.replace(/[^0-9]/g, '')) || 999999;
                    const bNum = parseInt(bVal.replace(/[^0-9]/g, '')) || 999999;
                    aVal = aNum;
                    bVal = bNum;
                }

                if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
                return 0;
            });

            renderTable();
        }

        function handleSort(column) {
            if (sortColumn === column) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortDirection = 'asc';
            }
            sortData();
        }

        function renderTable() {
            const html = `
                <table>
                    <thead>
                        <tr>
                            <th onclick="handleSort('id')">
                                Model ID
                                <span class="sort-arrow ${sortColumn === 'id' ? 'active' : ''}">
                                    ${sortColumn === 'id' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'}
                                </span>
                            </th>
                            <th onclick="handleSort('modality')">
                                Modality
                                <span class="sort-arrow ${sortColumn === 'modality' ? 'active' : ''}">
                                    ${sortColumn === 'modality' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'}
                                </span>
                            </th>
                            <th onclick="handleSort('creator')">
                                Creator
                                <span class="sort-arrow ${sortColumn === 'creator' ? 'active' : ''}">
                                    ${sortColumn === 'creator' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'}
                                </span>
                            </th>
                            <th onclick="handleSort('cost')">
                                Initial Cost
                                <span class="sort-arrow ${sortColumn === 'cost' ? 'active' : ''}">
                                    ${sortColumn === 'cost' ? (sortDirection === 'asc' ? '↑' : '↓') : '↕'}
                                </span>
                            </th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredData.map(model => `
                            <tr>
                                <td><a href="models/${model.id}.html" class="model-link">${model.id}</a></td>
                                <td><span class="modality">${model.architecture?.modality || 'N/A'}</span></td>
                                <td>${model.bot_info?.creator || 'N/A'}</td>
                                <td class="price">${getInitialCost(model)}</td>
                                <td>${(model.bot_info?.description || 'N/A').substring(0, 100)}${(model.bot_info?.description || '').length > 100 ? '...' : ''}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('tableContainer').innerHTML = html;
        }

        // Event listeners
        document.getElementById('searchInput').addEventListener('input', filterData);
        document.getElementById('modalityFilter').addEventListener('change', filterData);
        document.getElementById('ownerFilter').addEventListener('change', filterData);

        // Initialize
        loadData();
    </script>
</body>
</html>
"""


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

    # Generate interactive table HTML
    logger.info("🔧 Generating interactive table HTML")
    table_html_path = docs_md_dir / "table.html"
    table_html_path.write_text(generate_table_html())
    logger.success(f"Generated interactive table: {table_html_path}")

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
        if (bot_info := model.get("bot_info")) and (creator := bot_info.get("creator")):
            models_index_content.append(f" by {creator}")
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
